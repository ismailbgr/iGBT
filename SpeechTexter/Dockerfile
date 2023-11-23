FROM alpine

RUN apk update && apk add python3-dev gcc libc-dev py3-pip
RUN apk add ffmpeg flac

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# copy the app
COPY . /app

#chdir
WORKDIR /app

# run the celery worker
CMD celery -A tasks worker --loglevel=info -Q speechtexter