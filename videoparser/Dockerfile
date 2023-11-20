FROM alpine


# install ffmpeg and python3
RUN apk add --no-cache ffmpeg python3 py3-pip

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt


# copy the app
COPY . /app

#chdir
WORKDIR /app

# run the celery worker
CMD celery -A video_parsing worker --loglevel=info