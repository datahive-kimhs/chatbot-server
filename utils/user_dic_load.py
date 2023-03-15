import csv
import time

import openpyxl
import pandas as pd
from sqlalchemy import select, text


import openpyxl
import pandas as pd
import csv


from sqlalchemy import select, update, delete

from connection import get_ckline_db_engine
from models.dictionary import Dictionary
from models.scenario import Scenario
from models.user_dict import UserDict


# 학습 데이터 초기화
def all_clear_train_data(db):
    cursor = db.cursor()
    # 기존 학습 데이터 삭제
    sql = '''
        delete from user_dict
    '''

    cursor.execute(sql)
    db.commit()

    # auto increment 초기화
    sql = '''
        ALTER TABLE user_dict AUTO_INCREMENT=1
    '''

    cursor.execute(sql)
    db.commit()


# db에 데이터 저장
def insert_data(db, xls_row):
    word = xls_row[0]
    shape = xls_row[1]

    cursor = db.cursor()
    sql = '''
        INSERT user_dict( word, shape)
        values(
            '%s', '%s'
        )
    ''' % (word, shape)

    # 엑셀에서 불러온 cell에 데이터가 없는 경우 null로 치환
    sql = sql.replace("'None'", "null")

    cursor.execute(sql)
    # print('{} 저장'.format(query.value))
    db.commit()


def train_user_dict_old(db):
    try:
        db.connect()
        sql = "select * from ckaix_user_dict"
        rows = db.select_all(sql)

        with open("utils/user_dic.tsv", 'w', encoding='utf-8', newline='') as f:
            tw = csv.writer(f, delimiter='\t')
            for row in rows:
                tw.writerow([row[1].upper(), row[2]])

        sql = "select * from ckaix_dictionary"
        rows = db.select_all(sql)
        with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
            tw = csv.writer(f, delimiter='\t')
            for row in rows:
                tw.writerow([row[1].upper(), 'NNP'])

        sql = "select * from ckaix_scenario"
        rows = db.select_all(sql)
        with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
            tw = csv.writer(f, delimiter='\t')
            for row in rows:
                tw.writerow([row[4].upper(), 'NNP'])
                if row[3] is not None:
                    temp_arr = row[3].split(",")
                    for temp in temp_arr:
                        tw.writerow([temp.upper(), 'NNP'])
    except Exception as e:
        print(e)


def train_user_dict():
    ckline_db = get_ckline_db_engine()
    try:
        user_dictionary = dict()
        with ckline_db.get_db_session() as session:
            user_dict_stmt = select(UserDict)
            user_dict_data = session.execute(user_dict_stmt).all()
            for user_dict_row in user_dict_data:
                user_dictionary[user_dict_row.UserDict.word.upper()] = user_dict_row.UserDict.shape

            dictionary_stmt = select(Dictionary.idx, Dictionary.word)
            dictionary_data = session.execute(dictionary_stmt).all()
            for dictionary_row in dictionary_data:
                user_dictionary[dictionary_row.word.upper()] = 'NNP'

            scenario_stmt = select(Scenario.idx, Scenario.ner, Scenario.question, Scenario.ner_ja, Scenario.question_ja)
            scenario_data = session.execute(scenario_stmt).all()
            for scenario_row in scenario_data:
                user_dictionary[scenario_row.question.upper()] = 'NNP'
                ner_split = scenario_row.ner.split(',')
                for ner in ner_split:
                    user_dictionary[ner.upper()] = 'NNP'
                
                user_dictionary[scenario_row.question_ja.upper()] = 'NNP'
                ner_split = scenario_row.ner_ja.split(',')
                for ner in ner_split:
                    user_dictionary[ner.upper()] = 'NNP'

        recording_data = list(map(lambda key: [key, user_dictionary[key]], user_dictionary))

        with open("utils/user_dic.tsv", 'w', encoding='utf-8', newline='') as f:
            csv_w = csv.writer(f, delimiter='\t')
            csv_w.writerows(recording_data)

    except Exception as e:
        print(e)
        raise e

# import openpyxl
# import pandas as pd
# import csv

# from typing import Any
# import logging

# from sqlalchemy import select, update, delete

# from connection import get_ckline_db_engine
# from models.dictionary import Dictionary
# from models.scenario import Scenario
# from models.user_dict import UserDict


# def train_user_dict():
#     try:
#         ckline_db = get_ckline_db_engine()
#         with ckline_db.get_db_session() as session:
#             stmt = select(UserDict)
#             rows = session.execute(stmt).all()

#             with open("utils/user_dic.tsv", 'w', encoding='utf-8', newline='') as f:
#                 tw = csv.writer(f, delimiter='\t')
#                 for row in rows:
#                     tw.writerow([row.UserDict.word.upper(), row.UserDict.shape])

#             stmt = select(Dictionary)
#             rows = session.execute(stmt).all()

#             with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
#                 tw = csv.writer(f, delimiter='\t')
#                 for row in rows:
#                     tw.writerow([row.Dictionary.word.upper(), "NNP"])

#             stmt = select(Scenario)
#             rows = session.execute(stmt).all()

#             with open("utils/user_dic.tsv", 'a', encoding='utf-8', newline='') as f:
#                 tw = csv.writer(f, delimiter='\t')
#                 for row in rows:
#                     tw.writerow([row.Scenario.question.upper(), 'NNP'])
#                     if row.Scenario.ner is not None:
#                         temp_arr = row.Scenario.ner.split(',')

#                         for temp in temp_arr:
#                             tw.writerow([temp.upper(), 'NNP'])
#     except Exception as e:
#         print(e)
#     finally:
#         pass  # test
