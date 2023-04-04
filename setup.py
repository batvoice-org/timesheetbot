import setuptools

with open("README.md", "r") as hr:
    long_description = hr.read()

setuptools.setup(
    name="timesheetbot",
    version="0.1",
    author="Nicolas Seichepine",
    author_email="support@batvoice.com",
    description="Slack bot to fill timesheets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/batvoice-org/timesheetbot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "Django >= 4",
        "psycopg2 >= 2",
        "whitenoise >= 6",
        "pyyaml >= 6",
        "gspread >= 5",
        "oauth2client >= 4",
        "gspread-formatting >= 1",
        "gunicorn >= 20",
        "pytz >= 2022",
        "json_log_formatter >= 0.5",
        "coloredlogs >= 15.0",
    ],
    extras_require={
        "dev": [
            "black >= 23.1.0",
            "pip-tools >= 6.12.3",
            "pre-commit >= 3.2.2",
        ],
    },
)
