from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, edit, get_all, return_file, \
    get_user_posts


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/posts/<id>', 'GET', get, apply=wrappers)
    app.route('/posts', 'GET', get_all, apply=wrappers)
    app.route('/posts/user', 'GET', get_user_posts, apply=wrappers)
    app.route('/posts/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/posts', 'POST', add, apply=data_plus_wrappers)
    app.route('/posts/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/serve-files/<filename>', 'GET', return_file,
              apply=[check_auth, inject_db])
