########################################################################################################################
#
# Recipe for “Libs” image.
#
########################################################################################################################

FROM python:3.10-slim AS libs

# System packages
RUN apt-get update
RUN apt-get install -y libpq-dev build-essential

RUN mkdir -p /app /env

WORKDIR /app

RUN useradd --home-dir /app --group www-data app 
RUN pip install -U pip wheel virtualenv 
RUN chown app:www-data -R /app /env

# Add and install python requirements in a virtualenv
USER app
COPY requirements.txt ./
RUN virtualenv -p python3 /env
RUN /env/bin/pip install -r requirements.txt

COPY timesheetbot ./timesheetbot
COPY setup.py ./setup.py
COPY README.md ./README.md
RUN /env/bin/pip install -e .

USER root
ENV DJANGO_SETTINGS_MODULE=timesheetbot.settings
RUN /env/bin/python /app/timesheetbot/manage.py collectstatic --no-input -v 0
RUN (rm -rf /app/.cache)

########################################################################################################################
#
# Recipe for “Production” image.
#
########################################################################################################################

FROM python:3.10-slim

RUN mkdir -p /app /env

# System packages
RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y libpq5
RUN apt-get autoremove --purge
RUN apt-get clean

RUN useradd --home-dir /app --group www-data app 
RUN chown app:www-data -R /app /env

COPY --from=libs --chown=app:www-data /env /env
COPY --from=libs --chown=app:www-data /app /app
COPY .docker_bashrc /app/.bashrc
COPY prod_launch_web_interface.sh /app/starter.sh

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=timesheetbot.settings

USER app
ENTRYPOINT ["/bin/bash"]
CMD ["/app/starter.sh"]
