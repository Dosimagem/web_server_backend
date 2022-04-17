FROM python:3.6.9

# set work directory
WORKDIR /user/app

# install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt /user/app
RUN pip install -r requirements.txt

# copy project
COPY . /user/app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]