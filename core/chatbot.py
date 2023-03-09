import logging
import json
import re
import random
import string
from typing import Any, Optional

import pandas as pd
import googletrans
from sqlalchemy import select, update, delete
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest
from konlpy.tag import Komoran
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer

from connection import get_ckline_db_engine
from rank_bm25 import BM25Okapi
from models.answer import Answer
from ner.NerModel import NerModel
from ner.NerModel import NerModel_ja
from ner.make_train import make_train
from ner.train import train
from utils.Preprocess import Preprocess
from utils.Preprocess import Preprocess_ja
from utils.user_dic_load import train_user_dict
from utils.user_dic_load_ja import train_user_dict_ja
from utils.FindAnswer import FindAnswer
from ner.make_train import make_train
from ner.train import train
from train_tools.dict.create_dict import create_dict
from train_tools.dict.create_dict_ja import create_dict_ja
from schema.chatbot import ChatData
from schema.response import ChatResponse

import tensorflow as tf
from transformers import AutoTokenizer
from transformers import TFGPT2LMHeadModel

from extensions import model_data

# result = model_data.get_chatting_ckline()
# print(result)
MIN_WORD = 3
CUTOFF = 0.6

# text = "聴いていた楽しくなければ音楽とは認めない." 
# p_jp = Preprocess_ja()
# print(p_jp.pos(text))

# text = "듣던 즐겁지 않으면 음악으로 인정하지 않는다." 
# p = Preprocess()
# print(p.pos(text))

# 사용자 사전 생성(일본어)
# train_user_dict_ja()

# 사용자 사전 생성(한국어)
# train_user_dict()

# 챗봇 단어 사전 생성(일본어)
# create_dict_ja()

# 챗봇 단어 사전 생성(한국어)
# create_dict()

# 모델 학습 데이터 생성(한국어)
# make_train()

# 모델 학습 데이터 생성(일본어)
# make_train_ja()

# 모델 학습(한국어)
# train()

# 모델 학습(일본어)
# train_ja()

# 전처리 객체 생성(한국어)
# p = Preprocess(word2index_dic='train_tools/dict/chatbot_dict.bin',
#              userdic='utils/user_dic.tsv')

# 개체명 인식 모델(한국어)
# ner = NerModel(model_name='ner/ner_model.h5', preprocess=p)


komoran = Komoran()
# 전처리 객체 생성
p = Preprocess(word2index_dic='train_tools/dict/chatbot_dict.bin',
               userdic='utils/user_dic.tsv')

# 전처리 객체 생성
p_ja = Preprocess_ja(word2index_dic='train_tools/dict/chatbot_dict_ja.bin',
                     userdic=None)

# 개체명 인식 모델
ner = NerModel(model_name='ner/ner_model.h5', preprocess=p)
ner_ja = NerModel_ja(model_name='ner/ner_model_ja_ver1.h5', preprocess=p_ja)

def get_close_matches(word, possibilities, n=3, cutoff=0.6):
    if not n > 0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for index, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), index))

    # Move the best scorers to head of list
    result = _nlargest(n, result)

    # Strip scores for the best n matches
    if result:
        return [x for x in result]
    else:
        return []

def dist_raw(v1, v2):
    delta = v1 - v2   # 벡터 사이의 거리를 구하기 위해 빼줌
    return sp.linalg.norm(delta.toarray())

def get_close_smalltalk_question(X, num_samples, new_post_vec, dataset, query):
    best_doc = None
    best_dist = 65535
    best_i = None

    for i in range(0, num_samples):
        post_vec = X.getrow(i)

        # 함수호출
        d = dist_raw(post_vec, new_post_vec)

        if d<best_dist:
            best_dist = d
            best_i = i

    print("Best post is %i, dist = %.2f" % (best_i, best_dist))
    print('-->', query)
    print('---->', dataset['Q'][best_i])

    if best_dist <= 0.1:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.7)
        if len(close_matches_index):
            for index in close_matches_index:
                if index[1] == best_i:
                    return dataset['A'][best_i]
                else:
                    continue
            NUM = 0
            index = close_matches_index[NUM]
            answer_text = dataset['A'].iloc[index[1]]
            return answer_text
        else:
            return ''
    elif best_dist > 0.1 and best_dist <= 0.95:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.7)
        if len(close_matches_index):
            for index in close_matches_index:
                if index[1] == best_i:
                    return dataset['A'][best_i]
                else:
                    continue
            return dataset['A'][best_i]
        else:
            return ''
    elif best_dist > 0.95 and best_dist <= 1.20:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.7)
        if len(close_matches_index):
            for index in close_matches_index:
                if index[1] == best_i:
                    return dataset['A'][best_i]
                else:
                    continue
            return ''
        else:
            return ''
    else:
        return ''
    
def load_corpus(dataset, lang):
    if lang == "ko":
        merge_dataset_corpus = dataset['Q']
        merge_dataset_tokenized_corpus = []
        for data in merge_dataset_corpus:
            pos_list = komoran.pos(data)
            result = [pos[0] for pos in pos_list]
            merge_dataset_tokenized_corpus.append(result)
        dataset_bm25 = BM25Okapi(merge_dataset_tokenized_corpus)
        return dataset_bm25
    elif lang == "ja":
        merge_dataset_corpus = dataset['Q']
        merge_dataset_tokenized_corpus = []
        for data in merge_dataset_corpus:
            pos_list = p_ja.pos(data)
            result = [pos[0] for pos in pos_list]
            merge_dataset_tokenized_corpus.append(result)

        dataset_bm25 = BM25Okapi(merge_dataset_tokenized_corpus)
        return dataset_bm25


def question_answer_match(query, dataset):
    answer_result = []
    for index, question in enumerate(dataset['Q']):
        if query == question.upper():
            answer_result.append(dataset['A'][index])
        else:
            continue
    if len(answer_result) == 0:
        return []
    else:
        answer_text = random.choice(answer_result)
        return answer_text


# 구글 번역 API와 연결하는 함수 (프로젝트 내에 사용할지는 미지수)
def translate(q, lang="en"):
    translator = googletrans.Translator()
    translator.raise_Exception = True
    translated = translator.translate(q, src='auto', dest=lang).text
    return translated


def convert_specialChar(query):
    syntax = string.punctuation
    syntax = syntax.replace("#", "")

    if query[0] == "#":
        query = re.sub('[#+]', '', query)
        query = "#" + query
    else:
        if query.find("/") > 0:
            pass
        elif query.find("-") > 0:
            pass
        elif query.find("(") > 0:
            pass
        elif query.find(")") > 0:
            pass
        elif query.find("?") > 0:
            pass
        elif query.find(",") > 0:
            pass
        else:
            query = query.translate(str.maketrans('', '', syntax))
    return query


def get_pos_keywords(query, lang):
    if lang == "ko":
        pos = p.pos(query)
        # 품사 태그와 같이 키워드 출력
        answer_keyword = []
        answer_keyword_string = ""
        ret = p.get_keywords(pos, without_tag=False)
        for i in ret:
            if i[1] == 'NNG' or i[1] == 'NNP':
                if len(i[0]) >= 2:
                    answer_keyword.append(i[0])
                    answer_keyword_string += i[0] + ","
    # elif lang == "ja":
    #     pos = p_ja.pos(query)
    #     # 품사 태그와 같이 키워드 출력
    #     answer_keyword = []
    #     answer_keyword_string = ""
    #     ret = p_ja.get_keywords(pos, without_tag=False)
    #     for i in ret:
    #         if i[1] == '名詞':
    #             if len(i[0]) >= 2:
    #                 answer_keyword.append(i[0])
    #                 answer_keyword_string += i[0] + ","
    elif lang == "ja":
        pos = p.pos(query)
        # 품사 태그와 같이 키워드 출력
        answer_keyword = []
        answer_keyword_string = ""
        ret = p.get_keywords(pos, without_tag=False)
        for i in ret:
            if i[1] == 'NNP':
                if len(i[0]) >= 2:
                    answer_keyword.append(i[0])
                    answer_keyword_string += i[0] + ","
        if len(answer_keyword) == 0:
            pos = p_ja.pos(query)
        # 품사 태그와 같이 키워드 출력
            answer_keyword = []
            answer_keyword_string = ""
            ret = p_ja.get_keywords(pos, without_tag=False)
            for i in ret:
                if i[1] == '名詞':
                    if len(i[0]) >= 2:
                        answer_keyword.append(i[0])
                        answer_keyword_string += i[0] + ","
    return answer_keyword, answer_keyword_string


def predict_ner(query, lang):
    if lang == "ko":
        ner_predicts = ner.predict(query)
        ner_tags = ner.predict_tags(query)
    elif lang == "ja":
        ner_predicts = ner_ja.predict(query)
        ner_tags = ner_ja.predict_tags(query)
    else:
        ner_predicts = []
        ner_tags = []
    return ner_predicts, ner_tags


def exception_handling(query):
    origin_query = query
    if "스케쥴" in query:
        query = query.replace('스케쥴', '스케줄')
    elif query == "연락처":
        query = "담당자 찾기"
    elif query == "도착통지서":
        query = query.replace('도착통지서', 'ARRIVAL NOTICE 발행')
    elif query == "CARGO TRACKING":
        query = query.replace('CARGO TRACKING', '화물추적')
    elif query == "SCHEDULE":
        query = query.replace('SCHEDULE', '스케줄')
    elif query == "상차지 변경":
        query = query.replace('상차지 변경', '픽업지 변경')
    return query, origin_query


def change_answer(query, answer_text):
    if query == "연락처":
        return "담당자 찾기 기능을 통하여 확인 부탁드립니다."
    return answer_text


def text_format(answers, text):
    answers_len = len(answers)
    if answers_len == 1:
        answer_text = text.format(answers[0])
    elif answers_len == 2:
        answer_text = text.format(answers[0], answers[1])
    elif answers_len == 3:
        answer_text = text.format(answers[0], answers[1], answers[2])
    elif answers_len == 4:
        answer_text = text.format(answers[0], answers[1], answers[2], answers[3])
    return answer_text


def special_qa_number_logic(type_: Optional[Any], query, ner_predicts):
    ckline_db = get_ckline_db_engine()
    syntax = string.punctuation
    if type_ is not None:
        try:
            # query에서 해당 type 넘버와 공백 제거
            preprocess_text = query.replace(type_[0], '').replace(' ', '')
            # query에서 특수문자 제거
            preprocess_text = preprocess_text.translate(str.maketrans('', '', syntax))
            sql = "select * from ckaix_special_qa"
            sql_result = ckline_db.get_db_session().execute(sql).all()
            for sql_result_element in sql_result:
                # ckaix_special_qa 테이블에서 question 가져와서 공백 제거
                preprocess_question = sql_result_element[0].replace(' ', '')
                # 특수문자 처리
                preprocess_question = preprocess_question.translate(str.maketrans('', '', syntax))
                # 전처리가 끝난 preprocess_text와 전처리가 끝난 preprocess_question이 같다면 로직 처리
                if preprocess_text == preprocess_question:
                    # LOB형식인 answer 쿼리를 받아와서 쿼리 변수에 비엘 넘버를 넣어서 sql 실행
                    lob_data = sql_result_element[3]
                    lob_data_text = ''.join(lob_data.read())
                    lob_data_sql = lob_data_text.format(type_[0])
                    answers = ckline_db.get_db_session().execute(lob_data_sql).all()
                    # text를 받아서 변수에 lob_data_sql 쿼리문 실행한 결과 answer_text에 저장
                    text = sql_result_element[2]
                    if answers is None:
                        break
                    answer_text = text.format(answers[0])
                    # answer_text 반환
                    return answer_text
            else:
                for ner in ner_predicts:
                    if ner[1] == "CK_WORD":
                        flag = True
                        for i in range(1, 5):
                            sql = "select * from ckaix_special_qa where upper(ner{}) = '{}' ".format(int(i), ner[0])
                            sql_result = ckline_db.get_db_session().execute(sql).all()
                            if len(sql_result) == 0:
                                continue
                            elif len(sql_result) != 0:
                                lob_data = sql_result[0][3]
                                lob_data_text = ''.join(lob_data.read())
                                lob_data_sql = lob_data_text.format(type_[0])
                                text = sql_result[0][2]
                                answers = ckline_db.get_db_session().execute(lob_data_sql).all()
                                if answers is None:
                                    flag = False
                                    break
                                    # raise ValueError("answers is not queried")
                                answer_text = text.format(answers[0])
                                return answer_text
                            elif len(sql_result) == 0 and i == int(sql_result[0][0]):
                                flag = False
                                break
                        if flag is False:
                            break
        except Exception as ex:
            print("FUNC_SPECIAL_QA_SPECIAL : ", ex)
            raise Exception
    else:
        cnt = 0
        for ner in ner_predicts:
            if ner[1] == "CK_WORD":
                cnt += 1
        try:
            if cnt >= 2:
                sql = "select * from ckaix_special_qa where question = '{}' ".format(query)
                sql_result = ckline_db.get_db_session().execute(sql).all()
                if len(sql_result) == 0:
                    raise ValueError("sql_result is not queried")
                lob_data = sql_result[0][3]
                new_sql = ''.join(lob_data.read())
                text = sql_result[0][2]
                for ner in ner_predicts:
                    try:
                        if ner[1] == "CK_WORD":
                            lob_data_sql = new_sql.format(ner)
                            lob_data_sql_answers = ckline_db.get_db_session().execute(lob_data_sql).all()
                            print(lob_data_sql_answers)
                            print(len(lob_data_sql_answers))
                            for i in range(len(lob_data_sql_answers)):
                                answer_text += text.format(lob_data_sql_answers[0][i])
                            return answer_text
                    except Exception as ex:
                        raise ValueError("answers is not queried")
            else:
                sql = "select * from ckaix_special_qa where question = '{}' ".format(query)
                sql_result = ckline_db.get_db_session().execute(sql).all()
                if len(sql_result) == 0:
                    raise ValueError("sql_result is not queried")
                lob_data = sql_result[0][3]
                new_sql = ''.join(lob_data.read())
                text = sql_result[0][2]
                answers = ckline_db.get_db_session().execute(new_sql).all()
                if answers is None:
                    raise ValueError("answers is not queried")
                answer_text = text_format(answers, text)
                return answer_text
        except Exception as ex:
            print("FUNC_SPECIAL_QA : ", ex)
            raise Exception

def return_answer_by_chatbot(user_text, model, tokenizer):
    sent = '<usr>' + user_text + '<sys>'
    input_ids = [tokenizer.bos_token_id] + tokenizer.encode(sent)
    input_ids = tf.convert_to_tensor([input_ids])
    output = model.generate(input_ids, max_length=50, do_sample=True, top_k=50)
    sentence = tokenizer.decode(output[0].numpy().tolist())
    chatbot_response = sentence.split('<sys> ')[1].replace('</s>', '')
    return chatbot_response

def vectorize_transform(query, dataset):
    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

    contents_tokens = [komoran.morphs(row) for row in dataset['Q']]

    contents_for_vectorize = []

    for content in contents_tokens:
        sentence = ''
        for word in content:
            sentence = sentence + ' ' + word

        contents_for_vectorize.append(sentence)

    X = vectorizer.fit_transform(contents_for_vectorize)
    num_samples, num_features = X.shape

    new_post = [query]
    new_post_tokens = [komoran.morphs(row) for row in new_post]

    new_post_for_vectorize = []

    for content in new_post_tokens:
        sentence = ''
        for word in content:
            sentence = sentence + ' ' + word

        new_post_for_vectorize.append(sentence)

    new_post_vec = vectorizer.transform(new_post_for_vectorize)
    return X, num_samples, new_post_vec, dataset, query


def make_answer(question: ChatData) -> ChatResponse:
    """
    if you use DB, reference core.chatbot_sample.py
    :param question: message(data) from client.
    :return: message(data) to be sent client from server.
    """
    train_user_dict()
    ckline_db = get_ckline_db_engine()
    # result = model_data.get_chatting_ckline()
    # print(result)

    query = question.query.upper()
    lang = question.lang.lower()
    bot_type = question.bot_type
    opt = question.opt
    test_query = query

    # 데이터 로드
    chatting_ckline = model_data.get_chatting_ckline()
    chatting_ckline_bm25 = model_data.get_chatting_ckline_bm25()
    chatting_kr = model_data.get_chatting_kr()
    merge_dataset_ja = model_data.get_merge_dataset_ja()
    merge_dataset_bm25_ja = model_data.get_merge_dataset_bm25_ja()
    model = model_data.get_model()
    tokenizer = model_data.get_tokenizer()

    if lang == "ko":
            # 일부 특수문자 처리
            query = convert_specialChar(query)
            query, origin_query = exception_handling(query)
            # 형태소 분석기 실행
            answer_keyword, answer_keyword_string = get_pos_keywords(query, lang)
            # 개체명 파악
            ner_predicts, ner_tags = predict_ner(query, lang)
    elif lang == "ja":
        # 일부 특수문자 처리
        query = convert_specialChar(query)
        # 형태소 분석기 실행
        answer_keyword, answer_keyword_string = get_pos_keywords(query, lang)
        # 개체명 파악
        ner_predicts, ner_tags = predict_ner(query, lang)
    print(f"answer_keyword : {answer_keyword}")
    print(f"ner_predicts : {ner_predicts}")
    print(f"ner_tags : {ner_tags}")

    # 답변 검색
    keyword_answer = ""
    answer_text = ""
    url = ""
    usruse = "0"
    category = ""
    input = ""
    depth = 1
    parent_idx = None
    
    try:
        with ckline_db.get_db_session() as session:
            f = FindAnswer(session)

            # # 인풋 템플릿 내에서 언어에 따른 검색
            sql = f"""select * from ckaix_input_template_ja where upper(name{f'_{lang}'  if lang != 'ko' else ''}) = '{query}'"""
            sql_result = session.execute(sql).all()
            print(f'input template내에서 입력과 같은 query가 있는지 검색 결과 - sql_result : {sql_result}')
            # 인풋 템플릿 내에서 검색될 경우 CKAIX_SCENARIO에서 question이 INPUT|{INDEX} 값으로 조회
            if sql_result:
                scenario_sql = f"""select * from ckaix_scenario_ja where upper(question) = 'INPUT|{sql_result[0][0]}'"""
                print(f"scenario_sql : {scenario_sql}")
                scenario_result = session.execute(scenario_sql).all()
                print(f'input template내에서 검색될 경우 시나리오에서 question 검색 - scenario_result : {scenario_result}')
                print(f"scenario_result : {scenario_result}")

                if sql_result:
                    scenario_sql = f"""select * from ckaix_scenario_ja where upper(question) = 'INPUT|{sql_result[0][0]}'"""
                    print(f"scenario_sql : {scenario_sql}")
                    scenario_result = session.execute(scenario_sql).all()
                    print(f'input template내에서 검색될 경우 시나리오에서 question 검색 - scenario_result : {scenario_result}')
                    print(f"scenario_result : {scenario_result}")
                    if scenario_result:
                        if lang == "ko":
                            answer_text, keyword_answer, url, usruse, category, input, depth, parent_idx = scenario_result[0][
                                5], "", scenario_result[0][7], scenario_result[0][11], scenario_result[0][8], sql_result[0][2], scenario_result[0][1], scenario_result[0][2]
                        if lang == "en":
                            answer_text, keyword_answer, url, usruse, category, input, depth, parent_idx = scenario_result[0][
                                14], "", scenario_result[0][16], scenario_result[0][11], scenario_result[0][8], sql_result[0][2], scenario_result[0][1], scenario_result[0][2]
                        if lang == "ja":
                            answer_text, keyword_answer, url, usruse, category, input, depth, parent_idx = scenario_result[0][
                                19], "", scenario_result[0][21], scenario_result[0][11], scenario_result[0][8], sql_result[0][2], scenario_result[0][1], scenario_result[0][2]
                        if lang == "cn":
                            answer_text, keyword_answer, url, usruse, category, input, depth, parent_idx = scenario_result[0][
                                24], "", scenario_result[0][26], scenario_result[0][11], scenario_result[0][8], sql_result[0][2], scenario_result[0][1], scenario_result[0][2]
                        # 관리자에서 등록한 # 키워드 답변 검색

            elif query[0] == "#":
                answer_text, url, parent_idx, depth = f.get_answer(query, lang)
                print(f'# 키워드가 query로 왔을 때 ckaix answer에서 검색 - answer text : {answer_text}')
                keyword_answer = ""

            try:
                if answer_text is None or answer_text == "":
                    # 비엘
                    BLnumber = []
                    # 부킹
                    BKnumber = []
                    # 컨테이너
                    CTnumber = []
                    # S/C 넘버
                    STnumber = []

                    # 비엘/부킹/컨테이너 번호를 찾기 위해 query를 split
                    split_query = query.split()
                    for query_element in split_query:
                        # 비엘 넘버라면 BLnumber 추가
                        if len(query_element) == 14 and query_element[-7:].isdigit():
                            BLnumber.append(query_element)
                            break
                        # 부킹 넘버라면 BKnumber 추가
                        elif len(query_element) == 9 and query_element[-7:].isdigit():
                            BKnumber.append(query_element)
                            break
                        # 컨테이너 넘버라면 CTnumber 추가
                        elif len(query_element) == 11 and query_element[-7:].isdigit():
                            CTnumber.append(query_element)
                            break
                        # S/C 넘버라면 STnumber 추가
                        elif len(query_element) == 10 and query_element[-7:].isdigit():
                            STnumber.append(query_element)
                            break
                        else:
                            continue

                    # 비엘 넘버 처리 로직
                    if len(BLnumber):
                        answer_text = special_qa_number_logic(BLnumber, query, ner_predicts)

                    # 부킹 넘버 처리 로직(위 비엘 넘버 처리 로직과 같음)
                    elif len(BKnumber):
                        answer_text = special_qa_number_logic(BKnumber, query, ner_predicts)

                    # 컨테이너 넘버 처리 로직(위 비엘 넘버 처리 로직과 같음)
                    elif len(CTnumber):
                        answer_text = special_qa_number_logic(CTnumber, query, ner_predicts)
                    
                    # S/C 넘버 처리 로직(위 비엘 넘버 처리 로직과 같음)
                    elif len(STnumber):
                        answer_text = special_qa_number_logic(STnumber, query, ner_predicts)
                    else:
                        pass

            except Exception as ex:
                print("SPECIAL_QA_SPECIAL_NUMBER : ", ex)
                raise Exception

            try:
                if answer_text is None or answer_text == "":
                    print('천경해운 데이터셋 정확한 값')
                    if lang == "ko":
                        result = question_answer_match(query, chatting_ckline)
                        print(f"천경해운 정확한 값에 대한 answer : {result}")
                        if len(result):
                            answer_text = result
                        else:
                            pass
                    elif lang == "ja":
                        result = question_answer_match(query, merge_dataset_ja)
                        print(f"천경해운(ja) 정확한 값에 대한 answer : {result}")
                        if len(result):
                            answer_text = result
                        else:
                            pass

            except Exception as ex:
                print("천경해운 정확 데이터 셋 : ", ex)
                raise Exception

            try:
                if answer_text is None or answer_text == "":
                    print('일상대화 데이터셋 정확한 값')
                    if lang == "ko":
                        result = question_answer_match(query, chatting_kr)
                        print(f"일상대화 정확한 값에 대한 answer : {result}")
                        if len(result):
                            answer_text = result
                        else:
                            pass
                    elif lang == "ja":
                        result = question_answer_match(query, merge_dataset_ja)
                        print(f"일상대화(ja) 정확한 값에 대한 answer : {result}")
                        if len(result):
                            answer_text = result
                        else:
                            pass

            except Exception as ex:
                print("스몰톡 데이터 셋 : ", ex)
                raise Exception

            try:
                if answer_text is None or answer_text == "":
                    try:
                        answer_text = special_qa_number_logic(None, query, ner_predicts)
                    except Exception as ex:
                        print(ex)
                        cnt = 0
                        for ner in ner_predicts:
                            if ner[1] == "CK_WORD":
                                cnt += 1
                        try:
                            if cnt >= 2:
                                for index, ner in enumerate(ner_predicts):
                                    if ner[1] == "CK_WORD":
                                        flag = True
                                        for i in range(1, 5):
                                            sql = "select * from ckaix_special_qa where upper(ner{}) = '{}' ".format(int(i),
                                                       ner[0])
                                            sql_result = ckline_db.get_db_session().execute(sql).all()
                                            if len(sql_result) == 0:
                                                continue
                                            elif len(sql_result) != 0:
                                                lob_data = sql_result[0][3]
                                                new_sql = ''.join(lob_data.read())
                                                text = sql_result[0][2]
                                                lob_data_sql = new_sql.format(ner_predicts[0][0])
                                                lob_data_sql_answers = ckline_db.get_db_session().execute(lob_data_sql).all()
                                                print(lob_data_sql_answers)
                                                print(len(lob_data_sql_answers))
                                                if lob_data_sql_answers is None:
                                                    flag = False
                                                    break
                                                for i in range(len(lob_data_sql_answers)):
                                                    answer_text += text.format(lob_data_sql_answers[i][0])
                                                break
                                            elif len(sql_result) == 0 and i == 4:
                                                flag = False
                                                break
                                        if flag is False:
                                            break
                            else:
                                for ner in ner_predicts:
                                    if ner[1] == "CK_WORD":
                                        flag = True
                                        for i in range(1, 5):
                                            sql = "select * from ckaix_special_qa where upper(ner{}) = '{}' ".format(int(i),
                                                                                                                    ner[0])
                                            sql_result = ckline_db.get_db_session().execute(sql).all()
                                            if len(sql_result) == 0:
                                                continue
                                            elif len(sql_result) != 0:
                                                lob_data = sql_result[0][3]
                                                new_sql = ''.join(lob_data.read())
                                                text = sql_result[0][2]
                                                answers = ckline_db.get_db_session().execute(new_sql).all()
                                                if answers is None:
                                                    flag = False
                                                    break
                                                answer_text = text_format(answers, text)
                                                break
                                            elif len(sql_result) == 0 and i == 4:
                                                flag = False
                                                break
                                        if flag is False:
                                            break
                        except Exception as ex:
                            print("FUNC_SPECIAL_QA : ", ex)
                            raise Exception

            except Exception as ex:
                print("SPECIAL_QA : ", ex)
                raise Exception
            
            # CKAIX_SCENAIO에서 검색
            else:
                if answer_text is None or answer_text == "":
                    answer_text, keyword_answer, url, usruse, category, input, depth, parent_idx = f.search(
                        query, answer_keyword=answer_keyword, ner_tags=ner_tags, ner_predicts=ner_predicts, lang=lang,
                        input=input, depth=depth, parent_idx=parent_idx, opt=opt)
                    if lang == 'ko':
                        answer_text = change_answer(origin_query, answer_text)
                    print(f"search CKAIX_SCENAIO : {answer_text}")
            
            # 관리자에서 등록한 해양물류사전 검색
            try:
                if answer_text is None or answer_text == "":
                    if query[:-4] == "의 뜻?":
                        answer_text = f.get_dictionary(f.tag_to_answer(ner_predicts), lang)
                        print(f'CK_WORDS 단어를 ckaix dictionary에서 검색 - answer text : {answer_text}')

            except Exception as ex:
                print(" 해양 물류 사전 : ", ex)

            try:
                # 위의 진행과정에서 answer_text 값을 얻지 못 했을지 스몰톡 검색을 한다.
                # 스몰톡은 2022.11.08 기준 천경해운 데이터셋, 한국어 일상 스몰톡 데이터셋이 존재한다.
                # 가장 우선 천경해운 데이셋으로 조회 후, 조회가 되지 않을 경우 한국어 일상 스몰톡으로 조회한다.
                # 천경해운 데이터셋
                if answer_text is None or answer_text == "":
                    if lang == "ko":
                        query_pos_list = komoran.pos(query)
                        tokenized_query = []
                        for pos in query_pos_list:
                            tokenized_query.append(pos[0])
                        if max(chatting_ckline_bm25.get_scores(tokenized_query)) >= 12:
                            text = chatting_ckline_bm25.get_top_n(tokenized_query, chatting_ckline['Q'], n=1)[0]
                            answer_text = question_answer_match(text, chatting_ckline)

                    elif lang == "ja":
                        # merge_data 일본어 버전 미구현
                        query_pos_list = p_ja.pos(query)
                        tokenized_query = []
                        for pos in query_pos_list:
                            tokenized_query.append(pos[0])
                        if max(merge_dataset_bm25_ja.get_scores(tokenized_query)) >= 12:
                            text = merge_dataset_bm25_ja.get_top_n(tokenized_query, merge_dataset_ja['Q'], n=1)[0]
                            answer_text = question_answer_match(text, merge_dataset_ja)

            except Exception as ex:
                print(" 한국 : 천경 데이터 셋 / 일본 : merge 데이터 셋 : ", ex)
            
            try:
                # 일상대화 데이터셋
                if answer_text is None or answer_text == "":
                    if lang == "ko":
                        print("한국어 기준 높은 스몰톡 입장")
                        close_matches_index = get_close_matches(
                                                        query, chatting_kr['Q'], 1, 0.8)
                        if len(close_matches_index):
                            NUM = 0
                            index = close_matches_index[NUM]
                            answer_text = chatting_kr['A'].iloc[index[1]]

            except Exception as ex:
                print(" 한국어 기준 높은 스몰톡 : ", ex)
                raise Exception
            
            try:
                if answer_text is None or answer_text == "":
                    if lang == "ko":
                        print("kogpt로 입장!")
                        answer_text = return_answer_by_chatbot(test_query, model, tokenizer)

            except Exception as ex:
                print(" 생성 모델 : ", ex)

    # 위 모든 과정중에도 답을 얻지 못한 경우에는 다음과 같은 값을 리턴한다.
    except Exception as ex:
        if lang == "ko":
            answer_text = "죄송해요 무슨 말인지 모르겠어요. 조금 더 공부할게요!"
            keyword_answer = None
        elif lang == "ja":
            answer_text = "すみません, 何を言っているのかわかりません. もう少し勉強します!"
            keyword_answer = None

    if len(query) == 1:
        if lang == "ko":
            answer_text = "글자 수가 너무 짧습니다. <br>최소 2글자 이상 입력해주세요."
        elif lang == "ja":
            answer_text = "文字数が短すぎます. <br>最低2文字以上入力してください."
    
    # query = query + "<BR>"
    if lang == "ja":
        send_json_data_str = {
            "Query": query,
            "Answer": answer_text if answer_text else "すみません, 何を言っているのかわかりません. もう少し勉強します!",
            "keyword": answer_keyword,
            "keyword_answer": keyword_answer,
            "NER": str(ner_predicts),
            "url": url,
            "usruse": usruse,
            "category": category,
            "input": input,
            "depth": depth,
            "parent_idx": parent_idx,
        }
    else:
        send_json_data_str = {
            "Query": query,
            "Answer": answer_text if answer_text else "죄송해요 무슨 말인지 모르겠어요. 조금 더 공부할게요!",
            "keyword": answer_keyword,
            "keyword_answer": keyword_answer,
            "NER": str(ner_predicts),
            "url": url,
            "usruse": usruse,
            "category": category,
            "input": input,
            "depth": depth,
            "parent_idx": parent_idx,
        }
    print(f'최종 결과 값 - send_json_data_str : {send_json_data_str}')

    return ChatResponse(**send_json_data_str)
