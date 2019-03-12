from helper import check_auth, inject_db, jsonify, pass_data, if_login
from .controller import add, get, delete, edit, get_all, return_file, \
    get_user_posts, get_category_posts, get_tags_posts


def call_router(app):
    login_wrappers = [if_login, inject_db, jsonify]
    data_login_wrappers = (login_wrappers[:])
    data_login_wrappers.append(pass_data)
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/posts/<id>', 'GET', get, apply=login_wrappers)
    app.route('/posts/_search', 'POST', get_all, apply=data_login_wrappers)
    app.route('/posts/user', 'POST', get_user_posts, apply=data_login_wrappers)
    app.route('/posts/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/posts', 'POST', add, apply=data_plus_wrappers)
    app.route('/posts/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/serve-files/<filename>', 'GET', return_file, apply=[inject_db])
    app.route('/posts/category', 'POST', get_category_posts,
              apply=data_login_wrappers)

    app.route('/posts/tags', 'POST', get_tags_posts, apply=data_login_wrappers)
