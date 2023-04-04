# Generated by Django 4.1.3 on 2022-12-02 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("timesheetbot", "0006_user_working_timezone"),
    ]

    operations = [
        migrations.CreateModel(
            name="Program",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slack_value", models.CharField(max_length=15, unique=True)),
                ("slack_description", models.CharField(max_length=63, unique=True)),
                (
                    "spreadsheet_column_letter",
                    models.CharField(max_length=2, unique=True),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.RenameField(
            model_name="timeentry",
            old_name="activities",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="spreadsheet_row_first_day_of_week",
            new_name="spreadsheet_top_left_row",
        ),
        migrations.RemoveField(
            model_name="timeentry",
            name="is_cii",
        ),
        migrations.RemoveField(
            model_name="timeentry",
            name="is_cir",
        ),
        migrations.RemoveField(
            model_name="timeentry",
            name="is_holiday",
        ),
        migrations.AlterField(
            model_name="worktype",
            name="slack_description",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="worktype",
            name="slack_value",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="worktype",
            name="spreadsheet_value",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name="timeentry",
            name="program",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="timesheetbot.program",
            ),
        ),
        migrations.RunSQL("UPDATE timesheetbot_worktype SET is_active=false;"),
        migrations.RunSQL(
            """INSERT INTO timesheetbot_worktype (slack_value, slack_description, spreadsheet_value, is_active) VALUES
                ('meeting_planning', 'Meeting - planning : sprints, scrums, OKRs, operations else', 'Meeting - planning : sprints, scrums, OKRs, operations else', True),
                ('meeting_worskhop', 'Meeting - worskhop : peer programming, working together', 'Meeting - worskhop : peer programming, working together', True),
                ('meeting_admin', 'Meeting - admin : other NA to a program', 'Meeting - admin : other NA to a program', True),
                ('meeting_sales', 'Meeting - sales : other NA to a program', 'Meeting - sales : other NA to a program', True),
                ('meeting_customer_support_1', 'Meeting - customer support : planning roadmap, co-construction, Comop, Copil, follow-up', 'Meeting - customer support : planning roadmap, co-construction, Comop, Copil, follow-up', True),
                ('meeting_customer_support_2', 'Meeting - customer support : other NA such as demo of a feature, issue, etc.', 'Meeting - customer support : other NA such as demo of a feature, issue, etc.', True),
                ('meeting_other', 'Meeting - other', 'Meeting - other', True),
                ('development_new_feature', 'Development - new feature', 'Development - new feature', True),
                ('development_bug_fixes', 'Development - bug fixes', 'Development - bug fixes', True),
                ('development_devops', 'Development - devops', 'Development - devops', True),
                ('development_datascience', 'Development - datascience', 'Development - datascience', True),
                ('development_other', 'Development - other', 'Development - other', True),
                ('study_r&dStudy - R&D', 'Study - R&D', '', True),
                ('study_other', 'Study - other', 'Study - other', True),
                ('operations_data_building_1', 'Operations - data building : transcription', 'Operations - data building : transcription', True),
                ('operations_data_building_2', 'Operations - data building : classification', 'Operations - data building : classification', True),
                ('operations_data_building_3', 'Operations - data building : calls qm evaluations', 'Operations - data building : calls qm evaluations', True),
                ('operations_data_building_4', 'Operations - data building : other', 'Operations - data building : other', True);
            """
        ),
        migrations.RunSQL(
            """INSERT INTO timesheetbot_program (slack_value, slack_description, spreadsheet_column_letter, is_active) VALUES
                ('cir', '*CIR*: _R&D activities_', 'I', True),
                ('cii', '*CII*: _new features/ideas for the product_', 'H', True),
                ('project_1', '*Project 1*: _Aqua_', 'J', True),
                ('project_2', '~*Project 2*: :soon:~', 'K', True),
                ('sick', '*Sick* :face_with_thermometer:', 'G', True),
                ('holiday', '*Holiday* :palm_tree:', 'F', True),
                ('none', '_None of them_', 'E', True);
            """
        ),
    ]
