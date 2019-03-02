import json
import logging
from uuid import uuid4

from sqlalchemy import and_

from log import Msg
from helper import Now, model_to_dict, Http_error
from post.model import Post
from .model import Comment


def add(db_session, data, username):
    logging.info(Msg.START + json.dumps(data))

    post = db_session.query(Post).filter(Post.id == data.get('post_id')).first()
    if post is None:
        logging.error(Msg.PARENT_INVALID + 'relative post doesnt exist')
        raise Http_error(404, Msg.PARENT_INVALID)

    model_instance = Comment()
    model_instance.id = str(uuid4())
    model_instance.message = data.get('message')
    model_instance.post_id = data.get('post_id')
    model_instance.creation_date = Now()
    model_instance.creator = username

    logging.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)
    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(
        username) + "getting user_id = {}".format(id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(Comment).filter(Comment.id == id).first()
    if model_instance:
        logging.debug(
            Msg.GET_SUCCESS + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    logging.error(Msg.GET_FAILED + json.dumps({"id": id}))

    logging.info(Msg.END)

    return model_instance


def delete(id, db_session, username):
    logging.info(
        Msg.START + "user is {}  ".format(username) + "comment_id= {}".format(
            id))
    logging.debug(Msg.DELETE_REQUEST + "comment_id= {}".format(id))

    comment = db_session.query(Comment).filter(Comment.id == id).first()

    if comment is None:
        logging.error(Msg.DELETE_FAILED + Msg.NOT_FOUND)
        raise Http_error(404, Msg.NOT_FOUND)

    if comment.creator != username:
        logging.error(Msg.ALTERING_AUTHORITY_FAILED)
        raise (403, Msg.ALTERING_AUTHORITY_FAILED)

    db_session.query(Comment).filter(Comment.id == id).delete()

    logging.debug(Msg.DELETE_SUCCESS)

    logging.info(Msg.END)

    return {}


def get_all(post_id, data, db_session, username):
    logging.info(Msg.START + "user is {}".format(username))

    logging.debug(Msg.GET_ALL_REQUEST + "Comments...")

    post = db_session.query(Post).filter(Post.id == post_id).first()
    if post is None:
        logging.error(Msg.PARENT_INVALID)
        raise Http_error(404, Msg.PARENT_INVALID)

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count_number') is None:
        data['count_number'] = 20

    result = db_session.query(Comment).filter(and_(Comment.post_id == post_id,
                                                   Comment.creation_date < data.get(
                                                       'time'))).order_by(
        Comment.creation_date.desc()).limit(data.get('count_number')).all()

    logging.debug(Msg.GET_SUCCESS)

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

    if model_instance.creator != username:
        logging.error(Msg.ALTERING_AUTHORITY_FAILED)
        raise (403, Msg.ALTERING_AUTHORITY_FAILED)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
        model_instance.modification_date = Now()
        model_instance.modifier = username

    logging.debug(Msg.MODEL_ALTERED)

    logging.debug(Msg.EDIT_SUCCESS + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)

    return model_instance
