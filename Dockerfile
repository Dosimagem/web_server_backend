FROM python:3.6.9

ARG USER_DIR=/user/app

# set work directory
WORKDIR $USER_DIR

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt $USER_DIR
RUN pip install -r requirements.txt

# copy project
COPY . $USER_DIR

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]