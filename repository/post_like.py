from like.model import Like


def delete_post_likes(post_id,db_session,username):
    db_session.query(Like).filter(Like.post_id == post_id).delete()
    return {"result":True}