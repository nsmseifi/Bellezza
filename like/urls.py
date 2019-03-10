from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/likes/_search', 'POST', get, apply=[inject_db,jsonify,pass_data])
    app.route('/likes/<post_id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/likes', 'POST', add, apply=data_plus_wrappers)
