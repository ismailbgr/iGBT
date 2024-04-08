FROM pytorch/pytorch:2.2.1-cuda11.8-cudnn8-runtime
USER root

RUN apt update && apt install -y python3-dev gcc libc-dev python3-pip
# RUN apt install -y ffmpeg flac 

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# copy the app
COPY . /app

#chdir
WORKDIR /app

# run the celery worker
CMD celery -A tasks worker --loglevel=info -Q sentimentclassifier