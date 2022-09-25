FROM python:3.10.7-alpine3.16

ARG USER_DIR=/user/app

# set work directory
WORKDIR $USER_DIR

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY web_server/ web_server
COPY manage.py ./
COPY requirements.txt ./
COPY requirements-dev.txt ./
COPY pytest.ini ./
COPY .flake8 ./

# install dependencies
RUN pip install --upgrade pip
RUN pip install pip-tools
RUN pip-sync requirements.txt requirements-dev.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]