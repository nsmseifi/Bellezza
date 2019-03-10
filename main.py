from bottle import run, request,Bottle

from send_message import send_message
from user.urls import  call_router as user_routes
from post.urls import call_router as post_routes
from app_token.urls import call_router as token_routes
from like.urls import call_router as like_routes
from comment.urls import call_router as comment_routes
from register.urls import call_router as register_routes
from category.urls import call_router as category_routes
from tag.urls import call_router as tag_routes


from helper import value

app_host = value('app_host','localhost')
app_port = value('app_port','8080')

if __name__ == '__main__':

    app = Bottle()

    user_routes(app)
    post_routes(app)
    token_routes(app)
    like_routes(app)
    comment_routes(app)
    register_routes(app)
    category_routes(app)
    tag_routes(app)

    run(host=app_host, port=app_port, debug=True, app=app)
    print(request.json)
