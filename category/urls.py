from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, get_all, edit


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/categories/<category_title>', 'GET', get, apply=[inject_db, jsonify])
    app.route('/categories/<category_title>', 'DELETE', delete, apply=[check_auth,
                                                             inject_db])
    app.route('/categories', 'POST', add, apply=data_plus_wrappers)
    app.route('/categories/_search', 'POST', get_all, apply=[inject_db,
                                                             jsonify])
    app.route('/categories/<category_title>', 'PUT', edit, apply=data_plus_wrappers)


