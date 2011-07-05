When Will It Air - wwia

A "prototype" webapp to check the next airing time of your favorite TV shows. It displays the countdown to the next airing time of the show along with some basic info about the last two episodes aired. Any number of shows can be added to the main page and there are a wide number of shows to choose from via the ‘Add’ page.

The backend is written in Python. The tvshows metadata and episodes data is stored in a MySQL database, which is queried by the main python script as well as the ‘add more shows’ script. No web framework is used for this prototype webapp. Instead content is served directly using mod_python via Apache web server. Jinja2 is used as the templating language.

There is a background job needed to update the episodes data, which is done by an update script which should be run every day or at a higher frequency. This update script scrapes episodes data from Internet and updates the database as required. It uses BeautifulSoup module for this purpose.

pytz module is also used to make time-mangling easy. Specifically, the screen scraped date/time is for ‘Eastern’ time zone. Hence, this module is used when converting between user time zone and Eastern Time zone.

All the dependencies are listed below:

BeautifulSoup   - 3.0.8.1

MySQL-python    - 1.2.2

Jinja2          - 2.5.5

mod_python      - 3.3.1

pytz            - 2006p
