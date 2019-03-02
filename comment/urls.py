from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, edit, get_all


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/comments/<id>', 'GET', get, apply=wrappers)
    app.route('/comments/<post_id>', 'POST', get_all, apply=data_plus_wrappers)
    app.route('/comments/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/comments', 'POST', add, apply=data_plus_wrappers)
    app.route('/comments/<id>', 'PUT', edit, apply=data_plus_wrappers)
