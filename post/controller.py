import json
import os
from uuid import uuid4
import logging

from bottle import static_file, response

from log import Msg
from helper import Now, model_to_dict, Http_error, file_mime_type
from repository.post_like import delete_post_likes
from repository.post_comment import delete_post_comments
from .model import Post

save_path = os.environ.get('save_path')


def add(db_session, data, username):
    logging.info(Msg.START)

    model_instance = Post()
    model_instance.id = str(uuid4())
    model_instance.title = data.get('title')
    model_instance.body = data.get('body')
    model_instance.likes = 0
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.pictures_id = []

    # logging.debug(Msg.DATA_ADDITION+"  || Data :"+json.dumps(data))
    if ('upload' not in data) or (data['upload'] is None):
        data['upload'] = []

    for item in data['upload']:
        upload = item
        # name, ext = os.path.splitext(upload.filename)
        upload.filename = str(uuid4())
        (model_instance.pictures_id).append(upload.filename)
        print(upload.filename)
        # if ext not in ('.png', '.jpg', '.jpeg'):
        #     return 'File extension not allowed.'

        upload.save(save_path)  # appends upload.filename automatically
    del (data['upload'])

    logging.debug(Msg.DATA_ADDITION + "  || Data :" + json.dumps(data))

    db_session.add(model_instance)

    logging.debug(Msg.DB_ADD)

    logging.info(Msg.END)

    return model_instance


def get(id, db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    model_instance = db_session.query(Post).filter(Post.id == id).first()
    if model_instance:
        logging.info(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    logging.debug(Msg.GET_SUCCESS)

    logging.info(Msg.END)
    return model_instance


def delete(id, db_session, username):
    logging.info(
        Msg.START + "user is {}  ".format(username) + "post_id = {}".format(id))
    logging.info(Msg.DELETE_REQUEST + "user is {}".format(username))

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(Msg.MODEL_GETTING)
    else:
        logging.error(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    if username != model_instance.creator:
        logging.error(Msg.ALTERING_AUTHORITY_FAILED)
        raise Http_error(403, Msg.ALTERING_AUTHORITY_FAILED)

    logging.debug(Msg.DELETE_PROCESSING + 'post-id = {}'.format(id))

    post = db_session.query(Post).filter(Post.id == id).first()
    if post.pictures_id:
        for filename in post.pictures_id:
            file_path = save_path + '/' + filename
            os.remove(file_path)
        logging.debug('related files of post_id = {} deleted'.format(id))

    delete_post_likes(id, db_session, username)
    logging.debug('related likes for post_id = {} deleted'.format(id))

    delete_post_comments(id, db_session, username)
    logging.debug('related comments for post_id = {} deleted'.format(id))

    db_session.query(Post).filter(Post.id == id).delete()

    logging.debug(Msg.DELETE_SUCCESS + "Post.id {}".format(id))

    logging.info(Msg.END)
    return {}


def get_all(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        result = db_session.query(Post).order_by(
            Post.creation_date.desc()).all()
        logging.debug(Msg.GET_SUCCESS)
    except:
        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.debug(Msg.END)
    return result


def get_user_posts(db_session, username):
    logging.info(Msg.START + "user is {}".format(username))
    try:
        result = db_session.query(Post).filter(
            Post.creator == username).order_by(Post.creation_date.desc()).all()
        logging.debug(Msg.GET_SUCCESS)
    except:
        logging.error(Msg.GET_FAILED)
        raise Http_error(500, Msg.GET_FAILED)

    logging.debug(Msg.END)
    return result


def edit(id, db_session, data, username):
    logging.info(
        Msg.START + "user is {}  ".format(username) + "post_id = {}".format(id))

    if "id" in data.keys():
        del data["id"]
    if "upload" in data.keys():
        logging.debug(Msg.UPLOAD_NOT_ALLOWED + " post_id = {}".format(id))
        raise Http_error(400, Msg.UPLOAD_NOT_ALLOWED)

    model_instance = get(id, db_session, username)
    if model_instance:
        logging.debug(
            Msg.MODEL_GETTING + json.dumps(model_to_dict(model_instance)))
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED + json.dumps(data))
        raise Http_error(404, Msg.NOT_FOUND)

    if username != model_instance.creator:
        logging.error(Msg.ALTERING_AUTHORITY_FAILED)
        raise Http_error(403, Msg.ALTERING_AUTHORITY_FAILED)

    for key, value in data.items():
        # TODO  if key is valid attribute of class
        setattr(model_instance, key, value)
        model_instance.modification_date = Now()
        model_instance.modifier = username

    logging.debug(Msg.MODEL_ALTERED)
    logging.debug(Msg.DB_ADD + json.dumps(model_to_dict(model_instance)))
    logging.info(Msg.END)

    return model_instance


def return_file(filename, **kwargs):
    response.body = static_file(filename, root=save_path)
    file_path = save_path + '/' + filename
    response.content_type = file_mime_type(file_path)
    return response
