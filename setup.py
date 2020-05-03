import setuptools

with open("README.md", "r") as hr:
    long_description = hr.read()

setuptools.setup(
    name="timesheetbot",
    version="0.1",
    author="Nicolas Seichepine",
    author_email="timesheetbot@mail.seichepine.org",
    description="Slack bot to fill timesheets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sei-nicolas/timesheetbot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=['Django >= 2.0', 'psycopg2 >= 2.0', 'whitenoise >= 5.0', 'pyyaml >= 5.0', 'gspread >= 3.0', 'oauth2client >= 4.0', 'gspread-formatting', 'gunicorn >= 20.0']
)
