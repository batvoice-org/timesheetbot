from django.urls import re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from timesheetbot.utils.slack_query_handler import handle_slack

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^favicon\.ico$", RedirectView.as_view(url="/static/images/favicon.ico")),
    re_path(r"^slack$", handle_slack),
]
