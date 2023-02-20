FROM python:3.10-alpine

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
RUN apk add build-base

# Install pip requirements
COPY Pipfile Pipfile.lock ./

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    && apk add libpq-dev gcc \
    && apk add libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev python3-dev


RUN pip install pipenv
#RUN pipenv requirements > requirements.txt
#RUN #pip uninstall -y pipenv
#RUN python -m pip install --upgrade pip
#RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN pipenv install -d --system --deploy --ignore-pipfile
RUN pipenv install psycopg2

RUN apk del .tmp-build-deps

WORKDIR /discord
COPY . /discord

RUN adduser -u 5678 --disabled-password --gecos "" user && chown -R user /discord
USER user

