import openpyxl
import pandas as pd
import csv

from typing import Any
import logging

from sqlalchemy import select, update, delete

from core import ckline_db
from models.dictionary_ja import Dictionaryja
from models.scenario_ja import Scenarioja
from models.user_dict_ja import Userdictja

def train_user_dict_ja():
    try:
        with ckline_db.get_db_session() as session:
            stmt = select(Userdictja)
            rows = session.execute(stmt).all()

            with open("utils/user_dic_ja_NNP.tsv", 'w', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Userdictja.word.upper(), 'NNP'])

            stmt = select(Dictionaryja)
            rows = session.execute(stmt).all()

            with open("utils/user_dic_ja_NNP.tsv", 'a', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Dictionaryja.word.upper(), 'NNP'])

            stmt = select(Scenarioja)
            rows = session.execute(stmt).all()

            with open("utils/user_dic_ja_NNP.tsv", 'a', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Scenarioja.question_ja.upper(), 'NNP'])
                    if row.Scenarioja.ner_ja is not None:
                        temp_arr = row.Scenarioja.ner_ja.split(',')

                        for temp in temp_arr:
                            tw.writerow([temp.upper(), 'NNP'])
    except Exception as e:
        print(e)

    finally:
        pass  # test