from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=127, unique=True)
    slack_username = models.CharField(max_length=255, unique=True)
    slack_userid = models.CharField(max_length=15, unique=True)
    do_send_copy_of_data = models.BooleanField(null=False, default=True)
    slack_republish_hook = models.CharField(max_length=127, unique=False, blank=True, default='')
    min_hours_between_notifications = models.IntegerField(default=4)
    spreadsheet_row_first_day_of_week = models.IntegerField(unique=True, blank=False, null=False)
    look_for_data_starting_at = models.DateField()
    last_notified = models.DateTimeField()

    def __str__(self):
        return "<User: {}>".format(self.slack_username)

class WorkType(models.Model):
    slack_value = models.CharField(max_length=15, unique=True)
    slack_description = models.CharField(max_length=63, unique=True)
    spreadsheet_value = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return "<WorkType: {}>".format(self.spreadsheet_value)

class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activities = models.CharField(max_length=1023, blank=True, null=False)
    date = models.DateField(blank=False, null=False)
    is_morning = models.BooleanField(null=False)
    is_afternoon = models.BooleanField(null=False)
    is_cir = models.BooleanField(null=True, default=False)
    is_cii = models.BooleanField(null=True, default=False)
    is_holiday = models.BooleanField(default=False, null=False)
    work_type = models.ForeignKey(WorkType, on_delete=models.SET_NULL, null=True)
    creation_time = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    modification_time = models.DateTimeField(auto_now=True, blank=False, null=False)
    has_been_written_in_gsheet = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = ('user', 'date', 'is_morning',)

    def __str__(self):
        return "<TimeEntry: {}/{}/".format(self.user, self.date) + ("morning" if self.is_morning else "afternoon") +  ">"

class NotificationHour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timezone_hour = models.IntegerField(null=False)

    class Meta:
        unique_together = ('user', 'timezone_hour',)

    def __str__(self):
        return "<NotificationHour: {} at {}>".format(self.user, self.timezone_hour)

