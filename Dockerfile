FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY ./shortener /code/
COPY ./templates /code/
COPY ./urls /code/
COPY ./utils /code/
COPY ./manage.py /code/
COPY ./requirements.txt /code/
COPY ./frontend/dist/shortener /code/frontend