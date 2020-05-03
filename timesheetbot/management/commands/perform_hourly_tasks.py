from timesheetbot.models import User
from timesheetbot.utils.user_analyzer import UserAnalyzer
from timesheetbot.utils.google_sheet_writer import GoogleSheetWriter

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command interface class """

    help = 'Regularly performs notification/writing tasks'

    def handle(self, *args, **options):
        """ Entrypoint when launched """

        # For each user: sends notifications if needed, updates analysis startpoint if needed
        for one_user in User.objects.values('pk').all():
            user_analyzer = UserAnalyzer(one_user['pk'])
            user_analyzer.launch_notifications()
            user_analyzer.update_user_analysis_mindate()

        # Writes new data in the google sheet
        GoogleSheetWriter().write_all_new_data()
