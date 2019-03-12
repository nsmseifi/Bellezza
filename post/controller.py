import json
import os
from uuid import uuid4
import logging

from bottle import static_file, response
from sqlalchemy import func, and_
from sqlalchemy.dialects.postgresql import Any

from like.controller import liked_by_user
from log import Msg
from tag.controller import get as get_tag
from category.controller import get as get_category
from helper import Now, model_to_dict, Http_error, file_mime_type
from repository.post_like import delete_post_likes
from repository.post_comment import delete_post_comments, post_last_comment
from user.controller import get_profile
from .model import Post

save_path = os.environ.get('save_path')


def add(db_session, data, username):
    logging.info(Msg.START)

    if data.get('category') is None:
        logging.error(Msg.DATA_MISSING + ' category is not in data')
        raise Http_error(400, {'category': Msg.DATA_MISSING})

    model_instance = Post()
    model_instance.id = str(uuid4())
    model_instance.title = data.get('title')
    model_instance.body = data.get('body')
    model_instance.likes = 0
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.pictures_id = []

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
            tag = get_tag(item, db_session)
            if item != tag.title:
                logging.error(Msg.INVALID_TAG)
                raise Http_error(404, {item: Msg.INVALID_TAG})

        model_instance.tags = tags

    categories = (data.get('category')).split(',')
    for item in categories:
        item.strip()
        category = get_category(item, db_session)
        if item != category.title:
            logging.error(Msg.INVALID_TAG)
            raise Http_error(404, {item: Msg.INVALID_CATEGORY})

    model_instance.category = categories


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


def get(id, db_session, username = None):
    model_instance = db_session.query(Post).filter(Post.id == id).first()
    if model_instance:
        logging.info(Msg.MODEL_GETTING)
    else:
        logging.debug(Msg.MODEL_GETTING_FAILED)
        raise Http_error(404, Msg.NOT_FOUND)

    logging.debug(Msg.GET_SUCCESS)

    post = model_to_dict(model_instance)
    post.update(post_last_comment(id, db_session))

    logging.info(Msg.END)
    return post


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


def get_all(data,db_session, username=None):

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count') is None:
        data['count'] = 50
    if data.get('scroll') is None:
        logging.error(Msg.SCROLL_UNDEFINED)
        raise Http_error(400,{'scroll': Msg.SCROLL_UNDEFINED})

    if data['scroll'] == 'down':
        result = db_session.query(Post).filter(Post.creation_date < data.get(
                                                           'time')).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()
    else:
        result = db_session.query(Post).filter(
            Post.creation_date > data.get('time')).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()

    final_result = []
    if result is None:
        logging.error(Msg.NOT_FOUND)
        raise Http_error(400, {'post': Msg.NOT_FOUND})

    for item in result:
        post = model_to_dict(item)
        if username is None:
            post['user_liked'] = False
        else:
            liked = liked_by_user(item.id,username,db_session)
            if liked :
                post['user_liked'] = True
        post_user = get_profile(item.creator, db_session)
        creator = model_to_dict(post_user)
        del creator['password']


        post['creator'] = creator
        post['last_comment'] = post_last_comment(post['id'],db_session)
        final_result.append(post)

    logging.debug(Msg.GET_SUCCESS)

    logging.debug(Msg.END)
    return final_result


def get_user_posts(data, db_session, username=None):

    logging.info(Msg.START )
    # result = db_session.query(Post).filter(Post.creator == username).order_by(
    #     Post.creation_date.desc()).all()

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count') is None:
        data['count'] = 50
    if data.get('scroll') is None:
        logging.error(Msg.SCROLL_UNDEFINED)
        raise Http_error(400,{'scroll': Msg.SCROLL_UNDEFINED})

    if data.get('creator') is None:
        logging.error(Msg.DATA_MISSING + 'creator is required')
        raise Http_error((400,{'creator':Msg.DATA_MISSING}))

    if data['scroll'] == 'down':
        result = db_session.query(Post).filter(and_(
            Post.creator== data.get('creator'),Post.creation_date <
                                                    data.get(
                                                           'time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()
    else:
        result = db_session.query(Post).filter(and_(Post.creator == username,
                                                    Post.creation_date >
                                                    data.get(
                                                        'time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()

    final_result = []
    if result is None:
        logging.error(Msg.NOT_FOUND)
        raise Http_error(400, {'post': Msg.NOT_FOUND})

    for item in result:
        post = model_to_dict(item)
        if username is None:
            post['user_liked'] = False
        else:
            liked = liked_by_user(item.id,username,db_session)
            if liked :
                post['user_liked'] = True

        post_user = get_profile(item.creator,db_session)
        creator = model_to_dict(post_user)
        del creator['password']

        post['creator'] = creator

        post['last_comment'] = post_last_comment(post['id'],db_session)
        final_result.append(post)

    logging.debug(Msg.GET_SUCCESS)

    logging.debug(Msg.END)
    return final_result


def get_category_posts(data, db_session, username=None):
    logging.info(Msg.START)

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count') is None:
        data['count'] = 50
    category = []
    if data.get('category'):
        category = data['category']
    if data.get('scroll') is None:
        logging.error(Msg.SCROLL_UNDEFINED)
        raise Http_error(400,{'scroll': Msg.SCROLL_UNDEFINED})

    if data['scroll'] == 'down':
        result = db_session.query(Post).filter(
            and_(Post.category.op('@>')(category),
                Post.creation_date < data.get('time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()
    else:
        result = db_session.query(Post).filter(
            and_(Post.category.op('@>')(category),
                 Post.creation_date > data.get('time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()

    final_result = []
    if result is None:
        logging.error(Msg.NOT_FOUND)
        raise Http_error(400, {'post': Msg.NOT_FOUND})

    for item in result:
        post = model_to_dict(item)
        if username is None:
            post['user_liked'] = False
        else:
            liked = liked_by_user(item.id,username,db_session)
            if liked :
                post['user_liked'] = True

        post_user = get_profile(item.creator, db_session)
        creator = model_to_dict(post_user)
        del creator['password']

        post['creator'] = creator
        post['last_comment'] = post_last_comment(post['id'],db_session)
        final_result.append(post)


    logging.debug(Msg.GET_SUCCESS)

    logging.debug(Msg.END)
    return final_result


def get_tags_posts(data, db_session, username = None):
    logging.info(Msg.START)
    tags = data.get('tags') or []

    if data.get('time') is None:
        data['time'] = Now()
    if data.get('count') is None:
        data['count'] = 50
    if data.get('scroll') is None:
        logging.error(Msg.SCROLL_UNDEFINED)
        raise Http_error(400,{'scroll': Msg.SCROLL_UNDEFINED})
    if data['scroll'] == 'down':
        result = db_session.query(Post).filter(
            and_(Post.tags.op('@>')(tags),
                Post.creation_date < data.get('time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()
    else:
        result = db_session.query(Post).filter(and_(Post.tags.op('@>')(tags),
                                                    Post.creation_date >
                                                    data.get(
                                                        'time'))).order_by(
            Post.creation_date.desc()).limit(data.get('count')).all()

    final_result = []
    if result is None:
        logging.error(Msg.NOT_FOUND)
        raise Http_error(400, {'post': Msg.NOT_FOUND})

    for item in result:
        post = model_to_dict(item)
        if username is None:
            post['user_liked'] = False
        else:
            liked = liked_by_user(item.id,username,db_session)
            if liked :
                post['user_liked'] = True

        post_user = get_profile(item.creator, db_session)
        creator = model_to_dict(post_user)
        del creator['password']

        post['creator'] = creator
        post['last_comment'] = post_last_comment(post['id'],db_session)
        final_result.append(post)


    logging.debug(Msg.GET_SUCCESS)

    logging.debug(Msg.END)
    return final_result


def edit(id, db_session, data, username):
    logging.info(
        Msg.START + "user is {}  ".format(username) + "post_id = {}".format(id))
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

    if data.get('category') is None:
        logging.error(Msg.DATA_MISSING + ' category is not in data')
        raise Http_error(400, {'category': Msg.DATA_MISSING})

    if "id" in data.keys():
        del data["id"]

    if data.get('tags') is not None:
        tags = (data.get('tags')).split(',')
        for item in tags:
            item.strip()
            tag = get_tag(item, db_session)
            if item != tag.title:
                logging.error(Msg.INVALID_TAG)
                raise Http_error(404, {item: Msg.INVALID_TAG})

        model_instance.tags = tags

    categories = (data.get('category')).split(',')
    for item in categories:
        item.strip()
        category = get_category(item, db_session)
        if item != category.title:
            logging.error(Msg.INVALID_TAG)
            raise Http_error(404, {item: Msg.INVALID_CATEGORY})

    model_instance.category = categories
    del (data['category'])
    del (data['tags'])

    if "upload" in data.keys():
        logging.debug(Msg.UPLOAD_NOT_ALLOWED + " post_id = {}".format(id))
        raise Http_error(400, Msg.UPLOAD_NOT_ALLOWED)

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
