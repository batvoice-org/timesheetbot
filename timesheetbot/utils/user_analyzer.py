import datetime
import pytz
import timesheetbot.settings as settings

from timesheetbot.models import User, TimeEntry, WorkType, NotificationHour
from timesheetbot.utils.query_sender import QuerySender


class UserAnalyzer:
    """Class to handle User data/infos."""

    def __init__(self, uid):
        """Class initialization"""
        self.user = User.objects.filter(pk=uid).first()
        self.query_sender = QuerySender()

    def launch_modals(self, trigger_id):
        """Create a new filling-data modal if data are missing"""

        missing_data = self.find_missing_data()
        if len(missing_data):
            # Modal by default for the first missing date
            self.query_sender.prepare_and_send_modal(
                trigger_id, self.user.pk, sorted(missing_data)[0]
            )

    def find_missing_data(self):
        """Find out what entries must be filled"""

        # Relies on auxilary functions, to know what should be filled minus what's already
        return self.find_needed_data() - self.find_available_data()

    def find_needed_data(self):
        """Find out all the time slots for which informations must be filled"""

        # For efficiency, a starting date is regularly updated
        # If entries are filled up to a date, start only at that date next time
        # Also: we might expect data only up to today
        needed_data = set([])
        date_study = self.user.look_for_data_starting_at
        date_current = datetime.date.today()
        while date_study < date_current:
            # Adding morning and afternoon if not the week-end
            if date_study.weekday() < 5:
                needed_data.add(str(date_study) + "_0")
                needed_data.add(str(date_study) + "_1")
            date_study = date_study + datetime.timedelta(days=1)

        # Current day is special: depending on the time, we might expect morning and/or afternoon
        if date_current.weekday() < 5:
            if self.user.look_for_data_starting_at <= date_current:
                current_tz_hour = datetime.datetime.now(
                    tz=pytz.timezone(self.user.working_timezone)
                ).hour
                if current_tz_hour >= settings.config["MORNING_ENDS_AT"]:
                    needed_data.add(str(date_current) + "_0")
                if current_tz_hour >= settings.config["AFTERNOON_ENDS_AT"]:
                    needed_data.add(str(date_current) + "_1")

        return needed_data

    def find_available_data(self):
        """Returns all already filled timeslots for user"""

        available_data = set([])
        # We study data only starting from the reference data, for the current user
        for one_data in TimeEntry.objects.filter(
            user=self.user.pk,
            date__gte=self.user.look_for_data_starting_at,
            program__isnull=False,
            work_type__isnull=False,
        ).values("description", "date", "is_morning"):
            # A data point is not valid if
            # - no activity & not holiday
            # - no infos. on CIR, CII or work type [already filtered at query level]
            if (len(one_data["description"]) <= 2):
                continue

            # But if all that is available, data can ineed be considered as available
            postfix_day_period = "_0" if one_data["is_morning"] else "_1"
            available_data.add(str(one_data["date"]) + postfix_day_period)

        return available_data

    def register_changes(self, date_object, change_type, change_dict):
        """New infos. have been sent; let's store those new infos"""

        # Retrieve the data for user/timeslot or create if necessary
        time_entry = TimeEntry.objects.filter(
            user=self.user,
            date=date_object["date"],
            is_morning=date_object["is_morning"],
            is_afternoon=date_object["is_afternoon"],
        ).first()
        if time_entry is None:
            time_entry = TimeEntry(
                user=self.user,
                description="",
                date=date_object["date"],
                is_morning=date_object["is_morning"],
                is_afternoon=date_object["is_afternoon"],
            )
            time_entry.save()

        # Form has been sent, hence we expect new infos. about activity description
        if change_type == "submit":
            description = change_dict["description-block"]["description-action"]["value"]
            time_entry.descripiton = description.strip()

        time_entry.save()

        # We might publish that new piece of information in dedicated slack channel
        self.user_republish_information(time_entry)

    def launch_notifications(self):
        """Launch notifications inviting user to fill the missing entries"""

        # Notifications can be sent only at configured hours for current user
        current_tz_time = datetime.datetime.now(
            tz=pytz.timezone(self.user.working_timezone)
        )
        current_tz_hour = current_tz_time.hour
        user_hour_notif = NotificationHour.objects.filter(
            user=self.user.pk, timezone_hour=current_tz_hour
        ).first()
        if user_hour_notif is not None:
            # And we send notifications only if there are entries that actually must be filled
            count_missing_data = len(self.find_missing_data())
            if count_missing_data:
                # We notify only if last notification is old enough according to configuration
                if (
                    self.user.last_notified
                    + datetime.timedelta(
                        hours=self.user.min_hours_between_notifications
                    )
                ) <= current_tz_time:
                    # Skip notifications on WE if settings say so
                    if (settings.config["SKIP_NOTIFICATIONS_ON_WE"]) and (
                        current_tz_time.weekday() >= 5
                    ):
                        return
                    # Relies on dedicated class for the sending & update last notification timestamp
                    self.query_sender.prepare_and_send_notification(
                        self.user, count_missing_data
                    )
                    self.update_user_latest_notification()

    def update_user_analysis_mindate(self):
        """Updates the user starting point for missing data analysis"""

        # Look for missing entries according to current starting point
        missing_data = self.find_missing_data()
        if len(missing_data):
            # The new starting point may be the first missing point if there are some
            first_missing_date = [
                int(part) for part in sorted(missing_data)[0].split("_")[0].split("-")
            ]
            self.user.look_for_data_starting_at = datetime.date(*first_missing_date)
        else:
            # Else, we can start future analysis directly at the current day
            self.user.look_for_data_starting_at = datetime.date.today()

        self.user.save()

    def update_user_latest_notification(self):
        """Updates user last notification timestamp"""

        self.user.last_notified = datetime.datetime.now(
            tz=pytz.timezone(self.user.working_timezone)
        )
        self.user.save()

    def user_republish_information(self, time_entry: TimeEntry):
        """When a new entry is complete, publish infos. to the associated public channel if needed"""

        # Summarizes info. and send through dedicated class
        date = str(time_entry.date) + " morning" if time_entry.is_morning else " afternoon"

        text = f'*{date}* :\n- _Work type_ : {time_entry.work_type.slack_description}\n- _Program_ : {time_entry.program.slack_description}\n- _Description_ : {time_entry.description}'

        # Send to dedicated hook if exists/is valid
        if self.user.slack_republish_hook.startswith("http"):
            self.query_sender.send_simple_message(
                text, hook_url=self.user.slack_republish_hook
            )

        # Send a copy to personal channel if so configured
        if self.user.do_send_copy_of_data:
            self.query_sender.send_simple_message(
                text, user_slack_id=self.user.slack_userid
            )
