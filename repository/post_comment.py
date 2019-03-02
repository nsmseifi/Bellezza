from comment.model import Comment


def delete_post_comments(post_id, db_session, username):
    db_session.query(Comment).filter(Comment.post_id == post_id).delete()
    return {"result":True}