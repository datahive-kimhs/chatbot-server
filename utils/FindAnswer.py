from os import abort
import pandas as pd
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Komoran

komoran_object = Komoran()

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

class FindAnswer:
    def __init__(self, session):
        self.session = session

    # ner tag를 활용하여 답을 찾는 함수
    def get_answer(self, query):
        sql = """select * from ckaix_answer where exposure = '1' and ner = '{}'""".format(
            query)
        answer = self.session.execute(sql).all()
        return answer[0][2], answer[0][3]
    
    # 태그가 포함되어있는 단어를 변환해주는 함수
    def tag_to_answer(self, ner_predicts):
        answer = ""
        for word, tag in ner_predicts:
            if word == "선박" or word == "양하":
                tag = 'CK_WORD'
                answer = word
                break
            # 변환해야 하는 태그가 있는 경우 추가
            if tag == 'CK_WORD':
                answer = word
                break

        return answer
    
    # 사용자의 질문 중 해양물류사전에 등록 단어가 있을 경우 키워드버튼에 추가시키는 함수
    def get_dictionary(self, query):
        sql = """select * from ckaix_dictionary dict where UPPER(dict.word) =  UPPER('{}') """.format(
            query)
        answer = self.session.execute(sql).all()
        answer_text = f"{answer[0][1]}의 뜻은 {answer[0][2]}"
        return answer_text


    # 검색 쿼리 생성
    def _make_query(self, question, ner_tags, lang):
        sql = """SELECT
                    IDX, DEPTH, PARENT_IDX, NER, 
                    (CASE 
                    WHEN A.question LIKE '%INPUT%' 
                    THEN (SELECT name FROM ckaix_input_template WHERE IDX =  SUBSTR(A.QUESTION, 7) ) 
                    ELSE A.question 
                    END ) as QUESTION,
                    ANSWER, KEYWORD_ANSWER, URL, CATEGORY, PRIORITY, EXPOSURE, USRUSE, NER_EN, 
                    QUESTION_EN, ANSWER_EN, KEYWORD_ANSWER_EN, URL_EN, NER_JA, QUESTION_JA, ANSWER_JA, 
                    KEYWORD_ANSWER_JA, URL_JA, NER_CN, QUESTION_CN, ANSWER_CN, KEYWORD_ANSWER_CN, URL_CN 
                FROM ckaix_scenario A"""
        if question is not None and ner_tags is None:
            if lang == "ko":
                sql = sql + \
                    " where exposure = '1' and upper(question)=upper('{}') ".format(
                        question)
            elif lang == "en":
                sql = sql + \
                    " where exposure = '1' and upper(question_en)=upper('{}') ".format(
                        question)
            elif lang == "ja":
                sql = sql + \
                    " where exposure = '1' and upper(question_JA)=upper('{}') ".format(
                        question)
            elif lang == "cn":
                sql = sql + \
                    " where exposure = '1' and upper(question_cn)=upper('{}') ".format(
                        question)

        elif ner_tags is not None:
            where = " where exposure = '1' "
            if len(ner_tags) > 0:
                where = " where exposure = '1' and "
                where += " ("
                for ne in ner_tags:
                    if "발행" == ne or "요청" == ne or "확인" == ne or "변경" == ne or "조회" == ne or "수정" == ne or "시간" == ne \
                    or "부산" == ne or "인천" == ne or "등록" == ne or "발생" == ne or "신청" == ne or "정보" == ne or "서비스" == ne \
                        or "신규" == ne or "운임" == ne or "자가" == ne or "운송" == ne or "번호" == ne or "진행" == ne or "상태" == ne \
                            or "추적" == ne:
                        continue

                    if lang == "ko":
                        where += " upper(ner) like upper('%{}%') or ".format(ne)
                    elif lang == "en":
                        where += " upper(ner_en) like upper('%{}%') or ".format(ne)
                    elif lang == "ja":
                        where += " upper(ner_JA) like upper('%{}%') or ".format(ne)
                    elif lang == "cn":
                        where += " upper(ner_cn) like upper('%{}%') or ".format(ne)

                where = where[:-3] + ')'
            sql = sql + where
        return sql

     # 답변 검색
    def search(self, question, answer_keyword, ner_tags, ner_predicts, lang, input):
        ckline_talk_dataset = pd.read_json(f'./data/chatting_ckline.json').dropna()
        url = ""
        category = ""
        if ner_tags is None:
            ner_tags = [""]
        # 질문으로 답변 검색
        try:
            sql = self._make_query(question, None, lang)
            answers = self.session.execute(sql).all()
            idx = ""
            keyword_answer = ""
            answer, url, category, usruse = "", "", "", ""

            if lang == "ko":
                idx = answers[0][0]
                keyword_answer = self.find_keyword_answer(idx, lang)
                answer, url, category, usruse = answers[0][5], answers[0][7], answers[0][8], answers[0][11]
            elif lang == "en":
                idx = answers[0][0]
                keyword_answer = self.find_keyword_answer(idx, lang)
                answer, url, category, usruse = answers[0][14], answers[0][16], answers[0][8], answers[0][11]
            elif lang == "ja":
                idx = answers[0][0]
                keyword_answer = self.find_keyword_answer(idx, lang)
                answer, url, category, usruse = answers[0][19], answers[0][21], answers[0][8], answers[0][11]
            elif lang == "cn":
                idx = answers[0][0]
                keyword_answer = self.find_keyword_answer(idx, lang)
                answer, url, category, usruse = answers[0][24], answers[0][26], answers[0][8], answers[0][11]

            return answer, keyword_answer, url, usruse, category, input

        # 검색되는 답변이 없으면 키워드로만 검색
        except Exception as ex:
            print(ex)
            if len(answer_keyword) != 0:
                for answer_key in answer_keyword:
                    if len(answer_key) >= 2:
                        sql = self._make_query(None, answer_keyword, lang)
                        answers = self.session.execute(sql).all()

                        keyword_answer = ""
                        answerNum = 5
                        keyword_answerNum1 = 4
                        keyword_answerNum2 = 6

                        if lang == "ko":
                            answerNum = 5
                            keyword_answerNum1 = 4
                            keyword_answerNum2 = 6
                        elif lang == "en":
                            answerNum = 14
                            keyword_answerNum1 = 13
                            keyword_answerNum2 = 15
                        elif lang == "ja":
                            answerNum = 19
                            keyword_answerNum1 = 18
                            keyword_answerNum2 = 20
                        elif lang == "cn":
                            answerNum = 24
                            keyword_answerNum1 = 23
                            keyword_answerNum2 = 25

                        # 고도화
                        try:
                            keyNum = 0
                            if len(answers) > 1:               
                               if lang == "ko":
                                    for i in answers:
                                        if keyNum < 7:
                                            keyword_answer += i[keyword_answerNum1]+","
                                        keyNum += 1

                                    X, num_samples, new_post_vec, ckline_talk_dataset, question = vectorize_transform(question, ckline_talk_dataset)
                                    result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                    print(f'answer > 1일 때, 천경해운 새로운 closer_matcher {result}')
                                    if result == None:
                                        answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                    elif len(result):
                                        answer = result
                                    else:
                                        answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                    
                            
                            elif len(answers) == 1:
                                if ner_tags[0] == "CK_WORD":
                                    a = self.tag_to_word(ner_predicts)
                                    keyword_answer = a+","

                                try:
                                    keyword_answer += answers[0][keyword_answerNum2]
                                    answer, category = answers[0][answerNum],  answers[0][8]

                                    if keyword_answer == "딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                        keyword_answer = "지연공문,"
                                        category = ''
                                    elif keyword_answer == ",딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                        keyword_answer = "지연공문,"
                                        category = ''

                                    X, num_samples, new_post_vec, ckline_talk_dataset, question = vectorize_transform(question, ckline_talk_dataset)
                                    result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                    print(f'answer == 1일 때, 천경해운 새로운 closer_matcher {result}')
                                    if len(result):
                                        answer = result
                                    else:
                                        answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                except Exception as ex:
                                    find_keyword = answers[0][4]

                                    keyword_answer = find_keyword
                                    answer = "다음과 같은 키워드가 검색되었습니다."

                            return answer, keyword_answer, url, "0", category, input
                        except Exception as ex:
                            print(ex)
                    else:
                        continue
                return answer, keyword_answer, url, usruse, category, input
            else:
                return answer, keyword_answer, url, usruse, category, input

    # 챗봇 말풍선 하단에 출력되는 키워드를 만들어주는 함수
    def find_keyword_answer(self, idx, lang):
        sql = f"""select 
                    (CASE
                     WHEN category = 3 
                     THEN (SELECT name{f"_{lang}" if lang != "ko" else ""} FROM ckaix_input_template WHERE IDX =  SUBSTR(A.QUESTION, 7)) 
                     ELSE A.QUESTION{f"_{lang}" if lang != "ko" else ""} 
                     END) as question
                from ckaix_scenario A 
                where exposure = '1' and parent_idx =  {idx} order by priority"""

        results = self.session.execute(sql).all()
        ret = ""
        update_sql = ""
        for result in results:
            if result[0]:
                ret += result[0] + ","

        if lang == "ko":
            update_sql = f"""update ckaix_scenario set keyword_answer = '{ret}' where idx = {idx}"""
        elif lang == "en":
            update_sql = f"""update ckaix_scenario set keyword_answer_en = '{ret}' where idx = {idx}"""
        elif lang == "ja":
            update_sql = f"""update ckaix_scenario set keyword_answer_JA = '{ret}' where idx = {idx}"""
        elif lang == "cn":
            update_sql = f"""update ckaix_scenario set keyword_answer_cn = '{ret}' where idx = {idx}"""
        
        self.session.execute(update_sql)
        return ret
    
    # NER 태그를 실제 입력된 단어로 변환
    def tag_to_word(self, ner_predicts):
        answer = ""
        try:
            for word, tag in ner_predicts:

                # 변환해야 하는 태그가 있는 경우 추가
                if tag == 'CK_WORD':
                    sql = f"""select * from ckaix_dictionary where upper(word) = upper('{word}')"""
                    print(f"CK WORD sql : {sql}")
                    result = self.session.execute(sql).all()
                    if result:
                        answer = word + "의 뜻?"

            return answer
        except:
            return ""
