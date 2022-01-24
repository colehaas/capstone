FROM python:3.9
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ADD . /driverite
WORKDIR /driverite
RUN pip install -r requirements.txt
VOLUME /mnt/data-source/database
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py createsuperuser2 --username test1 --password 123 --noinput --email 'test1@aol.com'

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]