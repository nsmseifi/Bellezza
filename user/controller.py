import json
import logging
import os
from uuid import uuid4

from sqlalchemy import and_

from log import Msg
from helper import Now, model_to_dict, Http_error, check_schema
from .model import User
from app_redis import app_redis as redis

save_path = os.environ.get('save_path')

def add(db_session, data):
    logging.info(Msg.START)
    required = ['cell_no','name','activation_code','password']
    check_schema(required,data.keys())

    cell_no = data.get('cell_no')
    name = data.get('name')
    user = db_session.query(User).filter(User.username == cell_no).first()
    if user:
        logging.error(Msg.USER_XISTS.format(cell_no))
        raise Http_error(409, {"cell_no": Msg.USER_XISTS.format(cell_no)})

    logging.debug(Msg.CHECK_REDIS_FOR_EXISTANCE)

    activation_code = redis.get(cell_no)
    if activation_code is None:
        logging.error(Msg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404,
                         {"activation_code": Msg.REGISTER_KEY_DOESNT_EXIST})

    activation_code = activation_code.decode("utf-8")
    if activation_code != data.get('activation_code'):
        logging.error(Msg.REGISTER_KEY_INVALID)
        raise Http_error(400, {"activation_code": Msg.REGISTER_KEY_INVALID})

    user_by_name = db_session.query(User).filter(User.name == name).first()
    if user_by_name != None:
        logging.error(Msg.NAME_NOT_UNIQUE)
        raise Http_error(409, {"name": Msg.NAME_NOT_UNIQUE})

    logging.debug(Msg.USR_ADDING)

    model_instance = User()
    model_instance.username = cell_no
    model_instance.password = data.get('password')
    model_instance.name = name
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = data.get('cell_no')
    model_instance.bio = data.get('bio')

    if ('upload' not in data) or (data['upload'] is None):
        data['upload'] = []

    upload = data['upload'][0]
    name, ext = os.path.splitext(upload.filename)

    upload.filename = str(uuid4())
    model_instance.avatar = upload.filename

    if ext not in ('.png', '.jpg', '.jpeg'):
        raise Http_error(400, {'avatar': 'File type not allowed.'})

    upload.save(save_path)  # appends upload.filename automatically

    del (data['upload'])

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
        model_instance.tags = tags

    logging.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(
        username) + "getting user_id = {}".format(id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": Msg.NOT_FOUND})

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return model_instance


def get_profile(username, db_session):
    logging.info(Msg.START + "user is {}  ".format(username))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(
        User.username == username).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"user": Msg.NOT_FOUND})

    logging.info(Msg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(
        Msg.START + "user is {}  ".format(username) + "user_id= {}".format(id))
    logging.debug(Msg.DELETE_REQUEST + "user_id= {}".format(id))

    user = db_session.query(User).filter(User.id == username).first()
    if user is None:
        logging.error(Msg.NOT_FOUND + ' user by username = {}'.format(username))
        raise Http_error(404, {'username': Msg.NOT_FOUND})

    db_session.query(User).filter(User.id == id).delete()

    logging.debug(Msg.DELETE_SUCCESS)

    if user.avatar:
        file_path = save_path + '/' + user.avatar
        os.remove(file_path)

    logging.info(Msg.END)

    return {}


def get_all(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        logging.debug(Msg.GET_ALL_REQUEST + "Users...")
        result = db_session.query(User).all()

        logging.debug(Msg.GET_SUCCESS)

    except:

        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.info(Msg.END)

    return result


def edit(id, db_session, data, username):
    logging.info(Msg.START + " user is {}".format(username))
    if "id" in data.keys():
        del data["id"]

    logging.debug(Msg.EDIT_REQUST)

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, {"id": Msg.NOT_FOUND})

    if model_instance.username != username:
        raise Http_error(403,{'user':Msg.ALTERING_AUTHORITY_FAILED})

    if ('upload' not in data) or (data['upload'] is None):
        data['upload'] = []

    upload = data['upload'][0]
    name, ext = os.path.splitext(upload.filename)

    upload.filename = str(uuid4())
    model_instance.avatar = upload.filename

    if ext not in ('.png', '.jpg', '.jpeg'):
        raise Http_error(400, {'avatar': 'File type not allowed.'})

    upload.save(save_path)  # appends upload.filename automatically

    del (data['upload'])

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
        model_instance.tags = tags

        del data['tags']

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
    model_instance.modification_date = Now()
    model_instance.modifier = username

    logging.debug(Msg.MODEL_ALTERED)

    # db_session.add(model_instance)

    logging.debug(Msg.EDIT_SUCCESS + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance


def get_by_tag(data, db_session, username=None):
    logging.info(Msg.START)

    required = ['tags', 'scroll']
    check_schema(required, data.keys())

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count') is None:
        data['count'] = 50

    tags = data.get('tags')

    if data['scroll'] == 'down':
        result = db_session.query(User).filter(and_(User.tags.op('@>')(tags),
                                                    User.creation_date < data.get(
                                                        'time'))).order_by(
            User.creation_date.desc()).limit(data.get('count')).all()
    else:
        result = db_session.query(User).filter(and_(User.tags.op('@>')(tags),
                                                    User.creation_date > data.get(
                                                        'time'))).order_by(
            User.creation_date.desc()).limit(data.get('count')).all()

    if result is None:
        logging.error(Msg.NOT_FOUND)
        raise Http_error(400, {'post': Msg.NOT_FOUND})


    logging.debug(Msg.GET_SUCCESS)

    logging.debug(Msg.END)
    return result
