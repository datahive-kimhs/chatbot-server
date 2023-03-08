from typing import Any
import logging

from sqlalchemy import select, update, delete

from connection.ckline import get_ckline_db_engine
from models.answer import Answer


def sample_func_select() -> None:
    """
    This sample show how connect to DB
    and querying(SELECT) use orm module(sqlalchemy).
    :return: None
    """
    # query SELECT.
    ckline_db = get_ckline_db_engine()
    with ckline_db.get_db_session() as session:
        stmt = select(Answer).where(Answer.ner.like('%천경%'))
        rows = session.execute(stmt).all()
    for row in rows:
        print(f"{row.Answer.id}\t{row.Answer.answer}")
    """
    it's same that...

    session = ckline_db.get_db_session()
    stmt = select(Answer).where(Answer.ner.like('%천경%'))
    rows = session.execute(stmt).all()
    session.close()

    for row in rows:
        print(f"{row.Answer.idx}\t{row.Answer.answer}")
    """


def sample_func_transaction() -> None:
    """
    This sample show how connect to DB and
    do transaction(insert, update, delete) use orm module(sqlalchemy).
    :return: None
    """
    # insert, update, delete...
    # session.begin() == start transaction,
    # end of context(with clause) - implicit call commit(), exception - call rollback()
    try:
        ckline_db = get_ckline_db_engine()
        with ckline_db.get_db_session() as session, session.begin():
            # insert
            new_answer = Answer(answer="it is answer", ner="it is ner")
            session.add(new_answer)

            # update
            update_stmt = update(Answer). \
                where(Answer.idx == 999). \
                values(answer="it is answer", ner="it is ner"). \
                returning(Answer.idx)
            result = session.execute(update_stmt)
            print(result.IDX)

            # delete
            delete_stmt = delete(Answer). \
                where(Answer.idx == 999). \
                returning(Answer.idx)
            del_result = session.execute(delete_stmt)
            print(del_result.IDX)
    except Exception as e:
        logging.exception(e)
    """
    it's same that...

    try:
        session = ckline_db.get_db_session()
        session.begin()
        # do insert, update, delete...
        session.flush() # can skip
        # do insert, update, delete...
        session.flush() # can skip
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        # do exception handling...
    """
