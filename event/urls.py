from helper import check_auth, inject_db, jsonify, pass_data
from .controller import add, get_events, get_new_events, get_new_events_count


def call_router(app):
    wrappers = [check_auth, inject_db, jsonify]
    data_plus_wrappers = (wrappers[:])
    data_plus_wrappers.append(pass_data)

    app.route('/events/_search', 'POST', get_events, apply=data_plus_wrappers)
    app.route('/events', 'POST', add, apply=data_plus_wrappers)
    app.route('/events/_new', 'POST', get_new_events,apply=data_plus_wrappers)
    app.route('/events/_count', 'GET', get_new_events_count,apply=wrappers)

