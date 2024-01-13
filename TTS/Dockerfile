FROM bitnami/pytorch

USER root

RUN groupadd appuser -g 1000

RUN useradd appuser -g appuser -u 1000

RUN apt install -y ffmpeg flac 

RUN apt-get install espeak -y



WORKDIR /app

COPY . .

