Hello.

This is test exercise.
This little app represents small service to monitor websites and save these logs to PostgreSQL via Kafka.
It consists of two parts - consumer and producer.
They both are available in different Docker containers which you can run on one or more machines.

Consumer consumes messages from Kafka and saves them to PostgreSQL.
Producer gets urls list for checking from PostgreSQL, checks them and then sends info to Kafka topic.

Before building images you should fill several files with credentials in the directory where you've cloned the repo.

Such as:

* .ca-cert - CA used to sign certificate
* .cert-key - Private Key file of certfile certificate
* .cert-signed - Signed certificate
* .env - list of environment variables for production
* .env.test - list of environment variables for tests
You can find .env.example as an example what info you should put to .env* files.

After cloning this repo you can build two Docker images one for consumer and one for producer.

To build consumer image run from directory where you've cloned the repo:
```docker build --tag aiven_consumer_image . -f consumer/Dockerfile```

To build producer image run from directory where you've cloned the repo:
```docker build --tag aiven_producer_image . -f producer/Dockerfile```

To start consumer container run from directory where you've cloned the repo:
```docker run --env-file .env --network host -v /etc/localtime:/etc/localtime:ro --name aiven_consumer_container aiven_consumer_image```

To start producer container run from directory where you've cloned the repo:
```docker run --env-file .env --network host -v /etc/localtime:/etc/localtime:ro --name aiven_producer_container aiven_producer_image```

Tests are available inside container which you can run as follows:

for consumer - ```docker run -it --env-file .env --network host -v /etc/localtime:/etc/localtime:ro --name aiven_consumer_container aiven_consumer_image /bin/bash```

for producer - ```docker run -it --env-file .env --network host -v /etc/localtime:/etc/localtime:ro --name aiven_producer_container aiven_producer_image /bin/bash```
and then run ```pytest``` from inside container for tests.

