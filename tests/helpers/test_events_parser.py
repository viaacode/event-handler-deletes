#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from lxml.etree import XMLSyntaxError
import json

from tests.resources.premis_events import (
    single_premis_event_delete,
    single_premis_event_undelete,
    multi_premis_event,
    invalid_premis_event,
    invalid_xml_event,
)
from app.helpers.events_parser import (
    PremisEvents,
    InvalidPremisEventException,
)


def test_single_event_delete():
    p = PremisEvents(single_premis_event_delete)
    assert len(p.events) == 1

    assert p.events[0].event_id == "111"
    assert p.events[0].event_detail == "Ionic Defibulizer"
    assert p.events[0].fragment_id == "a1b2c3"
    assert p.events[0].event_type == "DELETE"
    assert p.events[0].event_outcome == "NOK"
    assert p.events[0].is_valid


def test_single_event_undelete():
    p = PremisEvents(single_premis_event_undelete)
    assert len(p.events) == 1

    assert p.events[0].event_id == "111"
    assert p.events[0].event_detail == "Ionic Defibulizer"
    assert p.events[0].fragment_id == "a1b2c3"
    assert p.events[0].event_type == "DELETE.UNDELETE"
    assert p.events[0].event_outcome == "OK"
    assert p.events[0].is_valid


def test_multi_event():
    p = PremisEvents(multi_premis_event)
    assert len(p.events) == 3

    assert p.events[0].event_id == "222"
    assert p.events[0].event_detail == "Ionic Defibulizer Plus"
    assert p.events[0].fragment_id == "a1b2c3"
    assert p.events[0].event_type == "EXPORT"
    assert p.events[0].event_outcome == "OK"
    assert not p.events[0].is_valid

    assert p.events[1].event_id == "333"
    assert p.events[1].event_detail == "Ionic Defibulizer"
    assert p.events[1].fragment_id == "d4e5f6"
    assert p.events[1].event_type == "DELETE"
    assert p.events[1].event_outcome == "OK"
    assert p.events[1].is_valid

    assert p.events[2].event_id == "444"
    assert p.events[2].event_detail == "Ionic Defibulizer Come Back"
    assert p.events[2].fragment_id == "g7h8j9"
    assert p.events[2].event_type == "DELETE.UNDELETE"
    assert p.events[2].event_outcome == "OK"
    assert p.events[2].is_valid


def test_invalid_premis_event():
    with pytest.raises(InvalidPremisEventException):
        PremisEvents(invalid_premis_event)


def test_invalid_xml_event():
    with pytest.raises(XMLSyntaxError):
        PremisEvents(invalid_xml_event)


def test_to_json():
    p = PremisEvents(single_premis_event_delete).events[0]
    event_dict = {
        "event_type": "DELETE",
        "event_datetime": "2019-03-30T05:28:40Z",
        "event_detail": "Ionic Defibulizer",
        "event_id": "111",
        "event_outcome": "NOK",
        "fragment_id": "a1b2c3",
        "external_id": "a1",
        "is_valid": True
    }
    assert p.to_json() == json.dumps(event_dict)
