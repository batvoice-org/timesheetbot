import datetime
import gspread
import gspread_formatting as gf
import timesheetbot.settings as settings

from timesheetbot.models import  TimeEntry
from oauth2client.service_account import ServiceAccountCredentials


def is_vacation(sheet, cellref):
    """ Checks if a cell has a non-blank background [= not worked] """

    cell_style = gf.get_effective_format(sheet, cellref).backgroundColor
    if (hasattr(cell_style, 'red') and hasattr(cell_style, 'green') and hasattr(cell_style, 'blue')):
        return ((cell_style.red < 1) or (cell_style.green < 1) or (cell_style.blue < 1))

    return True

def format_date_european_convention(entrydate):
    """ Given a date object, returns a "01-12-20"-formatted version """

    base_repr = str(entrydate).split('-')

    return base_repr[2] + '-' + base_repr[1] + '-' + base_repr[0][2:]

def get_sheet_name_from_date(entrydate):
    """ Given a date object, returns the name of the sheet that would be involved """

    first_day_of_week = entrydate - datetime.timedelta(days=entrydate.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=4)

    return format_date_european_convention(first_day_of_week) + ' => ' + format_date_european_convention(last_day_of_week)


class GoogleSheetWriter:
    """ Class to write data in relevant Google spreadsheet """

    def __init__(self):
        """ Connects client to the sheet """

        self.client = None

        # If a sheet is indeed expected to be configured
        if ((settings.config['GSPREAD_SHEET'] is not None) and (settings.config['GSPREAD_SHEET'].startswith('https://docs.google.com'))):

            # Access the sheets, and store some defaults infos.
            client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name(settings.config['GSPREAD_ACCESS_CONF_LOCATION'], ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']))
            self.client = client.open_by_url(settings.config['GSPREAD_SHEET'])
            self.format_holiday = gf.cellFormat(backgroundColor=gf.color(0, 0, 0))
            self.format_worked = gf.cellFormat(backgroundColor=gf.color(1, 1, 1))

    def write_all_new_data(self):
        """ Main entrypoint: writes all new data to the sheet """

        # Provided a sheet has been configured...
        if self.client is None:
            return

        # Arrays for which we may have to recompute the number of worked days
        written_tabs = {}
        current_sheet_name = None
        current_sheet = None

        # Loop over all the new data
        for one_data_chunk in TimeEntry.objects.filter(has_been_written_in_gsheet=False, is_cir__isnull=False, is_cii__isnull=False, work_type__isnull=False).order_by('date'):
            # Let's skip data that are not entirely filled yet
            if ((len(one_data_chunk.activities) <= 2) and (not one_data_chunk.is_holiday)):
                continue

            # Identify concerned sheet, select or create that sheet
            sheet_name = get_sheet_name_from_date(one_data_chunk.date)
            if (not (sheet_name == current_sheet_name)):
                current_sheet_name = sheet_name
                written_tabs[current_sheet_name] = set()
                try:
                    current_sheet = self.client.worksheet(current_sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    current_sheet = self.create_new_tab_from_model(current_sheet_name)

            # Current user data start at a configured row, let's fill data
            # Also: let's keep in mind that we modified a sheet for a given user
            user_start_row = one_data_chunk.user.spreadsheet_row_first_day_of_week
            written_tabs[current_sheet_name].add(user_start_row)
            current_row = user_start_row + one_data_chunk.date.weekday()
            if one_data_chunk.is_morning:
                sheet_range = 'C' + str(current_row) + ':F' + str(current_row)
            else:
                sheet_range = 'G' + str(current_row) + ':J' + str(current_row)
            if one_data_chunk.is_holiday:
                current_sheet.update(sheet_range, [['', '', '', '']])
                gf.format_cell_ranges(current_sheet, [(sheet_range, self.format_holiday)])
            else:
                current_sheet.update(sheet_range, [[one_data_chunk.activities, one_data_chunk.work_type.spreadsheet_value, (1 if one_data_chunk.is_cii else 0), (1 if one_data_chunk.is_cir else 0)]])
                gf.format_cell_ranges(current_sheet, [(sheet_range, self.format_worked)])

            # For performance/logic issues, we memorize that data have already been written
            one_data_chunk.has_been_written_in_gsheet = True
            one_data_chunk.save()

        # When data have been written, we may have to recompute the per-week worked/holidays counts
        self.update_count_worked_days(written_tabs)

    def update_count_worked_days(self, written_tabs):
        """ Given a list of modified places, recompute/checks the number of worked days for those places """

        # Loop over modified sheets, modified users
        for one_sheet_name in written_tabs:
            current_sheet = self.client.worksheet(one_sheet_name)
            for one_user_row in written_tabs[one_sheet_name]:
                # For a given week-user tab: number of worked half-days is 10 - found_holidays_in_tab
                count_worked_half_days = 10
                for current_row in range(one_user_row, one_user_row + 5):
                    if is_vacation(current_sheet, 'C' + str(current_row)):
                        count_worked_half_days -= 1
                    if is_vacation(current_sheet, 'G' + str(current_row)):
                        count_worked_half_days -= 1
                current_sheet.update('F' + str(one_user_row + 6), float(count_worked_half_days)/2)

    def create_new_tab_from_model(self, desti_name):
        """ When a needed sheet does not exist: duplicates a template at the last position to create that sheet """

        return self.client.duplicate_sheet(self.client.worksheet('TEMPLATE').id, new_sheet_name=desti_name, insert_sheet_index=len(self.client.worksheets()))
