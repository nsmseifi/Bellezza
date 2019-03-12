import json
import logging
import os
from uuid import uuid4

from sqlalchemy import and_

from log import Msg
from helper import Now, model_to_dict, Http_error, value, check_schema
from .model import DirectMessage
from user.controller import get_profile
from event.controller import add as add_event


def add(data, username, db_session):
    logging.info(Msg.START)

    required_data = ['message', 'reciever']

    check_schema(required_data, data.keys())

    reciever = get_profile(data['reciever'], db_session)

    logging.debug(Msg.SCHEMA_CHECKED)

    model_instance = DirectMessage()
    model_instance.sender = username
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.reciever = reciever.username
    model_instance.message = data.get('message')
    model_instance.seen = False

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    event_data = {'entity_name': 'DirectMessage', 'entity_id': model_instance.id,
                  'action': 'ADD',
                  'target': model_instance.reciever, }

    add_event(event_data, username, db_session)

    logging.debug(Msg.DB_ADD)

    logging.info(Msg.END)

    return model_instance


def get(direct_id, db_session, username):
    logging.info(Msg.START + 'getting direct_message = {}'.format(direct_id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(DirectMessage).filter(
        DirectMessage.id == direct_id).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {'id': Msg.NOT_FOUND})

    logging.info(Msg.END)

    model_instance.seen =True

    return model_instance


def delete(direct_id, db_session, username):
    logging.info(Msg.START + 'user is {}  '.format(
        username) + 'direct_message= {}'.format(direct_id))

    logging.debug(Msg.DELETE_REQUEST + 'direct_message= {}'.format(direct_id))

    logging.debug(Msg.MODEL_GETTING)

    model_instance = db_session.query(DirectMessage).filter(
        DirectMessage.id == direct_id).first()
    if model_instance is None:
        logging.error(
            Msg.NOT_FOUND + ' direct message by id = {}'.format(direct_id))
        raise Http_error(404, {'id': Msg.NOT_FOUND})

    if username != model_instance.sender:
        logging.error(Msg.NOT_ACCESSED)
        raise Http_error(401, {'username': Msg.NOT_ACCESSED})

    db_session.query(DirectMessage).filter(
        DirectMessage.id == direct_id).delete()

    event_data = {'entity_name': 'DirectMessage', 'entity_id': model_instance.id,
                  'action': 'DELETE',
                  'target': model_instance.reciever, }

    add_event(event_data, username, db_session)

    logging.debug(Msg.DELETE_SUCCESS)

    logging.info(Msg.END)

    return {}


def get_messages_by_recipient(db_session, username, data):
    logging.info(Msg.START)
    required = ['recipient', 'scroll']
    check_schema(required, data.keys())
    recipient = data.get('recipient')

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count_number') is None:
        data['count_number'] = 50

    logging.debug(Msg.GET_ALL_REQUEST + 'DirectMessages...')

    if data.get('scroll') == 'down':
        result = db_session.query(DirectMessage).filter(
            and_(DirectMessage.sender.in_((username, recipient)),
                 DirectMessage.reciever.in_((username, recipient)))).filter(
            DirectMessage.creation_date < data.get('time')).order_by(
            DirectMessage.creation_date.desc()).limit(
            data.get('count_number')).all()
    else:
        result = db_session.query(DirectMessage).filter(
            and_(DirectMessage.sender.in_((username, recipient)),
                 DirectMessage.reciever.in_(username, recipient))).filter(
            DirectMessage.creation_date > data.get('time')).order_by(
            DirectMessage.creation_date.desc()).limit(
            data.get('count_number')).all()

    final_result = []

    for message in result:
        message.seen = True
        message_creator = get_profile(message.creator, db_session)

        creator = model_to_dict(message_creator)
        del creator['password']

        new_message = model_to_dict(message)

        new_message['creator'] = creator
        final_result.append(new_message)

    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return final_result


def set_message_as_seen(direct_id, username, db_session):
    logging.info(Msg.START)

    model_instance = db_session.query(DirectMessage).filter(
        DirectMessage.id == direct_id).first()
    if model_instance is None:
        logging.error(
            Msg.NOT_FOUND + ' direct message by id = {}'.format(direct_id))
        raise Http_error(404, {'id': Msg.NOT_FOUND})

    if model_instance.reciever != username:
        logging.error(
            Msg.SET_SEEN_ERROR + json.dumps(model_to_dict(model_instance)))
        raise Http_error(403, {'reciever': Msg.SET_SEEN_ERROR})

    model_instance.seen = True

    return model_instance


def edit(direct_id, db_session, data, username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]

    logging.debug(Msg.EDIT_REQUST)

    model_instance = get(direct_id, db_session, username)
    if model_instance:
        logging.debug(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {'message': Msg.NOT_FOUND})

    if model_instance.sender != username:
        logging.error(Msg.ALTERING_AUTHORITY_FAILED)
        raise Http_error(403, {'sender': Msg.ALTERING_AUTHORITY_FAILED})

    model_instance.modification_date = Now()
    model_instance.modifier = username
    model_instance.message = data.get('message')

    logging.debug(Msg.MODEL_ALTERED)

    logging.debug(Msg.EDIT_SUCCESS + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance


def get_new_messages(db_session, data, username):
    logging.info(Msg.START)
    required = ['scroll']
    check_schema(required, data.keys())

    if data.get('time') is None:
        data['time'] = Now()

    if data.get('count_number') is None:
        data['count_number'] = 50

    logging.debug(Msg.GET_ALL_REQUEST + 'new  unread DirectMessages...')

    if data.get('scroll') == 'down':
        result = db_session.query(DirectMessage).filter(
            and_(DirectMessage.reciever == username,
                 DirectMessage.seen == False)).filter(
            DirectMessage.creation_date < data.get('time')).order_by(
            DirectMessage.creation_date.desc()).limit(
            data.get('count_number')).all()
    else:
        result = db_session.query(DirectMessage).filter(
            and_(DirectMessage.reciever == username,
                 DirectMessage.seen == False)).filter(
            DirectMessage.creation_date > data.get('time')).order_by(
            DirectMessage.creation_date.desc()).limit(
            data.get('count_number')).all()

    final_result = []

    for message in result:
        message_creator = get_profile(message.creator, db_session)

        creator = model_to_dict(message_creator)
        del creator['password']

        new_message = model_to_dict(message)

        new_message['creator'] = creator
        final_result.append(new_message)

    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return final_result


def get_new_messages_count(db_session, username):
    logging.info(Msg.START)

    logging.debug(Msg.GET_ALL_REQUEST + 'the count of unread DirectMessages...')

    result = db_session.query(DirectMessage).filter(
        and_(DirectMessage.reciever == username,
             DirectMessage.seen == False)).count()
    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)

    return {'count': int(result)}
