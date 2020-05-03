import os
import timesheetbot.settings as settings

from timesheetbot.utils.slack_analyzer import SlackAnalyzer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command interface class """

    help = 'Handles a slack POST payload'

    def add_arguments(self, parser):
        parser.add_argument('--request_file', type=str, required=True, help='Full path to a json encoded request')

    def handle(self, *args, **options):
        try:
            SlackAnalyzer(options['request_file']).analyze_and_respond()
        finally:
            if not settings.config['TIMESHEET_DEBUG_MODE']:
                os.remove(options['request_file'])
