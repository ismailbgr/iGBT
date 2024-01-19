FROM bitnami/pytorch:2.1.0

USER root

RUN groupadd appuser -g 1000

RUN useradd appuser -g appuser -u 1000

RUN apt update
RUN apt install -y ffmpeg flac

RUN apt-get install espeak -y

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# copy the app
COPY . /app

#chdir
WORKDIR /app

# chown
RUN chown -R appuser:appuser /app

# run the celery worker
CMD celery -A tasks worker --loglevel=info -Q tts


