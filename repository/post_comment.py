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


    comment = model_to_dict(last_comment)

    if last_comment:
        comment_creator = db_session.query(User).filter(
            User.username == last_comment.creator).first()
        comment['creator'] = model_to_dict(comment_creator)

        logging.info(('post_id = {} , last_comment is : {}').format(post_id,
                                                      last_comment.message))

    return comment
