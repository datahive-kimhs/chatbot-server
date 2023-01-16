import openpyxl
import pandas as pd
import csv

from typing import Any
import logging

from sqlalchemy import select, update, delete

from core import ckline_db
from models.dictionary import Dictionary
from models.scenario import Scenario
from models.user_dict import Userdict

def train_user_dict():
    try:
        with ckline_db.get_db_session() as session:
            stmt = select(Userdict)
            rows = session.execute(stmt).all()

            with open("utils/user_dic.tsv", 'w', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Userdict.word.upper(), row.Userdict.shape])

            stmt = select(Dictionary)
            rows = session.execute(stmt).all()

            with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Dictionary.word.upper(), "NNP"])

            stmt = select(Scenario)
            rows = session.execute(stmt).all()

            with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
                tw = csv.writer(f, delimiter='\t')
                for row in rows:
                    tw.writerow([row.Scenario.question.upper(), 'NNP'])
                    if row.Scenario.ner is not None:
                        temp_arr = row.Scenario.ner.split(',')

                        for temp in temp_arr:
                            tw.writerow([temp.upper(), 'NNP'])
    except Exception as e:
        print(e)

    finally:
        pass  # test