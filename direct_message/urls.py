from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get, delete, edit, get_messages_by_recipient, \
    get_new_messages, set_message_as_seen, get_new_messages_count


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/direct-messages/<direct_id>', 'GET', get, apply=wrappers)
    app.route('/direct-messages/<direct_id>', 'DELETE', delete,
              apply=[check_auth, inject_db])
    app.route('/direct-messages', 'POST', add, apply=data_plus_wrappers)
    app.route('/direct-messages/<direct_id>', 'PUT', edit,
              apply=data_plus_wrappers)
    app.route('/direct-messages/_search', 'POST', get_messages_by_recipient,
              apply=data_plus_wrappers)
    app.route('/direct-messages/<direct_id>', 'PATCH', set_message_as_seen,
              apply=wrappers)
    app.route('/direct-messages/_new', 'POST', get_new_messages,
              apply=data_plus_wrappers)
    app.route('/direct-messages/_count', 'GET', get_new_messages_count,
              apply=wrappers)

