FROM python:alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["/app/docker/habit_tracker/docker-entrypoint.sh"]
