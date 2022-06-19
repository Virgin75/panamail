FROM python:3.8

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update --yes\
    && apt install libpq-dev python-dev --yes

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
