from typing import Any
import logging

from sqlalchemy import select, update, delete

from core import ckline_db
from models.answer import Answer

import json
import pandas as pd
import re
import random
import googletrans
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest
from konlpy.tag import Komoran
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer

from ner.NerModel import NerModel
from utils.Preprocess import Preprocess
from utils.user_dic_load import train_user_dict
from utils.FindAnswer import FindAnswer
from ner.make_train import make_train
from ner.train import train
from train_tools.dict.create_dict import create_dict

MIN_WORD = 3
CUTOFF = 0.6
komoran_object = Komoran()

# 사용자 사전 생성
train_user_dict()

# 챗봇 단어 사전 생성
# create_dict()

# 모델 학습 데이터 생성
# make_train()

# 모델 학습
# train()

# 전처리 객체 생성
p = Preprocess(word2index_dic='train_tools/dict/chatbot_dict.bin',
               userdic='utils/user_dic.tsv')

# 개체명 인식 모델
ner = NerModel(model_name='ner/ner_model.h5', preprocess=p)

# 데이터 로드 함수
def load_dataset():
    # 한국어 일상 대화 데이터
    small_talk_dataset = pd.read_json(f'./data/chatting_kr.json', encoding="UTF-8").dropna()
    # 천경해운 업무 대화 데이터
    ckline_talk_dataset = pd.read_json(f'./data/chatting_ckline.json', encoding="UTF-8").dropna()
    # 욕설 데이터
    abuse_dataset = pd.read_json(f'./data/korea_abuse_data.json', encoding="UTF-8").dropna()

    return small_talk_dataset, ckline_talk_dataset, abuse_dataset

# 특수문자 처리 함수
def convert_specialChar(query):
    if query[-1] == "?":
        query = re.sub('[?+]', '', query)
        query = query + "?"
    elif query[0] == "#":
        query = re.sub('[#+]', '', query)
        query = "#" + query
    elif query[-1] == ".":
        query = re.sub('[.+]', '', query)
    elif query[-1] == "!":
        query = re.sub('[!+]', '', query)
    elif query[-1] == ",":
        query = re.sub('[,+]', '', query)

    return query

# 예외 문자 처리 함수
def exception_handling(query):
    origin_query = query
    if "스케쥴" in query:
        query = query.replace('스케쥴', '스케줄')
    elif query == "연락처":
        query = "담당자 찾기"
    return query, origin_query

# 형태소 분석기 실행
def get_pos_keywords(query):
    pos = p.pos(query)
    # 품사 태그와 같이 키워드 출력
    answer_keyword = []
    answer_keyword_string = ""
    ret = p.get_keywords(pos, without_tag=False)
    for i in ret:
        if i[1] == 'NNG' or i[1] == 'NNP':
            if len(i[0]) >= 2:
                answer_keyword.append(i[0])
                answer_keyword_string += i[0]+","
    
    return answer_keyword, answer_keyword_string

# 개체명 인식
def predict_ner(query):
    ner_predicts = ner.predict(query)
    ner_tags = ner.predict_tags(query)

    return ner_predicts, ner_tags

# query와 데이터셋에 있는 Q과 매칭 후 해당 A 리턴하는 함수
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

# "연락처" 쿼리에 대한 특수 처리
def change_answer(query, answer_text):
    if query == "연락처":
        return "담당자 찾기 기능을 통하여 확인 부탁드립니다."
    return answer_text

def vectorize_transform(query, dataset):
    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

    contents_tokens = [komoran_object.morphs(row) for row in dataset['Q']]

    contents_for_vectorize = []

    for content in contents_tokens:
        sentence = ''
        for word in content:
            sentence = sentence + ' ' + word

        contents_for_vectorize.append(sentence)

    X = vectorizer.fit_transform(contents_for_vectorize)
    num_samples, num_features = X.shape

    new_post = [query]
    new_post_tokens = [komoran_object.morphs(row) for row in new_post]

    new_post_for_vectorize = []

    for content in new_post_tokens:
        sentence = ''
        for word in content:
            sentence = sentence + ' ' + word

        new_post_for_vectorize.append(sentence)

    new_post_vec = vectorizer.transform(new_post_for_vectorize)
    return X, num_samples, new_post_vec, dataset, query

# 대화셋 중 word와 가장 유사한 배열의 인덱스 값을 리턴
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

    print(f"result : {result}")
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

def get_close_question(X, num_samples, new_post_vec, dataset, query):
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

    if best_dist == 0.00:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.6)
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
                                query, dataset['Q'], 10, 0.5)
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
                                query, dataset['Q'], 10, 0.6)
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

    if best_dist == 0.00:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.6)
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
                                query, dataset['Q'], 10, 0.5)
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
                                query, dataset['Q'], 10, 0.6)
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

# 구글 번역 API와 연결하는 함수 (프로젝트 내에 사용할지는 미지수)
def translate(q):
    translator = googletrans.Translator()
    translator.raise_Exception = True
    translated = translator.translate(q, src='auto', dest='ko').text

    return translated

def make_answer(question: Any) -> Any:
#     """
#     if use DB, reference core.chatbot_sample.py
#     :param question: message(data) from client.
#     :return: message(data) to be sent client from server.
#     """
    # 데이터 로드
    small_talk_dataset, ckline_talk_dataset, abuse_dataset = load_dataset()
    
    # json에서 데이터 변환
    query = question['Query'].upper()
    lang = question['Lang'].lower()

    if lang != "ko":
        query = translate(query)
        print(f"번역된 쿼리 : {query}")
    # 특수문자 처리
    # query = convert_specialChar(query)
    # # 예외 문자 처리
    # query, origin_query = exception_handling(query)

    # # 형태소 분석기 실행
    # answer_keyword, answer_keyword_string = get_pos_keywords(query)

    # # 개체명 파악
    # ner_predicts, ner_tags = predict_ner(query)

    # print(f"ner_predicts : {ner_predicts}")
    # print(f"ner_tags : {ner_tags}")

    # # 답변 검색
    # keyword_answer = ""
    # answer_text = ""
    # url = ""
    # usruse = "0"
    # category = ""
    # input = ""

    # #################챗봇 answer 로직#########################
    # try:
    #     with ckline_db.get_db_session() as session:
    #         f = FindAnswer(session)

    #         # # 인풋 템플릿 내에서 언어에 따른 검색
    #         sql = f"""select * from ckaix_input_template where upper(name{f'_{lang}'  if lang != 'ko' else ''}) = '{query}'"""
    #         sql_result = session.execute(sql).all()
    #         print(f'input template내에서 입력과 같은 query가 있는지 검색 결과 - sql_result : {sql_result}')
    #         # 인풋 템플릿 내에서 검색될 경우 CKAIX_SCENARIO에서 question이 INPUT|{INDEX} 값으로 조회
    #         if sql_result:
    #             scenario_sql = f"""select * from ckaix_scenario where upper(question) = 'INPUT|{sql_result[0][0]}'"""
    #             scenario_result = session.execute(scenario_sql).all()
    #             print(f'input template내에서 검색될 경우 시나리오에서 question 검색 - scenario_result : {scenario_result}')

    #             if scenario_result:
    #                 if lang == "ko":
    #                     answer_text, keyword_answer, url, usruse, category, input = scenario_result[0][
    #                         5], "", scenario_result[0][7], scenario_result[0][11], scenario_result[0][8], sql_result[0][2]
    #                 if lang == "en":
    #                     answer_text, keyword_answer, url, usruse, category, input = scenario_result[0][
    #                         14], "", scenario_result[0][16], scenario_result[0][11], scenario_result[0][8], sql_result[0][2]
    #                 if lang == "ja":
    #                     answer_text, keyword_answer, url, usruse, category, input = scenario_result[0][
    #                         19], "", scenario_result[0][21], scenario_result[0][11], scenario_result[0][8], sql_result[0][2]
    #                 if lang == "cn":
    #                     answer_text, keyword_answer, url, usruse, category, input = scenario_result[0][
    #                         24], "", scenario_result[0][26], scenario_result[0][11], scenario_result[0][8], sql_result[0][2]
                
    #         # 관리자에서 등록한 # 키워드 답변 검색
    #         elif (query[0] == "#"):
    #             answer_text, url = f.get_answer(query)
    #             print(f'# 키워드가 query로 왔을 때 ckaix answer에서 검색 - answer text : {answer_text}')
    #             keyword_answer = ""
            
    #         # 관리자에서 등록한 해양물류사전 검색
    #         # elif query[-2:] == "뜻?":
    #         #     answer_text = f.get_dictionary(f.tag_to_answer(ner_predicts))
    #         #     print(f'CK_WORDS 단어를 ckaix dictionary에서 검색 - answer text : {answer_text}')

    #         # query가 천경해운 데이터 셋에 정확하게 있을 경우 검색
    #         try:
    #             if answer_text is None or answer_text == "":
    #                 print('천경해운 데이터셋 정확한 값')
    #                 if lang == "ko":
    #                     result = question_answer_match(query, ckline_talk_dataset)
    #                     print(f"천경해운 데이터셋 정확한 값 : {result}")
    #                     if len(result):
    #                         answer_text = result
    #                     else:
    #                         pass

    #         except Exception as ex:
    #             print("천경해운 데이터 셋 : ", ex)
    #             raise Exception
            
    #         # query가 일상대화 데이터 셋에 정확하게 있을 경우 검색
    #         try:
    #             if answer_text is None or answer_text == "":
    #                 print('일상대화 데이터셋 정확한 값')
    #                 if lang == "ko":
    #                     result = question_answer_match(query, small_talk_dataset)
    #                     print(f"일상대화 데이터셋 정확한 값 : {result}")
    #                     if len(result):
    #                         answer_text = result
    #                     else:
    #                         pass

    #         except Exception as ex:
    #             print("스몰톡 데이터 셋 : ", ex)
    #             raise Exception
            
    #         # CKAIX_SCENAIO에서 검색
    #         else:
    #             if answer_text is None or answer_text == "":
    #                 answer_text, keyword_answer, url, usruse, category, input = f.search(
    #                     query, answer_keyword=answer_keyword, ner_tags=ner_tags, ner_predicts=ner_predicts, lang=lang, input=input)
    #                 answer_text = change_answer(origin_query, answer_text)
    #                 print(f"search CKAIX_SCENAIO : {answer_text}")
            
    #         # 관리자에서 등록한 해양물류사전 검색
    #         try:
    #             if answer_text is None or answer_text == "":
    #                 answer_text = f.get_dictionary(f.tag_to_answer(ner_predicts))
    #                 print(f'CK_WORDS 단어를 ckaix dictionary에서 검색 - answer text : {answer_text}')
            
    #         except Exception as ex:
    #             print(" 해양 물류 사전 : ", ex)
            
    #         try:
    #             # 천경해운 데이터셋
    #             if answer_text is None or answer_text == "":

    #                 if lang == "ko":
    #                     X, num_samples, new_post_vec, ckline_talk_dataset, query = vectorize_transform(query, ckline_talk_dataset)
    #                     result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, query)
    #                     print(f'천경해운 새로운 closer_matcher : {result}')
    #                     if len(result):
    #                         answer_text = result
    #                     else:
    #                         pass

    #         except Exception as ex:
    #             print(" 천경물류 데이터셋 : ", ex)
            
    #         try:
    #             # 욕설 감지
    #             if answer_text is None or answer_text == "":
    #                 if lang == "ko":
    #                     close_matches_index = get_close_matches(
    #                             query, abuse_dataset['Q'], MIN_WORD, 0.7)
    #                     if len(close_matches_index):
    #                         print("욕설 감지 json 데이터셋으로 입장")
    #                         NUM = 0
    #                         index = close_matches_index[NUM]
    #                         answer_text = abuse_dataset['A'].iloc[index[1]]
    #                         print(f'욕설 감지 데이터셋에서 검색해서 나온 값 - answer text : {answer_text}')
    #                     else:
    #                         pass
            
    #         except Exception as ex:
    #             print("욕설 감지 데이터셋 : ", ex)
    #             raise Exception

    #         try:
    #             # 일상대화 데이터셋
    #             if answer_text is None or answer_text == "":

    #                 if lang == "ko":
    #                     X, num_samples, new_post_vec, small_talk_dataset, query = vectorize_transform(query, small_talk_dataset)
    #                     result = get_close_smalltalk_question(X, num_samples, new_post_vec, small_talk_dataset, query)
    #                     print(f'일상대화 새로운 closer_matcher : {result}')
    #                     if len(result):
    #                         answer_text = result
    #                     else:
    #                         pass

    #         except Exception as ex:
    #             print("스몰톡 데이터셋 : ", ex)
    #             raise Exception


    # except Exception as ex:
    #         answer_text = "죄송해요 무슨 말인지 모르겠어요. 조금 더 공부할게요!"
    #         keyword_answer = None  

    # if len(query) == 1:
    #         answer_text = "글자 수가 너무 짧습니다. <br>최소 2글자 이상 입력해주세요."

    # send_json_data_str = {
    #     "Query": query,
    #     "Answer":  answer_text if answer_text else "죄송해요 무슨 말인지 모르겠어요. 조금 더 공부할게요!",
    #     "keyword": answer_keyword,
    #     "keyword_answer": keyword_answer,
    #     "NER": str(ner_predicts),
    #     "url": url,
    #     "usruse": usruse,
    #     "category": category,
    #     "input": input
    # }
    # print(f'최종 결과 값 - send_json_data_str : {send_json_data_str}')

    return "hello"

    

