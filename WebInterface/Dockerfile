FROM alpine:3.19.1

RUN apk update && apk add python3-dev gcc libc-dev py3-pip

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# copy the app
COPY . /app

#chdir
WORKDIR /app

# run the celery worker
# CMD celery -A app worker --loglevel=info
# install uvicorn
RUN pip3 install --break-system-packages uvicorn

# run the server
CMD uvicorn app:app --host 0.0.0.0 --port 5000 
