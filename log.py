import logging

formatter = logging.Formatter(
    '[%(asctime)s] p%(process)s {%(pathname)s %(filename)s:%(lineno)d} %(levelname)s - %(message)s', '%m-%d %H:%M:%S')

logging.basicConfig(
    filename='debug.log',
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s :%(lineno)d - %(funcName)5s()] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class Msg:
    START = "function is called--"
    END = "function finished successfully--"
    ADDING_ERR = "adding model to database encountered a problem  "
    Q_TYPE_ADDITION = "question type added to model  "
    Q_ADDITION = "question  added to model  "
    ANSWER_ADDITION = "answer added to model  "
    CREATOR_ADDITION = "creator added to model  "
    DATETIME_ADDITION = "date time added to model  "
    DURATION_ADDITION = "duration added to model  "
    DATA_ADDITION = "data added to model  "
    DB_ADD = "model added to database  "
    AUTH_CHECKING = "going to check authentication  "
    AUTH_SUCCEED = "authentication is successful  "
    GET_SUCCESS = "getting from database is successful  "
    GET_FAILED = "getting from database failed  "
    DELETE_SUCCESS = "deleting item is done successfully  "
    DELETE_FAILED = "deleting the item encountered a problem  "
    DELETE_REQUEST = "request for deleting item..."
    EDIT_REQUST = "editing the item..."
    EDIT_SUCCESS = "editing item is done successfully  "
    EDIT_FAILED = "editing the item encountered a problem  "
    MODEL_GETTING = "model_instance got from database successfully  "
    MODEL_GETTING_FAILED = "item is not exists in database  "
    MODEL_ALTERED = "item altered successfully  "
    GET_ALL_REQUEST = "getting all request from db..."
    NOT_FOUND = "no such item exists "
    COMMIT_FAILED = 'commiting process failed'
    TOKEN_CREATED = 'a new token for user created'
    TOKEN_EXPIRED = 'token is expired'
    TOKEN_DELETED = 'token deleted successfuly'
    TOKEN_INVALID = 'token is invalid'
    ALTERING_AUTHORITY_FAILED = 'user has no admission to alter the item'
    DELETE_PROCESSING = 'going to delete the item from db'
    GATHERING_RELATIVES = 'gathering item reletives to delete them from db'
    DELETE_RELATIVE = 'the reletive {} is going to be delete'
    UPLOAD_NOT_ALLOWED = 'no more uploads supports in edit'
    POST_ALREADY_LIKED = 'user liked the post before'
    POST_NOT_FOUND = 'no such post found'
    UNLIKED_POST = 'post {} is unliked by {} '
    USER_XISTS = 'user by this username ={} already exists'
    PARENT_INVALID = 'parent entity doesnt exist'



def logger(mood, message, func_name, func_path=None):
    if mood == "info":
        logging.info(message, func_name, func_path)
