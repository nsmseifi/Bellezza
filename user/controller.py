import json
import logging
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error
from .model import User


def add(db_session, data, username):
    logging.info(Msg.START )
    user = db_session.query(User).filter(User.username == data.get(
        'username')).first()
    if user:
        raise Http_error(403, Msg.USER_XISTS.format(data.get('username')))

    model_instance = User()
    model_instance.username = data.get('username')
    model_instance.password = data.get('password')
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username

    logging.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START
                 + "user is {}  ".format(username)
                 + "getting user_id = {}".format(id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(User).filter(User.id == id).first()
    if model_instance:
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(username)
                 + "user_id= {}".format(id))
    try:
        logging.debug(Msg.DELETE_REQUEST +
                      "user_id= {}".format(id))

        db_session.query(User).filter(User.id == id).delete()

        logging.debug(Msg.DELETE_SUCCESS)

    except:

        logging.error(Msg.DELETE_FAILED +
                      "user_id= {}".format(id))
        raise Http_error(500, Msg.DELETE_FAILED)

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
        raise Http_error(404, Msg.NOT_FOUND)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
        model_instance.modification_date = Now()
        model_instance.modifier = username

    logging.debug(Msg.MODEL_ALTERED)

    # db_session.add(model_instance)

    logging.debug(Msg.EDIT_SUCCESS +
                  json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance
