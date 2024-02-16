FROM postgres:16.2

# create a database named 'igbt' and a user named 'igbt' with password 'bitircez'

ENV POSTGRES_USER igbt
ENV POSTGRES_PASSWORD bitircez
ENV POSTGRES_DB igbt

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
