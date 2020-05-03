from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheetbot', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """INSERT INTO timesheetbot_worktype (slack_value, slack_description, spreadsheet_value, is_active) VALUES
                ('type-formation', 'Tutorials/courses/learning?', 'formation', True),
                ('type-dev', 'Coding?', 'developpement', True),
                ('type-reunion', 'Meetings?', 'reunion', True),
                ('type-etude', 'Writing specs/battle plan/reading papers?', 'etude', True),
                ('type-operations', '(Sys)admin stuff/preparing experiments?', 'operations', True),
                ('type-holidays', ' -- ', 'holidays', False);"""
      ),
    ]
