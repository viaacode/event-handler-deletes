#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch

from flask_api import status
from lxml.etree import XMLSyntaxError


from app.app import (
    liveness_check,
    handle_event,
)
from tests.resources.premis_events import single_premis_event_delete
from app.helpers.events_parser import InvalidPremisEventException, PremisEvents


def test_liveness_check():
    assert liveness_check() == ('OK', status.HTTP_200_OK)


@patch('pika.BlockingConnection')
@patch('app.app.request')
def test_handle_event(post_event_mock, conn_mock):
    # Mock request.data to return a single premis event
    post_event_mock.data = single_premis_event_delete

    result = handle_event()
    result == ("OK", status.HTTP_200_OK)


@patch('app.app.request')
@patch.object(PremisEvents, '__init__', side_effect=XMLSyntaxError('', 1, 1, 1))
def test_handle_event_xml_error(premis_events_mock, post_event_mock):
    # Mock request.data to return irrelevant data
    post_event_mock.data = ''

    result = handle_event()
    result[1] == status.HTTP_400_BAD_REQUEST


@patch('app.app.request')
@patch.object(PremisEvents, '__init__', side_effect=InvalidPremisEventException)
def test_handle_event_invalid_premis_event(premis_events_mock, post_event_mock):
    # Mock request.data to return irrelevant data
    post_event_mock.data = ''

    result = handle_event()
    result[1] == status.HTTP_400_BAD_REQUEST
