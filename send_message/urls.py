from helper import check_auth, inject_db, jsonify, pass_data
from .send_message import send_message


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify,pass_data]


    app.route('/send-message', 'POST', send_message, apply=wrappers)
