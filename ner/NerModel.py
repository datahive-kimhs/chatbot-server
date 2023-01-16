import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Model, load_model
from tensorflow.keras import preprocessing

# 개체명 인식 모델 모듈
class NerModel:
    def __init__(self, model_name, preprocess):

        # BIO 태그 클래시별 레이블
        self.index_to_ner = { 0: 'PAD',1: 'O', 2: 'CK_WORD', 3: 'NNP', 4: 'NNG'}

        # 의도 분류 모델 불러오기
        self.model = load_model(model_name)

        # 챗봇 Preprocess 객체
        self.p = preprocess

    # 개체명 클래스 예측
    def predict(self, query):
        # 형태소 분석

        pos = self.p.pos(query)

        # 문장 내 키워드 추출(불용어 제거)
        keywords = self.p.get_keywords(pos, without_tag=True)
        sequences = [self.p.get_wordidx_sequence(keywords)]
        
        # 패딩 처리
        max_len = 40
        padded_seqs = preprocessing.sequence.pad_sequences(sequences, padding="post", value=0, maxlen=max_len)

        # 키워드별 개체명 예측
        predict = self.model.predict(np.array([padded_seqs[0]]))
        predict_class = tf.math.argmax(predict, axis=-1)

        predict_class = predict_class.numpy()
        for index, value in enumerate(predict_class[0]):
            if value == 1 or value == 2 or value == 3 or value == 4:
                pass
            else:
                predict_class[0][index] = 3
        predict_class = tf.constant(predict_class)
        
        tags = [self.index_to_ner[i] for i in predict_class.numpy()[0]]
        
        return list(zip(keywords, tags))

    def predict_tags(self, query):
        # 형태소 분석
        pos = self.p.pos(query)

        # 문장 내 키워드 추출(불용어 제거)
        keywords = self.p.get_keywords(pos, without_tag=True)
        sequences = [self.p.get_wordidx_sequence(keywords)]

        # 패딩 처리
        max_len = 40
        padded_seqs = preprocessing.sequence.pad_sequences(sequences, padding="post", value=0, maxlen=max_len)
        predict = self.model.predict(np.array([padded_seqs[0]]))
        predict_class = tf.math.argmax(predict, axis=-1)

        predict_class = predict_class.numpy()
        for index, value in enumerate(predict_class[0]):
            if value == 1 or value == 2 or value == 3 or value == 4:
                pass
            else:
                predict_class[0][index] = 3
        predict_class = tf.constant(predict_class)

        tags = []
        for tag_idx in predict_class.numpy()[0]:
            if tag_idx == 1: continue
            tags.append(self.index_to_ner[tag_idx])
            if len(tags) == 0:
                return None
            return tags