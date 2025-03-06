FROM python:alpine

RUN adduser -D celeryuser

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

USER celeryuser

CMD ["celery", "-A", "habit_tracker", "worker", "--loglevel=info"]
