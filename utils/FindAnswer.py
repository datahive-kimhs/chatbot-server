from os import abort
import pandas as pd
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Komoran
from utils.Preprocess import Preprocess_ja
from extensions import model_data
from connection import get_ckline_db_engine

komoran_object = Komoran()

p_ja = Preprocess_ja(word2index_dic='train_tools/dict/chatbot_dict_ja.bin',
               userdic=None)

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

#         print("== Post %i with dist=%.2f   : %s" %(i,d,dataset['Q'][i]))

        if d<best_dist:
            best_dist = d
            best_i = i

    print("Best post is %i, dist = %.2f" % (best_i, best_dist))
    print('-->', query)
    print('---->', dataset['Q'][best_i])

    # if best_dist <= 0.60:
    #     return dataset['A'][best_i]
    # elif best_dist > 0.60 and best_dist <= 0.95:
    #     close_matches_index = get_close_matches(
    #                             query, dataset['Q'], 10, 0.6)
    #     if len(close_matches_index):
    #         for index in close_matches_index:
    #             if index[1] == best_i:
    #                 return dataset['A'][best_i]
    #             else:
    #                 continue
    #         NUM = 0
    #         index = close_matches_index[NUM]
    #         answer_text = dataset['A'].iloc[index[1]]
    #         return answer_text
    #     else:
    #         return ''
    # elif best_dist > 0.95 and best_dist <= 1.20:
    #     close_matches_index = get_close_matches(
    #                             query, dataset['Q'], 10, 0.6)
    #     if len(close_matches_index):
    #             NUM = 0
    #             index = close_matches_index[NUM]
    #             answer_text = dataset['A'].iloc[index[1]]
    #             return answer_text
    #     else:
    #         return ''
    # else:
    #     return '' 
    if best_dist <= 0.1:
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
    elif best_dist > 0.1 and best_dist <= 0.95:
        close_matches_index = get_close_matches(
                                query, dataset['Q'], 10, 0.6)
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

    # 검색 쿼리 생성
    def _make_query(self, question, ner_tags, lang, opt):
        if lang == "ko":
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
        elif lang == "ja":
            sql = """SELECT
                    IDX, DEPTH, PARENT_IDX, NER, QUESTION,
                    ANSWER, KEYWORD_ANSWER, URL, CATEGORY, PRIORITY, EXPOSURE, USRUSE, NER_EN,
                    QUESTION_EN, ANSWER_EN, KEYWORD_ANSWER_EN, URL_EN, NER_JA, 
                    (CASE
                    WHEN A.question_ja LIKE '%INPUT%'
                    THEN (SELECT name_ja FROM ckaix_input_template WHERE IDX =  SUBSTR(A.QUESTION_ja, 7) )
                    ELSE A.question_ja
                    END ) as QUESTION_JA,
                    ANSWER_JA, KEYWORD_ANSWER_JA, URL_JA, NER_CN, QUESTION_CN, ANSWER_CN, KEYWORD_ANSWER_CN, URL_CN
                FROM ckaix_scenario A"""

        if question is not None and ner_tags is None:
            if opt == 1:
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
            else:
                if lang == "ko":
                    sql = sql + \
                        " where upper(question)=upper('{}') ".format(
                            question)
                elif lang == "en":
                    sql = sql + \
                        " where upper(question_en)=upper('{}') ".format(
                            question)
                elif lang == "ja":
                    sql = sql + \
                        " where upper(question_JA)=upper('{}') ".format(
                            question)
                elif lang == "cn":
                    sql = sql + \
                        " where upper(question_cn)=upper('{}') ".format(
                            question)

        elif ner_tags is not None:
            print(f"ner_tags : {ner_tags}")
            if opt == 1:
                where = " where exposure = '1' "
                if len(ner_tags) > 0:
                    where = " where exposure = '1' and "
                    where += " ("
                    for ne in ner_tags:
                        if "발행" == ne or "요청" == ne or "확인" == ne or "변경" == ne or "조회" == ne or "수정" == ne or "시간" == ne \
                        or "부산" == ne or "인천" == ne or "등록" == ne or "발생" == ne or "신청" == ne or "정보" == ne or "서비스" == ne \
                            or "신규" == ne or "운임" == ne or "자가" == ne or "운송" == ne or "번호" == ne or "진행" == ne or "상태" == ne \
                                or "추적" == ne or "発行" == ne or "要請" == ne or "確認" == ne or "変更" == ne or "照会" == ne or "修正" == ne or "時間" == ne \
                        or "釜山" == ne or "仁川" == ne or "登録" == ne or "発生" == ne or "申請" == ne or "情報" == ne or "サービス" == ne \
                            or "新規" == ne or "運賃" == ne or "自家" == ne or "運送" == ne or "番号" == ne or "進行" == ne or "状態" == ne \
                                or "追跡" == ne or "소개" == ne:
                            continue

                        if lang == "ko":
                            where += " upper(ner) like upper('%{}%') or ".format(ne)
                        elif lang == "en":
                            where += " upper(ner_en) like upper('%{}%') or ".format(ne)
                        elif lang == "ja":
                            where += " upper(ner_ja) like upper('%{}%') or ".format(ne)
                        elif lang == "cn":
                            where += " upper(ner_cn) like upper('%{}%') or ".format(ne)

                    where = where[:-3] + ')'
                sql = sql + where
            else:
                where = " where "
                if len(ner_tags) > 0:
                    where += " ("
                    for ne in ner_tags:
                        if "발행" == ne or "요청" == ne or "확인" == ne or "변경" == ne or "조회" == ne or "수정" == ne or "시간" == ne \
                        or "부산" == ne or "인천" == ne or "등록" == ne or "발생" == ne or "신청" == ne or "정보" == ne or "서비스" == ne \
                            or "신규" == ne or "운임" == ne or "자가" == ne or "운송" == ne or "번호" == ne or "진행" == ne or "상태" == ne \
                                or "추적" == ne or "発行" == ne or "要請" == ne or "確認" == ne or "変更" == ne or "照会" == ne or "修正" == ne or "時間" == ne \
                        or "釜山" == ne or "仁川" == ne or "登録" == ne or "発生" == ne or "申請" == ne or "情報" == ne or "サービス" == ne \
                            or "新規" == ne or "運賃" == ne or "自家" == ne or "運送" == ne or "番号" == ne or "進行" == ne or "状態" == ne \
                                or "追跡" == ne or "소개" == ne:
                            continue

                        if lang == "ko":
                            where += " upper(ner) like upper('%{}%') or ".format(ne)
                        elif lang == "en":
                            where += " upper(ner_en) like upper('%{}%') or ".format(ne)
                        elif lang == "ja":
                            where += " upper(ner_ja) like upper('%{}%') or ".format(ne)
                        elif lang == "cn":
                            where += " upper(ner_cn) like upper('%{}%') or ".format(ne)

                    where = where[:-3] + ')'
                sql = sql + where
        print(f'return sql : {sql}')
        return sql
 
    # 답변 검색
    def search(self, question, answer_keyword, ner_tags, ner_predicts, lang, input, depth, parent_idx, opt):
        url = ""
        category = ""
        print(f"answer_keword : {answer_keyword}")
        ckline_talk_dataset = model_data.get_chatting_ckline()
        if ner_tags is None:
            ner_tags = [""]
        # 질문으로 답변 검색
        try:
            sql = self._make_query(question, None, lang, opt)
            answers = self.session.execute(sql).first()
            idx = ""
            keyword_answer = ""
            answer, url, category, usruse = "", "", "", ""
            print(f"answers : {answers}")
            if lang == "ko":
                idx = answers[0]
                keyword_answer = self.find_keyword_answer(idx, lang, opt)
                answer, url, category, usruse, depth, parent_idx = answers[5], answers[7], answers[8], answers[11], answers[1], answers[2]
            elif lang == "en":
                idx = answers[0]
                keyword_answer = self.find_keyword_answer(idx, lang, opt)
                answer, url, category, usruse, depth, parent_idx = answers[14], answers[16], answers[8], answers[11], answers[1], answers[2]
            elif lang == "ja":
                print("you got it?")
                idx = answers[0]
                keyword_answer = self.find_keyword_answer(idx, lang, opt)
                print("out func find_keyword_answer")
                answer, url, category, usruse, depth, parent_idx = answers[19], answers[21], answers[8], answers[11], answers[1], answers[2]
            elif lang == "cn":
                idx = answers[0]
                keyword_answer = self.find_keyword_answer(idx, lang, opt)
                answer, url, category, usruse, depth, parent_idx = answers[24], answers[26], answers[8], answers[11], answers[1], answers[2]

            print(f"answer : {answer}")
            return answer, keyword_answer, url, usruse, category, input, depth, parent_idx

        # 검색되는 답변이 없으면 키워드로만 검색
        except Exception as ex:
            print(ex)
            if lang == "ko":
                if len(answer_keyword) != 0:
                    for answer_key in answer_keyword:
                        if len(answer_key) >= 2:
                            sql = self._make_query(None, answer_keyword, lang, opt)
                            answers = self.session.execute(sql).all()
                            usruse = "0"
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

                                        vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

                                        contents_tokens = [komoran_object.morphs(row) for row in ckline_talk_dataset['Q']]

                                        contents_for_vectorize = []

                                        for content in contents_tokens:
                                            sentence = ''
                                            for word in content:
                                                sentence = sentence + ' ' + word

                                            contents_for_vectorize.append(sentence)

                                        X = vectorizer.fit_transform(contents_for_vectorize)
                                        num_samples, num_features = X.shape

                                        new_post = [question]
                                        new_post_tokens = [komoran_object.morphs(row) for row in new_post]

                                        new_post_for_vectorize = []

                                        for content in new_post_tokens:
                                            sentence = ''
                                            for word in content:
                                                sentence = sentence + ' ' + word

                                            new_post_for_vectorize.append(sentence)

                                        new_post_vec = vectorizer.transform(new_post_for_vectorize)
                                        result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                        
                                        print(f'천경해운 새로운 closer_matcher {result}')
                                        if result == None:
                                            answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                        elif len(result):
                                            answer = result
                                        else:
                                            answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""

                                    elif lang == "ja":
                                        pass
                                        # for i in answers:
                                        #     if keyNum < 7:
                                        #         keyword_answer += i[keyword_answerNum1]+","
                                        #     keyNum += 1

                                        # vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

                                        # contents_tokens = [komoran_object.morphs(row) for row in ckline_talk_dataset_ja['Q']]

                                        # contents_for_vectorize = []

                                        # for content in contents_tokens:
                                        #     sentence = ''
                                        #     for word in content:
                                        #         sentence = sentence + ' ' + word

                                        #     contents_for_vectorize.append(sentence)

                                        # X = vectorizer.fit_transform(contents_for_vectorize)
                                        # num_samples, num_features = X.shape

                                        # new_post = [question]
                                        # new_post_tokens = [komoran_object.morphs(row) for row in new_post]

                                        # new_post_for_vectorize = []

                                        # for content in new_post_tokens:
                                        #     sentence = ''
                                        #     for word in content:
                                        #         sentence = sentence + ' ' + word

                                        #     new_post_for_vectorize.append(sentence)

                                        # new_post_vec = vectorizer.transform(new_post_for_vectorize)
                                        # result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                        
                                        # print(f'천경해운 새로운 closer_matcher {result}')
                                        # if result == None:
                                        #     answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                        # elif len(result):
                                        #     answer = result
                                        # else:
                                        #     answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                
                                elif len(answers) == 1:
                                    if ner_tags[0] == "CK_WORD":
                                        a = self.tag_to_word(ner_predicts, lang)
                                        keyword_answer = a+","

                                    if lang == "ko":
                                        try:
                                            keyword_answer += answers[0][keyword_answerNum2]
                                            answer, category = answers[0][answerNum],  answers[0][8]
                                            depth = answers[0][1]
                                            parent_idx = answers[0][2]
                                            usruse = answers[0][11]

                                            if keyword_answer == "딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                                keyword_answer = "지연공문,"
                                                category = ''
                                            elif keyword_answer == ",딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                                keyword_answer = "지연공문,"
                                                category = ''

                                            vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

                                            contents_tokens = [komoran_object.morphs(row) for row in ckline_talk_dataset['Q']]

                                            contents_for_vectorize = []

                                            for content in contents_tokens:
                                                sentence = ''
                                                for word in content:
                                                    sentence = sentence + ' ' + word

                                                contents_for_vectorize.append(sentence)

                                            X = vectorizer.fit_transform(contents_for_vectorize)
                                            num_samples, num_features = X.shape

                                            new_post = [question]
                                            new_post_tokens = [komoran_object.morphs(row) for row in new_post]

                                            new_post_for_vectorize = []

                                            for content in new_post_tokens:
                                                sentence = ''
                                                for word in content:
                                                    sentence = sentence + ' ' + word

                                                new_post_for_vectorize.append(sentence)

                                            new_post_vec = vectorizer.transform(new_post_for_vectorize)
                                            result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                            print(f'천경해운 새로운 closer_matcher {result}')
                                            if len(result):
                                                answer = result
                                            else:
                                                answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                        except Exception as ex:
                                            find_keyword = answers[0][4]
                                            depth = answers[0][1]
                                            parent_idx = answers[0][2]
                                            usruse = answers[0][11]

                                            keyword_answer = find_keyword
                                            answer = "다음과 같은 키워드가 검색되었습니다."
                                    elif lang == "ja":
                                        try:
                                            pass
                                        except:
                                            pass
                                        #     keyword_answer += answers[0][keyword_answerNum2]
                                        #     answer, category = answers[0][answerNum],  answers[0][8]
                                        #     depth = answers[0][1]
                                        #     parent_idx = answers[0][2]
                                        #     usruse = answers[0][11]

                                        #     if keyword_answer == "딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                        #         keyword_answer = "지연공문,"
                                        #         category = ''
                                        #     elif keyword_answer == ",딜레이노티스|CKAIX_RPA_WORKING_LIST,":
                                        #         keyword_answer = "지연공문,"
                                        #         category = ''

                                        #     vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

                                        #     contents_tokens = [komoran_object.morphs(row) for row in ckline_talk_dataset['Q']]

                                        #     contents_for_vectorize = []

                                        #     for content in contents_tokens:
                                        #         sentence = ''
                                        #         for word in content:
                                        #             sentence = sentence + ' ' + word

                                        #         contents_for_vectorize.append(sentence)

                                        #     X = vectorizer.fit_transform(contents_for_vectorize)
                                        #     num_samples, num_features = X.shape

                                        #     new_post = [question]
                                        #     new_post_tokens = [komoran_object.morphs(row) for row in new_post]

                                        #     new_post_for_vectorize = []

                                        #     for content in new_post_tokens:
                                        #         sentence = ''
                                        #         for word in content:
                                        #             sentence = sentence + ' ' + word

                                        #         new_post_for_vectorize.append(sentence)

                                        #     new_post_vec = vectorizer.transform(new_post_for_vectorize)
                                        #     result = get_close_question(X, num_samples, new_post_vec, ckline_talk_dataset, question)
                                        #     print(f'천경해운 새로운 closer_matcher {result}')
                                        #     if len(result):
                                        #         answer = result
                                        #     else:
                                        #         answer, url = "아래의 버튼 중 원하시는 업무를 선택해주세요", ""
                                        # except Exception as ex:
                                        #     find_keyword = answers[0][4]
                                        #     depth = answers[0][1]
                                        #     parent_idx = answers[0][2]
                                        #     usruse = answers[0][11]

                                        #     keyword_answer = find_keyword
                                        #     answer = "다음과 같은 키워드가 검색되었습니다."

                                return answer, keyword_answer, url, usruse, category, input, depth, parent_idx
                            except Exception as ex:
                                print(ex)
                        else:
                            continue
                    return answer, keyword_answer, url, usruse, category, input, depth, parent_idx
                else:
                    return answer, keyword_answer, url, usruse, category, input, depth, parent_idx
            elif lang == "ja":
                sql = self._make_query(None, answer_keyword, lang, opt)
                answers = self.session.execute(sql).all()
                print(f"answers : {answers}")
                usruse = "0"
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
                        for i in answers:
                            if keyNum < 7:
                                keyword_answer += i[keyword_answerNum1]+","
                            keyNum += 1

                        answer, url = "下記のボタンの中からご希望の業務を選択してください.", ""

                    elif len(answers) == 1:
                        if ner_tags[0] == "CK_WORD":
                            a = self.tag_to_word(ner_predicts, lang)
                            keyword_answer = a+","

                        try:
                            keyword_answer += answers[0][keyword_answerNum2]
                            answer, category = answers[0][answerNum],  answers[0][8]
                            depth = answers[0][1]
                            parent_idx = answers[0][2]
                            usruse = answers[0][11]

                            answer, url = "下記のボタンの中からご希望の業務を選択してください.", ""
                        except Exception as ex:
                            find_keyword = answers[0][answerNum]
                            depth = answers[0][1]
                            parent_idx = answers[0][2]
                            usruse = answers[0][11]

                            keyword_answer = find_keyword
                            answer = "次のようなキーワードが検索されました."

                    return answer, keyword_answer, url, usruse, category, input, depth, parent_idx
            
                except Exception as ex:
                    print(ex)


    # NER 태그를 실제 입력된 단어로 변환
    def tag_to_word(self, ner_predicts, lang):
        answer = ""
        try:
            if lang == "ko":
                for word, tag in ner_predicts:
                    # 변환해야 하는 태그가 있는 경우 추가
                    if tag == 'CK_WORD':
                        sql = f"""select * from ckaix_dictionary where upper(word) = upper('{word}')"""
                        print(f"CK WORD sql : {sql}")
                        result = self.session.execute(sql).first()
                        if result:
                            answer = word + "의 뜻?"
            elif lang == "ja":
                for word, tag in ner_predicts:
                    # 변환해야 하는 태그가 있는 경우 추가
                    if tag == 'CK_WORD':
                        sql = f"""select * from ckaix_dictionary_ja where upper(word) = upper('{word}')"""
                        print(f"CK WORD sql : {sql}")
                        result = self.session.execute(sql).first()
                        if result:
                            answer = word + "の意味は?"
            return answer
        except:
            return ""

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

    # ner tag를 활용하여 답을 찾는 함수

    def get_answer(self, query, lang):
        if lang == "ko":
            sql = """select * from ckaix_answer where exposure = '1' and ner = '{}'""".format(
                query)
        elif lang == "ja":
            sql = """select * from ckaix_answer_ja where exposure = '1' and ner = '{}'""".format(
                query)
        answer = self.session.execute(sql).first()
        return answer[2], answer[3], answer[5], answer[6]

    # 사용자의 질문 중 해양물류사전에 등록 단어가 있을 경우 키워드버튼에 추가시키는 함수

    def get_dictionary(self, query, lang):
        if lang == "ko":
            sql = """select * from ckaix_dictionary dict where UPPER(dict.word) =  UPPER('{}') """.format(
                query)
            answer = self.session.execute(sql).first()
            answer_text = f"{answer[1]}의 뜻은 {answer[2]}"
        elif lang == "ja":
            sql = """select * from ckaix_dictionary_ja dict where UPPER(dict.word) =  UPPER('{}') """.format(
                query)
            answer = self.session.execute(sql).first()
            answer_text = f"{answer[1]}の意味は{answer[2]}"
        return answer_text

    # 챗봇 말풍선 하단에 출력되는 키워드를 만들어주는 함수
    def find_keyword_answer(self, idx, lang, opt):
        # print(f"idx : [{idx}]")
        # idx = int(idx)
        print(f"opt : {opt}")
        if opt == 1:
            sql = f"""select 
                    (CASE
                    WHEN category = 3 and A.question LIKE '%INPUT%'
                    THEN (SELECT name{f"_{lang}" if lang != "ko" else ""} FROM ckaix_input_template WHERE IDX =  SUBSTR(A.QUESTION, 7)) 
                    ELSE A.QUESTION{f"_{lang}" if lang != "ko" else ""} 
                    END) as question
                from ckaix_scenario A 
                where exposure = '1' and parent_idx =  {idx} order by priority"""
        else:
            sql = f"""select 
                    (CASE
                    WHEN category = 3 and A.question LIKE '%INPUT%'
                    THEN (SELECT name{f"_{lang}" if lang != "ko" else ""} FROM ckaix_input_template WHERE IDX =  SUBSTR(A.QUESTION, 7)) 
                    ELSE A.QUESTION{f"_{lang}" if lang != "ko" else ""} 
                    END) as question
                from ckaix_scenario A 
                where parent_idx =  {idx} order by priority"""

        print(f"sql : {sql}")
        results = self.session.execute(sql).all()
        print(f"results : {results}")
        ret = ""
        update_sql = ""
        for result in results:
            if result[0]:
                ret += result[0] + ","
        print(f"ret : {ret}")
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
