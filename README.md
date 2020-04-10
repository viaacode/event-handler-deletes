# Event handler: Deletes

## Synopsis

Handles incoming webhooks from Mediahaven. It transforms the incoming event and forwards it to a Rabbit queue. It will only accept events of type `"DELETE"` and `"DELETE.UNDELETE"`. It will drop all other types. For more information on configuring RabbitMQ see [RabbitMQ](#RabbitMQ).

## Prerequisites

- Git
- Docker
- Python 3.6+
- Linux (if you want to run it locally, uwsgi is not available on other
  platforms.)
- Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081)

## Usage

1. Clone this repository with:

   `$ git clone https://github.com/viaacode/event-handler-deletes.git`

2. Change into the new directory.

### Running locally

**Note**: As per the aforementioned requirements, this is a Python3 application. Check your Python version with `python --version`. You may want to substitute the `python` command below with `python3` and if your Python version
is < 3.

1. Start by creating a virtual environment:

   `$ python -m venv env`

2. Activate the virtual environment:

    `$ source env/bin/activate`

3. Install the external modules:

   ```
   $ pip install -r requirements.txt \
        --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
        --trusted-host do-prd-mvn-01.do.viaa.be
   ```

4. Run the tests with:

    `$ pytest -v`

5. Run the application:

   `$ uwsgi -i uwsgi.ini`

The application is now serving requests on `localhost:8080`. Try it with:

```
$ curl -v -X GET localhost:8080/health/live
```

#### Testing different events

Different events (as XML-files) are stored under `./tests/resources/`. Try them with:

##### Single event delete

```bash
$ curl -i -X POST \
    -H "Content-type: text/xml; charset=utf-8" \
    --data-binary @tests/resources/single_premis_event_delete.xml \
    localhost:8080/event
```

##### Single event undelete

```bash
$ curl -i -X POST \
    -H "Content-type: text/xml; charset=utf-8" \
    --data-binary @tests/resources/single_premis_event_undelete.xml \
    localhost:8080/event
```

##### Multiple events in one payload

```bash
$ curl -i -X POST \
    -H "Content-type: text/xml; charset=utf-8" \
    --data-binary @tests/resources/multi_premis_event.xml \
    localhost:8080/event
```

##### Invalid event

```bash
$ curl -i -X POST \
    -H "Content-type: text/xml; charset=utf-8" \
    --data-binary @tests/resources/invalid_premis_event.xml \
    localhost:8080/event
```

##### Invalid XML payload

```bash
$ curl -i -X POST \
    -H "Content-type: text/xml; charset=utf-8" \
    --data-binary @tests/resources/invalid_xml_event.xml \
    localhost:8080/event
```

These should return proper informative messages to the client caller.


### Running using Docker

1. Build the container:

   `$ docker build . -t event-handler-deletes`

2. Run the container:

   `$ docker run --rm -p 8080:8080 event-handler-deletes`

You can try the same cURL commands as specified above.

#### RabbitMQ

As the app sends the transformed messages to a RabbitMQ queue, we'll need to run
and setup an instance of a RabbitMQ service. If no such service is available, you
can easily use a Docker container to do so.

1. Build the container:

   `$ docker build -f ./Docker/Dockerfile.rabbitmq -t event-handler-deletes/rabbitmq ./Docker`

2. Run the container:

   `$ docker run -p 5672:5672 -p 15672:15672 --rm event-handler-deletes/rabbitmq`

Go to `localhost:15672` and log in with `guest/guest` to see if it is running successfully.

The messages will be send via direct exchange type to the queue defined in `config.yml`.

#### Docker Compose

If you want to run the app in a container as well as the rabbit container, you'll
need to make sure that they are allowed to communicate with each other.
You can use `Docker Compose` to do so:

   `$ docker-compose up`

Check if they are running with:

   `$ docker-compose ps`

In the `config.yml` file, be sure to point the rabbit host to the RabbitMQ container name
and not localhost. Send the same cURL commands as specified above.