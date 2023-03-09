
# Concept
In general this is a discord application written in clean architecture where code is split on use_cases, repos, entities.
Application is responsible for serving data on discord server. Data served (right now) is a UM weather meteogram
and the Moon phases per day. Responses are images. In the future, bot will be using API for getting data from another app called
FlightRadar (scrapping flight data), and serve the best flight prices for given direction.
There is also utils called MonManager (description below).

## BOT configuration

App is fetching meteogram from given city name. City coords are fetched from Nominatim, so response is addicted to library
response. Also, app uses specific .bin file with points matrix, which helps to calculate Polish cities coords (path needed). 
If there is no bin file, you will be fetching data from base UM website.
Also, the application is written for docker-compose use, so you have to put some credentials for images.

Summarizing configuration: 
- You have to create .env file with 
```commandline
DISCORD_TOKEN=DISCORD_TOKEN
DISCORD_GUILD=DISCORD_GUILD

HOST=localhost
PORT=5432
USER=postgres
PASSWORD=super_secret_password

DATABASE_NAME=testowy_discord

PGADMIN_EMAIL=PGADMIN_EMAIL
PGADMIN_PASSWORD=super_secret_password

POSTGRES_TEST_USER=postgres
POSTGRES_TEST_DB_NAME=test_db
POSTGRES_TEST_PASSWORD=postgres
```
- create _local_settings.py if you want to override some settings (for example path to bin file)

## MoonManager

This is a tool needed for preparing the Moon phase images. To use it, just run ```python moon_manager.py```. Class is using
external url which you can configure for your own. Basically, code is using selenium to get screenshot from website,
save it on disc, and put to database. If you want to fill your database with images for moon command, use it.

# How to play?

notice: you need to have pipenv

docker:
```bash
docker-compose up --build
```
cmd/terminal:

```bash
python discord_bot.py
```

### Tests

note: tests using a docker image, so be sure you have installed it on your machine
```bash
pipenv install --dev
pytest
```