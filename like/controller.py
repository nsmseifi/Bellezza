import json
import logging
from uuid import uuid4

from log import Msg
from helper import Now, model_to_dict, Http_error
from .model import Like
from post.model import Post


def add(db_session, data, username):
    logging.info(Msg.START + json.dumps(data))
    post = db_session.query(Post).filter(Post.id == data.get('post_id')).first()

    if post is None:
        logging.error(Msg.POST_ALREADY_LIKED + json.dumps(data))
        raise Http_error(404, Msg.POST_NOT_FOUND)

    instance = db_session.query(Like).filter(Like.post_id == data.get(
        'post_id')).filter( Like.creator == username).first()
    if instance is not None:
        logging.error(Msg.POST_ALREADY_LIKED)
        raise Http_error(409, Msg.POST_ALREADY_LIKED)

    model_instance = Like()

    model_instance.post_id = data.get('post_id')
    model_instance.id = str(uuid4())
    model_instance.creation_date = Now()
    model_instance.creator = username

    logging.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    post.likes += 1

    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))

    logging.info(Msg.END)
    return model_instance


def get(post_id, db_session, username):
    logging.info(Msg.START
                 + "user is {}  ".format(username)
                 + "getting like for post_id = {}".format(post_id))
    logging.debug(Msg.MODEL_GETTING)
    model_instance = db_session.query(Like).filter(Like.post_id == post_id).first()
    if model_instance:
        logging.debug(Msg.GET_SUCCESS +
                      json.dumps(model_to_dict(model_instance)))
    else:
        logging.error(Msg.GET_FAILED + json.dumps({"post_id": post_id}))
        raise Http_error(404, Msg.NOT_FOUND)

    logging.info(Msg.END)

    return model_instance


def delete(post_id, db_session, username):
    logging.info(Msg.START + "user is {}  ".format(username)
                 + "delete like for post_id= {}".format(post_id))
    logging.debug(Msg.DELETE_REQUEST +
                  "like of post_id= {}".format(post_id))
    like = db_session.query(Like).filter(Like.post_id == post_id).filter(
        Like.creator == username).first()
    if like is None:
        logging.error(Msg.NOT_FOUND + ' post is not liked by user yet')
        raise Http_error(404, Msg.NOT_FOUND)

    # if like.creator != username:
    #     logging.error(Msg.ALTERING_AUTHORITY_FAILED)
    #     raise Http_error(403, Msg.ALTERING_AUTHORITY_FAILED)

    # db_session.query(Like).filter(Like.post_id == post_id).filter(
    #     Like.creator == username).delete()
    db_session.like.delete()
    post = db_session.query(Post).filter(Post.id == post_id).first()

    post.likes -= 1
    logging.debug(Msg.UNLIKED_POST.format(post_id, username))

    logging.debug(Msg.DELETE_SUCCESS)
    logging.info(Msg.END)

    return {}
