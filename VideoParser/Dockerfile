FROM alpine:3.19.1

# add app group
RUN addgroup -S appuser -g 1000

# add app user
RUN adduser -S appuser -G appuser -u 1000



# install ffmpeg and python3
RUN apk add --no-cache ffmpeg python3 py3-pip

# install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt


# copy the app
COPY . /app

#chdir
WORKDIR /app

# chown
RUN chown -R appuser:appuser /app

USER appuser

# run the celery worker
CMD celery -A tasks worker --loglevel=info -Q videoparser