#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
import requests
from flask import Flask, request
from flask_api import status
from lxml.etree import XMLSyntaxError
from viaa.configuration import ConfigParser
from viaa.observability import correlation, logging


from .helpers.events_parser import PremisEvents, InvalidPremisEventException
from .services.rabbit_service import RabbitService

app = Flask(__name__)
config = ConfigParser()
log = logging.get_logger(__name__, config=config)
correlation.initialize(flask=app, logger=log, pika=pika, requests=requests)


@app.route("/health/live")
def liveness_check() -> str:
    return "OK", status.HTTP_200_OK


@app.route("/event", methods=["POST"])
def handle_event() -> str:
    # Get and parse the incoming event(s)
    log.debug(request.data)
    try:
        premis_events = PremisEvents(request.data)
    except (XMLSyntaxError, InvalidPremisEventException) as e:
        log.error(e)
        return f"NOK: {e}", status.HTTP_400_BAD_REQUEST

    log.debug(f"Events in payload: {len(premis_events.events)}")
    for event in premis_events.events:
        log.debug(
            f"event_type: {event.event_type} / fragment_id: {event.fragment_id} / external_id: {event.external_id}"
        )
        # is_valid means we have a FragmentID and a "DELETE"/"DELETE.UNDELETE" eventType
        if event.is_valid:
            pid = event.external_id
            message = event.to_json()
            RabbitService(config=config.config).publish_message(message)
            log.info(
                f"(UN)DELETE sent for {pid}.",
                mediahaven_event=event.event_type,
                fragment_id=event.fragment_id,
                pid=event.external_id,
            )
        else:
            log.debug(f"Dropping event -> ID:{event.event_id}, type:{event.event_type}")
    return "OK", status.HTTP_200_OK
