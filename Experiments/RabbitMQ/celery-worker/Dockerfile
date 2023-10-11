FROM python:3.10

USER root

RUN echo "Starting..."

RUN apt-get update && apt-get install -y lsb-release

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
