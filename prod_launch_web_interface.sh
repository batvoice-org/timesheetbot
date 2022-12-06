#!/bin/bash
source /env/bin/activate
gunicorn timesheetbot.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 900 -
