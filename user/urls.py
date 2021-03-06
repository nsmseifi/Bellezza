from .controller import add, get, get_all, delete, edit, get_profile
from helper import check_auth, inject_db, jsonify, pass_data


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/users/<id>', 'GET', get, apply=wrappers)
    app.route('/users', 'GET', get_all, apply=wrappers)
    app.route('/users/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/users', 'POST', add, apply=[inject_db,jsonify,pass_data])
    app.route('/users/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/users/profile', 'GET', get_profile, apply=wrappers)
