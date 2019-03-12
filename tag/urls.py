from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, get_all

def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/tags/<tag_title>', 'GET', get, apply=[inject_db, jsonify])
    app.route('/tags/<tag_title>', 'DELETE', delete, apply=[check_auth,
                                                             inject_db])
    app.route('/tags', 'POST', add, apply=data_plus_wrappers)
    app.route('/tags/_search', 'POST', get_all, apply=[inject_db,
                                                             jsonify])


