FROM python:3.8.16-slim-buster

ARG USER_DIR=/user/app

# set work directory
WORKDIR $USER_DIR

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#
# RUN apt-get update && apt-get install -y\
#     libpq-dev\
#     gcc\
#     && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

# install dependencies
RUN set -ex && \
    pip install -U pip &&\
    pip install --no-cache-dir -r requirements.txt &&\
    pip cache purge

EXPOSE 8000
