from typing import Any
import logging

from sqlalchemy import select, update, delete

from core import ckline_db
from models.answer import Answer


def make_answer(question: Any) -> Any:
    """
    if use DB, reference core.chatbot_sample.py
    :param question: message(data) from client.
    :return: message(data) to be sent client from server.
    """
    return "hello"
