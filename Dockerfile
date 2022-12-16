FROM python:3.8.16-alpine3.17

ARG USER_DIR=/user/app

# set work directory
WORKDIR $USER_DIR

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#
RUN apk add --no-cache build-base

# copy project
COPY web_server/ web_server
COPY manage.py ./
COPY requirements.txt ./

# install dependencies
RUN pip install no-cache-dir -U pip;\
    pip install -r requirements.txt

EXPOSE 8000
