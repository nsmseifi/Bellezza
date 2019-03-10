from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, edit, get_all


def call_router(app):
    wrappers = [ inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)
    data_plus_wrappers.append(check_auth)

    app.route('/comments/<id>', 'GET', get, apply=wrappers)
    app.route('/comments/_search', 'POST', get_all, apply=[inject_db,jsonify,
                                                           pass_data])
    app.route('/comments/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/comments', 'POST', add, apply=data_plus_wrappers)
    app.route('/comments/<id>', 'PUT', edit, apply=data_plus_wrappers)
