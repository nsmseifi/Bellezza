import logging

from comment.model import Comment
from helper import model_to_dict
from user.model import User


def delete_post_comments(post_id, db_session, username):
    db_session.query(Comment).filter(Comment.post_id == post_id).delete()
    return {"result": True}


def post_last_comment(post_id, db_session):
    last_comment = db_session.query(Comment).filter(
        Comment.post_id == post_id).order_by(
        Comment.creation_date.desc()).first()
    if last_comment:
        comment_creator = db_session.query(User.name).filter(
            User.username == last_comment.creator).first()

        logging.info(('post_id = {} , last_comment is : {} ,'
                      'comment_creator is {}').format(post_id,
                                                      last_comment.message,
                                                      comment_creator))

        return {"last_comment": model_to_dict(last_comment),
                "comment_creator": comment_creator}

    else:
        return {"last_comment": None,
                "comment_creator": None}

