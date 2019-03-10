import json
import logging
import os
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error, value
from .model import Tag

admin = value('admin_username', 'admin')


def add(data, username, db_session):
    if username != admin:
        logging.error(Msg.NOT_ACCESSED)
        raise Http_error(401, {'username': Msg.NOT_ACCESSED})

    logging.info(Msg.START)

    title = data.get('title')
    if title is None:
        logging.error(Msg.DATA_MISSING + ' title')
        raise Http_error(400, {'title': Msg.DATA_MISSING})

    tag = db_session.query(Tag).filter(
        Tag.title == title).first()
    if tag:
        logging.error(Msg.NOT_UNIQUE + '  title already exists')
        raise Http_error(409, {'title': Msg.NOT_UNIQUE})

    model_instance = Tag()
    model_instance.title = title
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD)

    logging.info(Msg.END)

    return model_instance


def get(tag_title, db_session):
    logging.info(Msg.START + 'getting tag_title = {}'.format(tag_title))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(Tag).filter(
        Tag.title == tag_title).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {tag_title: Msg.INVALID_TAG})

    logging.info(Msg.END)

    return model_instance


def delete(tag_title, db_session, username):
    logging.info(
        Msg.START + 'user is {}  '.format(username) + 'tag_title= {}'.format(
            tag_title))
    if username != admin:
        logging.error(Msg.NOT_ACCESSED)
        raise Http_error(401, {'username': Msg.NOT_ACCESSED})

    logging.debug(Msg.DELETE_REQUEST + 'tag_title= {}'.format(tag_title))

    logging.debug(Msg.MODEL_GETTING)

    model_instance = db_session.query(Tag).filter(
        Tag.title == tag_title).first()
    if model_instance is None:
        logging.error(
            Msg.NOT_FOUND + ' tag by id = {}'.format(tag_title))
        raise Http_error(404, {tag_title: Msg.INVALID_TAG})

    db_session.query(Tag).filter(Tag.title == tag_title).delete()

    logging.debug(Msg.DELETE_SUCCESS)

    logging.info(Msg.END)

    return {}


def get_all(db_session):
    logging.info(Msg.START)
    try:
        logging.debug(Msg.GET_ALL_REQUEST + 'Tags...')
        result = db_session.query(Tag).all()

        logging.debug(Msg.GET_SUCCESS)

    except:

        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.info(Msg.END)

    return result


