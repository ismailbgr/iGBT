# Introduction

The project is composed of microservices, which are interconnected through a message queue architecture. Each service listens for a specific queue, executes the assigned task, and returns the output.️

Here is a diagram of the architecture:

![[assets/docker-compose.png]]

## Services

Currently there are 10 services:

- **[[RabbitMQ]]**: RabbitMQ is a message broker. It is used to send messages between the services. It is the central piece of the architecture.
- **[[Celery]]**: Celery is a distributed task queue. It is used to execute tasks asynchronously. It is composed of a message broker ([[RabbitMQ]]) and workers (Celery workers). The workers are the ones that execute the tasks. The message broker is the one that sends the tasks to the workers. The workers are the ones that execute the tasks. The message broker is the one that sends the tasks to the workers.
- **[[Ollama]]**: Ollama is a service that can easily inference Large Language Models (LLMs) using Dockerimage like structure. It is used to perform the local inference of the LLMs.
- **[[WebInterface]]**: The web interface is the entry point of the application. It is a web application that allows the user to interact with the system. It is built with Flask and sends requests [[Celery]] workers.
- **[SpeechTexter](Services/SpeechTexter.md)**: The speech texter is a service that converts speech to text. It communicates with the reqired APIs to perform the conversion.
- **[VideoParser](Services/VideoParser.md)**: The video parser is a service that processes a given video.
- **[[LLM]]**: The LLM is a service that receives a text and produces a summary of it. It communicates with the reqired 3rd or 1st party APIs (such as [[Ollama]]) to perform the conversion.
- **[[Database]]**: The database is a PostgreSQL database. It is used to store the data of the application.
- **[[Adminer]]**: Adminer is a web application that allows the user to interact with the database. It is built with Flask and sends requests [[Celery]] workers.
