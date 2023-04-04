from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=127, unique=True)
    slack_userid = models.CharField(max_length=15, unique=True)
    min_hours_between_notifications = models.IntegerField(default=4)
    spreadsheet_top_row = models.IntegerField(unique=True, blank=False, null=False)
    look_for_data_starting_at = models.DateField()
    last_notified = models.DateTimeField()
    working_timezone = models.CharField(max_length=31, unique=False, default="CET")

    def __str__(self):
        return "<User: {}>".format(self.first_name)


class WorkType(models.Model):
    slack_value = models.CharField(max_length=50, unique=True)
    slack_description = models.CharField(max_length=100, unique=True)
    spreadsheet_value = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return "<WorkType: {}>".format(self.slack_description)


class Program(models.Model):
    slack_value = models.CharField(max_length=15, unique=True)
    slack_description = models.CharField(max_length=63, unique=True)
    spreadsheet_column_letter = models.CharField(max_length=2, unique=True)
    is_active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return "<Program: {}>".format(self.slack_description)


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1023, blank=True, null=False)
    date = models.DateField(blank=False, null=False)
    is_morning = models.BooleanField(null=False)
    is_afternoon = models.BooleanField(null=False)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    work_type = models.ForeignKey(WorkType, on_delete=models.SET_NULL, null=True)
    creation_time = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modification_time = models.DateTimeField(auto_now=True, blank=False, null=False)
    has_been_written_in_gsheet = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = (
            "user",
            "date",
            "is_morning",
        )

    def __str__(self):
        return (
            "<TimeEntry: {}/{}/".format(self.user, self.date)
            + ("morning" if self.is_morning else "afternoon")
            + ">"
        )


class NotificationHour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timezone_hour = models.IntegerField(null=False)

    class Meta:
        unique_together = (
            "user",
            "timezone_hour",
        )

    def __str__(self):
        return "<NotificationHour: {} at {}>".format(self.user, self.timezone_hour)
