import datetime
import json
import os
import requests
import timesheetbot.settings as settings

from timesheetbot.models import TimeEntry, WorkType, Program

def template_insert(entrytext, dict_replacement):
    """Simple utility to replace values in text according to replacements dict"""

    out_text = entrytext
    for one_key_replacement in dict_replacement:
        # Variables are coded in a "{@variable_name@}" fashion
        out_text = out_text.replace(
            "{@" + one_key_replacement + "@}", dict_replacement[one_key_replacement]
        )

    return out_text


def format_date(date_string):
    """Given a date in a "YYY-MM-DD_[0|1]" format, return a human readable date"""

    days_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    date_body = date_string.split("_")[0]
    date_object = datetime.date(*[int(part) for part in date_body.split("-")])

    day_name = days_names[date_object.weekday()]
    day_period = "morning" if date_string.endswith("_0") else "afternoon"

    return f"{day_name} {day_period} ({date_body})"


def build_program_options():
    """Builds a slack-compatible dict representation of known programs"""
    program_list = []
    for program in Program.objects.filter(is_active=True).order_by("slack_description"):
        program_list.append(
            {
                "text": {"type": "mrkdwn", "text": program.slack_description[:75]},
                "value": program.slack_value,
            }
        )

    return program_list


def build_work_type_options():
    """Builds a slack-compatible dict representation of known work types"""

    work_type_list = []
    for work_type in WorkType.objects.filter(is_active=True).order_by(
        "slack_description"
    ):
        work_type_list.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": work_type.slack_description[:75],
                },
                "value": work_type.slack_value,
            }
        )

    return work_type_list


def get_option_for_key(options, key):
    """Utility to retrieve the correct dict representing a pre-select options for slack"""

    for one_option in options:
        if one_option["value"] == key:
            return one_option.copy()


class QuerySender:
    """Class to handle the outgoing queires towards slack API"""

    def __init__(self):
        """Initialization: only the header is concerned"""

        self.default_header = {"Content-type": "application/json; charset=utf-8"}

    def prepare_and_send_modal(self, trigger_id, user_id, date_repr):
        """Preapare and builds the modal menu asking for informations to user"""

        # Loads the template
        with open(
            os.path.join(settings.STATIC_ROOT, "json_payloads", "modal.json"), "r"
        ) as hr:
            view_data = json.load(hr)

        # Retrieves the data for user/timeslot if it exists
        user_data_object = TimeEntry.objects.filter(
            user=user_id,
            date=datetime.date(
                *[int(part) for part in date_repr.split("_")[0].split("-")]
            ),
            is_morning=(date_repr.endswith("_0")),
        ).first()

        # Fill the template
        view_data["blocks"][2]["element"]["initial_value"] = (
            user_data_object.description if user_data_object is not None else ""
        )
        view_data["blocks"][2]["label"]["text"] = template_insert(
            view_data["blocks"][2]["label"]["text"],
            {"time_period": format_date(date_repr)},
        )
        view_data["blocks"][4]["element"]["options"] = build_work_type_options()
        view_data["blocks"][6]["accessory"]["options"] = build_program_options()

        # The headers must also include an authorization token for the views API
        final_header = self.default_header
        final_header["Authorization"] = (
            "Bearer " + settings.config["SLACK_BEARER_TOKEN"]
        )

        # Finally post the request
        requests.post(
            settings.config["SLACK_VIEW_API_URL"],
            data=json.dumps({"trigger_id": trigger_id, "view": view_data}),
            headers=final_header,
        )

    def send_simple_message(self, message, hook_url=None, user_slack_id=None):
        """Posting a simple/non-formatted message to a given channel"""

        if hook_url is not None:
            requests.post(
                hook_url,
                data=json.dumps({"text": message}),
                headers=self.default_header,
            )

        elif user_slack_id is not None:
            # The headers must also include an authorization token for the chats API
            final_header = self.default_header
            final_header["Authorization"] = (
                "Bearer " + settings.config["SLACK_BEARER_TOKEN"]
            )

            message_formatted = {"channel": user_slack_id, "text": message}

            requests.post(
                settings.config["SLACK_CHAT_API_URL"],
                data=json.dumps(message_formatted),
                headers=final_header,
            )

    def prepare_and_send_notification(self, user_object, count_missing_entries):
        """Posting a notification asking to fill missing data to user private channel"""

        # Loads the template
        with open(
            os.path.join(settings.STATIC_ROOT, "json_payloads", "notification.json"),
            "r",
        ) as hr:
            notification = json.load(hr)

        # Fill infos. that must be personalized
        data_replacement = {
            "username": user_object.first_name,
            "missing_timesheet_count": str(count_missing_entries),
            "entry_plural": ("y" if count_missing_entries < 2 else "ies"),
            "verb_plural": ("is" if count_missing_entries < 2 else "are"),
        }
        notification["blocks"][0]["text"]["text"] = template_insert(
            notification["blocks"][0]["text"]["text"], data_replacement
        )
        notification["channel"] = user_object.slack_userid

        # The headers must also include an authorization token for the chats API
        final_header = self.default_header
        final_header["Authorization"] = (
            "Bearer " + settings.config["SLACK_BEARER_TOKEN"]
        )

        # And post
        requests.post(
            settings.config["SLACK_CHAT_API_URL"],
            data=json.dumps(notification),
            headers=final_header,
        )
