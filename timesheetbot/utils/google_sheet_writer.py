import datetime
import string
import gspread
import gspread_formatting as gf
import timesheetbot.settings as settings

from timesheetbot.models import TimeEntry
from oauth2client.service_account import ServiceAccountCredentials


def is_vacation(sheet, cellref):
    """Checks if a cell has a non-blank background [= not worked]"""

    cell_style = gf.get_effective_format(sheet, cellref).backgroundColor
    if (
        hasattr(cell_style, "red")
        and hasattr(cell_style, "green")
        and hasattr(cell_style, "blue")
    ):
        return (cell_style.red < 1) or (cell_style.green < 1) or (cell_style.blue < 1)

    return True


def format_date_for_tab_name(entrydate: datetime.date):
    return entrydate.strftime("%m-%d-%y")

def get_sheet_name_from_date(entrydate: datetime.date):
    """Given a date object, returns the name of the sheet that would be involved"""

    first_day_of_week = entrydate - datetime.timedelta(days=entrydate.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=4)

    return (
        format_date_for_tab_name(first_day_of_week)
        + " => "
        + format_date_for_tab_name(last_day_of_week)
    )


def get_column_num_from_letter(col: string):
    """Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703."""
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord("A")) + 1
    return num


def get_column_name_from_number(n):
    """Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA."""
    name = ''
    while n > 0:
        n, r = divmod (n - 1, 26)
        name = chr(r + ord('A')) + name
    return name

class GoogleSheetWriter:
    """Class to write data in relevant Google spreadsheet"""

    def __init__(self):
        """Connects client to the sheet"""

        self.client = None

        # If a sheet is indeed expected to be configured
        if (
            settings.config["GSPREAD_SHEET"] is None
            or settings.config["GSPREAD_ACCESS_CONF_LOCATION"] is None
            or not settings.config["GSPREAD_SHEET"].startswith(
                "https://docs.google.com"
            )
        ):
            raise RuntimeError(
                "GSPREAD_SHEET and GSPREAD_ACCESS_CONF_LOCATION environment variables are required"
            )

        # Access the sheets, and store some defaults infos.
        client = gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_name(
                settings.config["GSPREAD_ACCESS_CONF_LOCATION"],
                [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        )
        self.client = client.open_by_url(settings.config["GSPREAD_SHEET"])

        all_worksheet = self.client.worksheets()
        self.template_worksheet = next(
            w for w in all_worksheet if "template" in w.title.lower()
        )

    def write_all_new_data(self):
        """Main entrypoint: writes all new data to the sheet"""

        # Provided a sheet has been configured...
        if self.client is None:
            return

        # Arrays for which we may have to recompute the number of worked days
        current_sheet_name = None
        current_sheet = None

        # Loop over all the new data
        time_entries_to_write = TimeEntry.objects.filter(
            has_been_written_in_gsheet=False,
            program__isnull=False,
            work_type__isnull=False,
        ).order_by("date")

        for time_entry_to_write in time_entries_to_write:
            # Let's skip data that are not entirely filled yet
            if (len(time_entry_to_write.description) <= 2) and (
                not time_entry_to_write.is_holiday
            ):
                continue

            # Identify concerned sheet, select or create that sheet
            sheet_name = get_sheet_name_from_date(time_entry_to_write.date)
            if sheet_name != current_sheet_name:
                current_sheet_name = sheet_name
                try:
                    current_sheet = self.client.worksheet(current_sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    current_sheet = self.create_new_sheet_from_model(current_sheet_name)

            # Current user data start at a configured row, let's fill data
            # Also: let's keep in mind that we modified a sheet for a given user
            user_start_row = time_entry_to_write.user.spreadsheet_top_row
            current_row = user_start_row + 1 + time_entry_to_write.date.weekday() * 2

            if time_entry_to_write.is_afternoon:
                current_row += 1

            program_first_column_num = get_column_num_from_letter(
                settings.config["SPREADSHEET_PROGRAM_FIRST_COLUMN"]
            )
            program_latest_column_num = get_column_num_from_letter(
                settings.config["SPREADSHEET_PROGRAM_LATEST_COLUMN"]
            )
            program_column_num = get_column_num_from_letter(
                time_entry_to_write.program.spreadsheet_column_letter
            )

            sheet_range_start_column_name = get_column_name_from_number(
                program_first_column_num - 2
            )

            sheet_range = f'{sheet_range_start_column_name}{current_row}:{settings.config["SPREADSHEET_PROGRAM_LATEST_COLUMN"]}{current_row}'

            values = [
                [
                    time_entry_to_write.description,
                    time_entry_to_write.work_type.spreadsheet_value,
                ]
            ]

            for i in range(program_first_column_num, program_latest_column_num):
                if i == program_column_num:
                    values[0].append(1)
                else:
                    values[0].append("")

            current_sheet.update(
                sheet_range,
                values,
            )

            # For performance/logic issues, we memorize that data have already been written
            time_entry_to_write.has_been_written_in_gsheet = True
            time_entry_to_write.save()

    def create_new_sheet_from_model(self, new_sheet_name):
        """When a needed sheet does not exist: duplicates a template at the last position to create that sheet"""

        return self.client.duplicate_sheet(
            self.template_worksheet.id,
            new_sheet_name=new_sheet_name,
            insert_sheet_index=len(self.client.worksheets()),
        )
