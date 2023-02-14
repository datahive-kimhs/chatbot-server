class BaseError(Exception):
    """
    BaseClass(like interface) of Chatbot custom Exceptions.
    """
    pass


class ChatBotError(BaseError):
    """
    Error from Chatbot.
    """
    pass


class ChatRoomError(BaseError):
    """
    Error from ChatRoom.
    """
    pass


class DataBaseError(BaseError):
    """
    Error from Database.
    """
    pass


class CannotFoundData(DataBaseError):
    """
    Cannot found data in db.
    """
    pass


class TooManyFoundData(DataBaseError):
    """
    Too many found data in db.
    """
    pass


class IndexNotMatched(DataBaseError):
    """
    Not matched value and Primary key in db table.
    """
    pass



