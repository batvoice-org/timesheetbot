import datetime
import json
import re
import logging

from timesheetbot.models import User
from timesheetbot.utils.user_analyzer import UserAnalyzer

logger = logging.getLogger(__name__)


def parse_modal_date(date_as_text: str):
    """Parses date as displayed in modals to get a datetime object + morning/afternoon info."""

    # Morning | afternoon check
    if "morning" in date_as_text.lower():
        day_period = "morning"
    elif "afternoon" in date_as_text.lower():
        day_period = "afternoon"
    else:
        raise ValueError("morning|afternoon is not present in the string")

    # Compute date
    matches = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_as_text)
    if len(matches.groups()) == 3:
        year = int(matches[1])
        month = int(matches[2])
        day = int(matches[3])
    else:
        raise ValueError("No date found in the text.")

    date = datetime.date(year, month, day)

    return {
        "date": date,
        "is_morning": (day_period == "morning"),
        "is_afternoon": (day_period == "afternoon"),
    }


class SlackAnalyzer:
    """Parser for Slack request"""

    def __init__(self, json_path):
        """Initial loading"""

        with open(json_path, "r") as hr:
            self.request_data = json.load(hr)

    def analyze_and_respond(self):
        """Initial data parsing / routing"""

        # Elements available in all views/paring now
        self.user_analyzer = UserAnalyzer(
            User.objects.filter(slack_userid=self.request_data["user"]["id"])
            .values("pk")
            .get()["pk"]
        )
        self.triggered_uid = self.request_data["trigger_id"]

        # Either a block action or a submission
        if self.request_data["type"] == "block_actions":
            self.handle_button_clicked()
        elif self.request_data["type"] == "view_submission":
            try:
                self.handle_view_submission()
            except:
                logger.error(
                    f"Error while handling submission for {self.user_analyzer.user.first_name}."
                    + f"Incomming request body is {json.dumps(self.request_data)}"
                )
                self.user_analyzer.query_sender.send_simple_message(
                    ":warning: Something went wrong while saving your time entry...\n"
                    + "Please inform the administrator ASAP :pray:",
                    self.user_analyzer.user.slack_userid,
                )
                raise

    def handle_view_submission(self):
        """Parsing a submission request"""

        # Hence: register changes; then, launch new modal if necessary
        self.handle_data_modification("submit")
        self.user_analyzer.launch_modals(self.triggered_uid)

    def handle_button_clicked(self):
        """Parsing a block element action"""

        # Either a button => only launching modals / or select change => only registering changes
        if self.request_data["actions"][0]["type"] == "button":
            self.user_analyzer.launch_modals(self.triggered_uid)
        elif self.request_data["actions"][0]["type"] == "static_select":
            self.handle_data_modification("select")

    def handle_data_modification(self, action_type="submit"):
        """Wrapper to register modification to Users data"""

        # Parse the date and select relevant query portion
        data_concerned_date = parse_modal_date(
            self.request_data["view"]["blocks"][2]["label"]["text"]
        )
        if action_type == "submit":
            changes = self.request_data["view"]["state"]["values"]

        # Then delegate to the user class
        self.user_analyzer.register_changes(data_concerned_date, action_type, changes)
