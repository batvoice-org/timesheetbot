from django.contrib import admin

from .models import User, WorkType, TimeEntry, NotificationHour, Program


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(NotificationHour)
class NotificationHourAdmin(admin.ModelAdmin):
    pass


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    pass
