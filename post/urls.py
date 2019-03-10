from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, edit, get_all, return_file, \
    get_user_posts, get_category_posts, get_tags_posts


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/posts/<id>', 'GET', get, apply=[inject_db, jsonify])
    app.route('/posts/_search', 'POST', get_all, apply=[inject_db, jsonify,
                                                        pass_data])
    app.route('/posts/user/<username>', 'GET', get_user_posts,
              apply=[inject_db, jsonify])
    app.route('/posts/<id>', 'DELETE', delete, apply=[check_auth, inject_db])
    app.route('/posts', 'POST', add, apply=data_plus_wrappers)
    app.route('/posts/<id>', 'PUT', edit, apply=data_plus_wrappers)
    app.route('/serve-files/<filename>', 'GET', return_file, apply=[inject_db])
    app.route('/posts/category/<category_id>', 'GET', get_category_posts,
              apply=[inject_db, jsonify])

    app.route('/posts/tags', 'POST', get_tags_posts,
              apply=[inject_db, jsonify, pass_data])
