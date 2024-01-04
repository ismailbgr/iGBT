FROM bitnami/pytorch
USER root

# add app group
RUN groupadd appuser -g 1000

# add app user
RUN useradd appuser -g appuser -u 1000

RUN apt update && apt install -y python3-dev gcc libc-dev python3-pip
RUN apt install -y ffmpeg flac 

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# copy the app
COPY . /app

#chdir
WORKDIR /app

# chown
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /.cache

USER appuser

# run the celery worker
CMD celery -A tasks worker --loglevel=info -Q speechtexter