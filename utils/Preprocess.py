from konlpy.tag import Komoran
import pickle
import MeCab

class Preprocess_ja:
    def __init__(self, word2index_dic='', userdic=None):
        # 단어 인덱스 사전 불러오기
        if word2index_dic != '':
            f = open(word2index_dic, "rb")
            self.word_index = pickle.load(f)

            f.close()
        else:
            self.word_index = None

        # 형태소 분석기 초기화
        self.mecab = MeCab.Tagger()

        # 제외할 품사
        # 참조 : https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=apparition18&logNo=100106659574
        # 부사, 연대사, 접속사, 감동사, 조동사, 조사 , 보조기호 제거
        self.exclusion_tags = [
            '副詞', '連体詞', '接続詞', '感動詞', '助動詞', '助詞', '補助記号'
        ]
    
    # 형태소 분석기 POS 태거
    def pos(self, sentence):
        result = []
        for i in range(len(self.mecab.parse(sentence).split("\n"))-2):
            try:
                word = self.mecab.parse(sentence).split("\n")[i].split("\t")[0]
                pos = self.mecab.parse(sentence).split("\n")[i].split("\t")[4].split("-")[0]
                result.append((word,pos))
            except:
                word = self.mecab.parse(sentence).split("\n")[i].split("\t")[0]
                pos = self.mecab.parse(sentence).split("\n")[i].split("\t")[4]
                result.append((word,pos))
        return result
    
    # 불용어 제거 후 필요한 품사 정보만 가져오기
    def get_keywords(self, pos, without_tag=False):
        def f(x): return x in self.exclusion_tags
        word_list = []
        for p in pos:
            if f(p[1]) is False:
                word_list.append(p if without_tag is False else p[0])
        return word_list

    # 키워드를 단어 인덱스 시퀀스로 변환
    def get_wordidx_sequence(self, keywords):
        if self.word_index is None:
            return []
        w2i = []
        for word in keywords:
            try:
                w2i.append(self.word_index[word])
            except KeyError:
                # 해당 단어가 사전에 없는 경우 OOV 처리
                w2i.append(self.word_index['OOV'])
        return w2i

class Preprocess:
    def __init__(self, word2index_dic='', userdic=None):  # 생성자
        # 단어 인덱스 사전 불러오기
        if word2index_dic != '':
            f = open(word2index_dic, "rb")
            self.word_index = pickle.load(f)

            f.close()
        else:
            self.word_index = None

        # 형태소 분석기 초기화
        self.komoran = Komoran(userdic=userdic)

        # 제외할 품사
        # 참조 : https://komorandocs.readthedocs.io/ko/latest/firststep/postypes.html
        # 관계언 제거, 기호 제거
        # 어미 제거
        # 접미사 제거
        self.exclusion_tags = [
            'JKS', 'JKC', 'JKO', 'JKB', 'JKV', 'JKQ',
            'JX', 'JC',
            'SF', 'SP', 'SS', 'SE', 'SO',
            'EP', 'EF', 'EC', 'ETN', 'ETM',
            'XSN', 'XSV', 'XSA'
        ]

    # 형태소 분석기 POS 태거
    def pos(self, sentence):
        return self.komoran.pos(sentence)

    # 불용어 제거 후 필요한 품사 정보만 가져오기
    def get_keywords(self, pos, without_tag=False):
        def f(x): return x in self.exclusion_tags
        word_list = []
        for p in pos:
            if f(p[1]) is False:
                word_list.append(p if without_tag is False else p[0])
        return word_list

    # 키워드를 단어 인덱스 시퀀스로 변환
    def get_wordidx_sequence(self, keywords):
        if self.word_index is None:
            return []
        w2i = []
        for word in keywords:
            try:
                w2i.append(self.word_index[word])
            except KeyError:
                # 해당 단어가 사전에 없는 경우 OOV 처리
                w2i.append(self.word_index['OOV'])
        return w2i
