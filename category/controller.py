import json
import logging
import os
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error, value
from .model import Category
from tag.controller import get as get_tag

save_path = os.environ.get('save_path')
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

    category = db_session.query(Category).filter(
        Category.title == title).first()
    if category:
        logging.error(Msg.NOT_UNIQUE + '  title already exists')
        raise Http_error(409, {'title': Msg.NOT_UNIQUE})

    model_instance = Category()
    model_instance.title = title
    model_instance.description = data.get('description')
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
            tag = get_tag(item, db_session)
            if item != tag.title:
                logging.error(Msg.INVALID_TAG)
                raise Http_error(404,{item:Msg.INVALID_TAG})

        model_instance.tags = tags

    if ('upload' not in data) or (data['upload'] is None):
        logging.error(Msg.DATA_MISSING + 'image is not uploaded')
        raise Http_error(400, {'upload': Msg.DATA_MISSING})

    if len(data['upload']) > 1:
        raise Http_error(400, {'upload': 'just 1 image can be uploaded'})

    upload = data['upload'][0]
    upload.filename = str(uuid4())
    model_instance.image = upload.filename
    print(upload.filename)

    upload.save(save_path)  # appends upload.filename automatically

    del (data['upload'])

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD)

    logging.info(Msg.END)

    return model_instance


def get(category_title, db_session):
    logging.info(Msg.START + 'getting category_title = {}'.format(category_title))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(Category).filter(
        Category.title == category_title).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {category_title: Msg.INVALID_CATEGORY})

    logging.info(Msg.END)

    return model_instance


def delete(category_title, db_session, username):
    logging.info(
        Msg.START + 'user is {}  '.format(username) + 'category_title= {}'.format(
            category_title))
    if username != admin:
        logging.error(Msg.NOT_ACCESSED)
        raise Http_error(401, {'username': Msg.NOT_ACCESSED})

    logging.debug(Msg.DELETE_REQUEST + 'category_title= {}'.format(category_title))

    logging.debug(Msg.MODEL_GETTING)

    model_instance = db_session.query(Category).filter(
        Category.title == category_title).first()
    if model_instance is None:
        logging.error(
            Msg.NOT_FOUND + ' category by title = {}'.format(category_title))
        raise Http_error(404, {'category': Msg.INVALID_CATEGORY})

    db_session.query(Category).filter(Category.title == category_title).delete()

    logging.debug(Msg.DELETE_SUCCESS)

    logging.info(Msg.END)

    return {}


def get_all(db_session):
    logging.info(Msg.START)
    try:
        logging.debug(Msg.GET_ALL_REQUEST + 'Categorys...')
        result = db_session.query(Category).all()

        logging.debug(Msg.GET_SUCCESS)

    except:

        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.info(Msg.END)

    return result


def edit(category_title, data, db_session, username):
    logging.debug(Msg.EDIT_REQUST)
    logging.info(Msg.START + ' user is {}'.format(username))
    if username != admin:
        logging.error(Msg.NOT_ACCESSED)
        raise Http_error(401, {'username': Msg.NOT_ACCESSED})

    model_instance = get(category_title, db_session)
    if model_instance:
        logging.debug(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {category_title: Msg.NOT_FOUND})

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
            tag = get_tag(item, db_session)
            if item != tag.title:
                logging.error(Msg.INVALID_TAG)
                raise Http_error(404, {item: Msg.INVALID_TAG})

        model_instance.tags = tags
        del data['tags']

    if "upload" in data.keys():
        upload = data['upload'][0]
        upload.filename = str(uuid4())
        model_instance.image = upload.filename
        upload.save(save_path)  # appends upload.filename automatically
        del (data['upload'])

    if 'id' in data.keys():
        del data['id']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
        model_instance.modification_date = Now()
        model_instance.modifier = username

    logging.debug(Msg.EDIT_SUCCESS + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance
