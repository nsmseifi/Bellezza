import json
import logging
import os
from uuid import uuid4

from sqlalchemy import and_

from log import Msg
from helper import Now, model_to_dict, Http_error, value, check_schema
from .model import Event
from user.controller import get_profile


def add(data, username, db_session):
    logging.info(Msg.START)

    required_data = ['action', 'target', 'entity_name', 'entity_id']

    check_schema(required_data, data.keys())

    logging.debug(Msg.SCHEMA_CHECKED)

    model_instance = Event()
    model_instance.creator = username
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.target = data.get('target')
    model_instance.action = data.get('action')
    model_instance.entity_id = data.get('entity_id')
    model_instance.entity_name = data.get('entity_name')
    model_instance.seen = False

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD)

    logging.info(Msg.END)

    return model_instance


def get_events(data, db_session, username):

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count_number') is None:
        data['count_number'] = 50

    final_result = []

    logging.debug(Msg.GET_ALL_REQUEST + 'Events...')
    logging.info(Msg.START + 'getting events for user = {}'.format(username))
    logging.debug(Msg.MODEL_GETTING)

    if data.get('scroll') == 'down':

        result = db_session.query(Event).filter(and_(Event.target == username,
                                                     Event.creation_date < data.get(
                                                         'time'))).order_by(
            Event.creation_date.desc()).limit(data.get('count_number')).all()
    else:
        result = db_session.query(Event).filter(and_(Event.target == username,
                                                     Event.creation_date >
                                                     data.get(
                                                         'time'))).order_by(
            Event.creation_date.desc()).limit(data.get('count_number')).all()

    for event in result:
        event.seen = True
        event_creator = get_profile(event.creator, db_session)

        creator = model_to_dict(event_creator)
        del creator['password']

        new_event = model_to_dict(event)

        new_event['creator'] = creator
        final_result.append(new_event)

    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return final_result


def get_new_events(db_session, data, username):
    logging.info(Msg.START)
    required = ['scroll']
    check_schema(required, data.keys())

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count_number') is None:
        data['count_number'] = 50

    logging.debug(Msg.GET_ALL_REQUEST + 'new  unread Events...')

    if data.get('scroll') == 'down':
        result = db_session.query(Event).filter(
            and_(Event.target == username, Event.seen == False)).filter(
            Event.creation_date < data.get('time')).order_by(
            Event.creation_date.desc()).limit(data.get('count_number')).all()
    else:
        result = db_session.query(Event).filter(
            and_(Event.target == username, Event.seen == False)).filter(
            Event.creation_date > data.get('time')).order_by(
            Event.creation_date.desc()).limit(data.get('count_number')).all()

    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return result


def get_new_events_count(db_session, username):
    logging.info(Msg.START)

    logging.debug(Msg.GET_ALL_REQUEST + 'the count of unread Events...')

    result = db_session.query(Event).filter(
        and_(Event.target == username, Event.seen == False)).count()
    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return {'count': int(result)}
