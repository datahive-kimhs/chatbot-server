from typing import Any
from sqlalchemy import select
from connection import get_ckline_db_engine
from models.dictionary import Dictionary


def make_train():
    ckline_db = get_ckline_db_engine()
    with ckline_db.get_db_session() as session:
        stmt = select(Dictionary)
        rows = session.execute(stmt).all()

        with open("ner/ner_train.txt", 'w', encoding='utf-8', newline='') as f:
            for row in rows:      
                f.write(f"""; {row.Dictionary.word.upper()} 주문 하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 하고싶어요
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	주문	NNP	O
3	하	VV	O
4	고	EC	O
5	싶	VX	O
6	어요	EC	O


; {row.Dictionary.word.upper()} 먹고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 먹고싶어요
2	먹	VV	O
3	고	EC	O
4	싶	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	어요	EC	O

; {row.Dictionary.word.upper()} 하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 하고싶어요
2	하	VV	O
3	고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	싶	VX	O
5	어요	EC	O

; {row.Dictionary.word.upper()} 원해요
$<{row.Dictionary.word.upper()}:CK_WORD> 원해요
2	원	NNB	O
3	하	XSA	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	어요	EC	O

; {row.Dictionary.word.upper()} 어떻게 해야 되요?
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 해야 되요?
2	어떻	VA	O
3	게	EC	O
4	하	VV	O
5	아야	EC	O
6	되	VV	O
7	요	EF	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
8	?	SF	O

; {row.Dictionary.word.upper()} 어떻게 해야 돼
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 해야 돼
2	어떻	VA	O
3	게	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	하	VV	O
5	아야	EC	O
6	되	VV	O
7	어	EC	O

; {row.Dictionary.word.upper()} 하고 싶은데
$<{row.Dictionary.word.upper()}:CK_WORD> 하고 싶은데
2	하	VV	O
3	고	EC	O
4	싶	VX	O
5	은데	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 알려줘
$<{row.Dictionary.word.upper()}:CK_WORD> 알려줘
2	알리	VV	O
3	어	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	주	VX	O
5	어	EC	O

; {row.Dictionary.word.upper()} 가르쳐줘
$<{row.Dictionary.word.upper()}:CK_WORD> 가르쳐줘
2	가르치	VV	O
3	어	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	주	VX	O
5	어	EC	O

; {row.Dictionary.word.upper()} 하고 싶다
$<{row.Dictionary.word.upper()}:CK_WORD> 하고 싶다
2	하	VV	O
3	고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	싶	VX	O
5	다	EC	O

; {row.Dictionary.word.upper()} 하고 싶은데
$<{row.Dictionary.word.upper()}:CK_WORD> 하고 싶은데
2	하	VV	O
3	고	EC	O
4	싶	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	은데	EC	O

; {row.Dictionary.word.upper()} 할게요
$<{row.Dictionary.word.upper()}:CK_WORD> 할게요
2	하	VV	O
3	ㄹ게요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 도와줘
$<{row.Dictionary.word.upper()}:CK_WORD> 도와줘
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	돕	VV	O
3	아	EC	O
4	주	VX	O
5	어	EC	O

; {row.Dictionary.word.upper()} 할께요
$<{row.Dictionary.word.upper()}:CK_WORD> 할께요
3	ㄹ께	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	하	VV	O
4	요	JX	O

; {row.Dictionary.word.upper()} 도와주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 도와주세요
2	도와주	VV	O
3	시	EP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	어요	EC	O

; {row.Dictionary.word.upper()} 할 수 있나요?
$<{row.Dictionary.word.upper()}:CK_WORD> 할 수 있나요?
2	하	VV	O
3	ㄹ	ETM	O
4	수	NNB	O
5	있	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	나요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 가능 한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 가능 한가요
2	가능	XR	O
3	한	MM	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	가요	NNP	O

; {row.Dictionary.word.upper()} 문의드려요
$<{row.Dictionary.word.upper()}:CK_WORD> 문의드려요
2	문의	NNG	O
3	드리	VV	O
4	어요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 당일 가능한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 당일 가능한가요
2	당일	NNG	O
3	가능	XR	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	하	XSA	O
5	ㄴ	ETM	O
6	가요	NNP	O

; {row.Dictionary.word.upper()} 해주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 해주세요
2	하	VV	O
3	아	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	주	VX	O
5	시	EP	O
6	어요	EC	O

; {row.Dictionary.word.upper()} 하려구요
$<{row.Dictionary.word.upper()}:CK_WORD> 하려구요
2	하	VV	O
3	려구요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 되었나요
$<{row.Dictionary.word.upper()}:CK_WORD> 되었나요
2	되	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	었	EP	O
4	나요	EC	O

; {row.Dictionary.word.upper()} 되나요
$<{row.Dictionary.word.upper()}:CK_WORD> 되나요
2	되	VV	O
3	나요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 할수 있을까요?
$<{row.Dictionary.word.upper()}:CK_WORD> 할수 있을까요?
2	하	VV	O
3	ㄹ	ETM	O
4	수	NNB	O
5	있	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	을까요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 싶어요
3	어요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	싶	VX	O

; {row.Dictionary.word.upper()} 언제 가능
$<{row.Dictionary.word.upper()}:CK_WORD> 언제 가능
2	언제	MAG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	가능	XR	O

; {row.Dictionary.word.upper()} 언제가능할까요
$<{row.Dictionary.word.upper()}:CK_WORD> 언제가능할까요
2	언제	NP	O
3	가능	XR	O
4	하	XSA	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	ㄹ까요	EC	O

; {row.Dictionary.word.upper()} 한가요?
$<{row.Dictionary.word.upper()}:CK_WORD> 한가요?
2	하	VX	O
3	ㄴ가요	EF	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	?	SF	O

; {row.Dictionary.word.upper()} 어떻게 하나요
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 하나요
2	어떻	VA	O
3	게	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	하	VV	O
5	나요	EC	O

; {row.Dictionary.word.upper()} 어떻게 되나요
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 되나요
2	어떻	VA	O
3	게	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	되	VV	O
5	나요	EC	O

; {row.Dictionary.word.upper()} 어떻게 하나요
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 하나요
2	어떻	VA	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	게	EC	O
4	하	VV	O
5	나요	EC	O

; {row.Dictionary.word.upper()} 하는법
$<{row.Dictionary.word.upper()}:CK_WORD> 하는법
2	하	VV	O
3	는	ETM	O
4	법	NNB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 할래
$<{row.Dictionary.word.upper()}:CK_WORD> 할래
2	하	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	ㄹ래	EC	O

; {row.Dictionary.word.upper()} 해줘
$<{row.Dictionary.word.upper()}:CK_WORD> 해줘
2	하	VV	O
3	아	EC	O
4	주	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	어	EC	O

; {row.Dictionary.word.upper()} 확인
$<{row.Dictionary.word.upper()}:CK_WORD> 확인
2	확인	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 해야 합니다
$<{row.Dictionary.word.upper()}:CK_WORD> 해야 합니다
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	하	VV	O
3	아야	EC	O
4	하	VV	O
5	ㅂ니다	EC	O

; {row.Dictionary.word.upper()} 가능할까요
$<{row.Dictionary.word.upper()}:CK_WORD> 가능할까요
2	가능	XR	O
3	하	XSA	O
4	ㄹ까요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 몇시부터 가능한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 몇시부터 가능한가요
2	몇	MM	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	시	NNB	O
4	부터	JX	O
5	가능	XR	O
6	하	XSA	O
7	ㄴ	ETM	O
8	가요	NNP	O

; {row.Dictionary.word.upper()} 다음주 주문
$<{row.Dictionary.word.upper()}:CK_WORD> 다음주 주문
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	다음	NNG	O
3	주 주	NNP	O
4	문	NNP	O

; {row.Dictionary.word.upper()} 당일 주문
$<{row.Dictionary.word.upper()}:CK_WORD> 당일 주문
2	당일	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	주문	NNP	O

; {row.Dictionary.word.upper()} 모레주문
$<{row.Dictionary.word.upper()}:CK_WORD> 모레주문
2	모레	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	주문	NNP	O

; {row.Dictionary.word.upper()} 내일 주문 하고 싶습니다.
$<{row.Dictionary.word.upper()}:CK_WORD> 내일 주문 하고 싶습니다.
2	내일	NNG	O
3	주문	NNP	O
4	하	VV	O
5	고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	싶	VX	O
7	습니다	EF	O
8	.	SF	O

; {row.Dictionary.word.upper()} 내일 오후4시30분에 진료받으러 가겠습니다. 주문 부탁드립니다
$<{row.Dictionary.word.upper()}:CK_WORD> 내일 오후4시30분에 진료받으러 가겠습니다. 주문 부탁드립니다
2	내일	NNG	O
3	오후	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	4	SN	O
5	시	NNB	O
6	30	SN	O
7	분	NNB	O
8	에	JKB	O
9	진료	NNG	O
10	받	VV	O
11	으러	EC	O
12	가	VV	O
13	겠	EP	O
14	습니다	EF	O
15	.	SF	O
16	주문	NNP	O
17	부탁	NNG	O
18	드리	VV	O
19	ㅂ니다	EC	O

; {row.Dictionary.word.upper()} 내일주문 가능한가요?
$<{row.Dictionary.word.upper()}:CK_WORD> 내일주문 가능한가요?
2	내	NNB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	일주문	NNP	O
4	가능	XR	O
5	하	XSA	O
6	ㄴ가요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 내일주문하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 내일주문하고싶어요
2	내일	NNG	O
3	주문	NNG	O
4	하	XSV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	고	EC	O
6	싶	VX	O
7	어요	EC	O

; {row.Dictionary.word.upper()} 사랑니 발치 주문
$<{row.Dictionary.word.upper()}:CK_WORD> 사랑니 발치 주문
2	사랑니	NNP	O
3	발치	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	주문	NNP	O

; {row.Dictionary.word.upper()} 여기서 치료주문이 되나요?
$<{row.Dictionary.word.upper()}:CK_WORD> 여기서 치료주문이 되나요?
2	여기	NP	O
3	서	JKB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	치료	NNP	O
5	주문	NNP	O
6	이	JKS	O
7	되	VV	O
8	나요	EF	O
9	?	SF	O

; {row.Dictionary.word.upper()} 오늘 주문 가능한가요?
$<{row.Dictionary.word.upper()}:CK_WORD> 오늘 주문 가능한가요?
2	오늘	NNG	O
3	주문	NNP	O
4	가능	XR	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	하	XSA	O
6	ㄴ가요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 토요일주문
$<{row.Dictionary.word.upper()}:CK_WORD> 토요일주문
2	토요일	NNP	O
3	주문	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 받고싶은데 주문 어떻게 하나요
$<{row.Dictionary.word.upper()}:CK_WORD> 받고싶은데 주문 어떻게 하나요
2	받	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	고	EC	O
4	싶	VX	O
5	은데	EC	O
6	주문	NNP	O
7	어떻	VA	O
8	게	EC	O
9	하	VV	O
10	나요	EC	O

; {row.Dictionary.word.upper()} 하려고 하는데 주문 진행도와주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 하려고 하는데 주문 진행도와주세요
2	하	VV	O
3	려고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	하	VV	O
5	는데	EC	O
6	주문	NNP	O
7	진행	NNG	O
8	도와주	VV	O
9	시	EP	O
10	어요	EC	O

; {row.Dictionary.word.upper()} 신청 어떻게 하나요
$<{row.Dictionary.word.upper()}:CK_WORD> 신청 어떻게 하나요
2	신청	NNP	O
3	어떻	VA	O
4	게	EC	O
5	하	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	나요	EC	O

; {row.Dictionary.word.upper()} 주문상담하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문상담하고싶어요
2	주문	NNG	O
3	상담	NNG	O
4	하	XSV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	고	EC	O
6	싶	VX	O
7	어요	EC	O

; {row.Dictionary.word.upper()} 1월17일 주문이요
$<{row.Dictionary.word.upper()}:CK_WORD> 1월17일 주문이요
2	1	SN	O
3	월	NNB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	17	SN	O
5	일	NNB	O
6	주문	NNG	O
7	이	VCP	O
8	요	EC	O

; {row.Dictionary.word.upper()} 통합주문
$<{row.Dictionary.word.upper()}:CK_WORD> 통합주문
2	통합	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	주문	NNP	O

; {row.Dictionary.word.upper()} 어떻게 주문해야되지요?
$<{row.Dictionary.word.upper()}:CK_WORD> 어떻게 주문해야되지요?
2	어떻	VA	O
3	게	EC	O
4	주문	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	하	XSV	O
6	아야	EC	O
7	되	VV	O
8	지요	EF	O
9	?	SF	O

; {row.Dictionary.word.upper()} 주문은 어떻게 해요?
$<{row.Dictionary.word.upper()}:CK_WORD> 주문은 어떻게 해요?
2	주문	NNP	O
3	은	JX	O
4	어떻	VA	O
5	게	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	하	VX	O
7	아요	EF	O
8	?	SF	O

; {row.Dictionary.word.upper()} 사전주문가능한가요?
$<{row.Dictionary.word.upper()}:CK_WORD> 사전주문가능한가요?
2	사전	NNP	O
3	주문	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	가능	XR	O
5	하	XSA	O
6	ㄴ가요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 미리 주문할수있나요?
$<{row.Dictionary.word.upper()}:CK_WORD> 미리 주문할수있나요?
2	미리	MAG	O
3	주문	NNG	O
4	하	XSV	O
5	ㄹ	ETM	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	수	NNB	O
7	있	VX	O
8	나요	EF	O
9	?	SF	O

; {row.Dictionary.word.upper()} 미리 주문가능할까요?
$<{row.Dictionary.word.upper()}:CK_WORD> 미리 주문가능할까요?
2	미리	MAG	O
3	주문	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	가능	XR	O
5	하	XSA	O
6	ㄹ까요	EF	O
7	?	SF	O

; {row.Dictionary.word.upper()} 주문해주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문해주세요
2	주문	NNG	O
3	하	XSV	O
4	아	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	주	VX	O
6	시	EP	O
7	어요	EC	O

; {row.Dictionary.word.upper()} 주문하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하고싶어요
2	주문	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	하	XSV	O
4	고	EC	O
5	싶	VX	O
6	어요	EC	O

; {row.Dictionary.word.upper()} 주문하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하고싶어요
2	주문	NNG	O
3	하	XSV	O
4	고	EC	O
5	싶	VX	O
6	어요	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 주문 하는법 알려주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 하는법 알려주세요
2	주문	NNP	O
3	하	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	는	ETM	O
5	법	NNB	O
6	알리	VV	O
7	어	EC	O
8	주	VX	O
9	시	EP	O
10	어요	EC	O

; {row.Dictionary.word.upper()} 주문 잡고 싶은데요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 잡고 싶은데요
2	주문	NNP	O
3	잡	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	고	EC	O
5	싶	VX	O
6	은데	EC	O
7	요	JX	O

; {row.Dictionary.word.upper()} 주문 가능 여부
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 가능 여부
2	주문	NNP	O
3	가능	XR	O
4	여부	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 주문 가능한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 가능한가요
2	주문	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	가능	XR	O
4	하	XSA	O
5	ㄴ	ETM	O
6	가요	NNP	O

; {row.Dictionary.word.upper()} 주문 관련 문의드립니다
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 관련 문의드립니다
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	주문	NNP	O
3	관련	NNG	O
4	문의	NNG	O
5	드리	VV	O
6	ㅂ니다	EC	O

; {row.Dictionary.word.upper()} 주문 하까 마까?
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 하까 마까?
2	주문	NNP	O
3	하	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	까	EC	O
5	마	NNG	O
6	까	NNP	O
7	?	SF	O

; {row.Dictionary.word.upper()} 주문하까?
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하까?
2	주문	NNG	O
3	하	XSV	O
4	까	EF	O
5	?	SF	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 주문 관련 문의하고 싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 관련 문의하고 싶어요
2	주문	NNP	O
3	관련	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	문의	NNG	O
5	하	XSV	O
6	고	EC	O
7	싶	VX	O
8	어요	EC	O

; {row.Dictionary.word.upper()} 음식 주문하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 음식 주문하고싶어요
2	음식	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	주문	NNG	O
4	하	XSV	O
5	고	EC	O
6	싶	VX	O
7	어요	EC	O

; {row.Dictionary.word.upper()} 주문문의요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문문의요
2	주문	NNG	O
3	문의	NNG	O
4	요	JX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 인터넷으로 주문할수 잇나요
$<{row.Dictionary.word.upper()}:CK_WORD> 인터넷으로 주문할수 잇나요
2	인터넷	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	으로	JKB	O
4	주문	NNG	O
5	하	XSV	O
6	ㄹ	ETM	O
7	수	NNB	O
8	잇	VV	O
9	나요	EC	O

; {row.Dictionary.word.upper()} 최대한 빨리 주문할수 있는 방법이 있나요
$<{row.Dictionary.word.upper()}:CK_WORD> 최대한 빨리 주문할수 있는 방법이 있나요
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	최대한	NNG	O
3	빨리	MAG	O
4	주문	NNG	O
5	하	XSV	O
6	ㄹ	ETM	O
7	수	NNB	O
8	있	VV	O
9	는	ETM	O
10	방법	NNG	O
11	이	JKS	O
12	있	VV	O
13	나요	EC	O

; {row.Dictionary.word.upper()} 주문빨리하고싶어요!
$<{row.Dictionary.word.upper()}:CK_WORD> 주문빨리하고싶어요!
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
2	주문	NNG	O
3	빨리	MAG	O
4	하	XSV	O
5	고	EC	O
6	싶	VX	O
7	어요	EF	O
8	!	SF	O

; {row.Dictionary.word.upper()} 주문접수받아줘
$<{row.Dictionary.word.upper()}:CK_WORD> 주문접수받아줘
2	주문	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	접수	NNG	O
4	받	VV	O
5	아	EC	O
6	주	VX	O
7	어	EC	O

; {row.Dictionary.word.upper()} 주문가능한 수단 다 가르쳐줘
$<{row.Dictionary.word.upper()}:CK_WORD> 주문가능한 수단 다 가르쳐줘
2	주문	NNG	O
3	가능	XR	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	하	XSA	O
5	ㄴ	ETM	O
6	수단	NNG	O
7	다	MAG	O
8	가르치	VV	O
9	어	EC	O
10	주	VX	O
11	어	EC	O

; {row.Dictionary.word.upper()} 메뉴 주문해주세요
$<{row.Dictionary.word.upper()}:CK_WORD> 메뉴 주문해주세요
2	메뉴	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	주문	NNG	O
4	하	XSV	O
5	아	EC	O
6	주	VX	O
7	시	EP	O
8	어요	EC	O

; {row.Dictionary.word.upper()} 인터넷으로 주문할수 있나요
$<{row.Dictionary.word.upper()}:CK_WORD> 인터넷으로 주문할수 있나요
2	인터넷	NNG	O
3	으로	JKB	O
4	주문	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	하	XSV	O
6	ㄹ	ETM	O
7	수	NNB	O
8	있	VV	O
9	나요	EC	O

; {row.Dictionary.word.upper()} 주문하게 전화번호 줘
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하게 전화번호 줘
2	주문	NNG	O
3	하	XSV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	게	EC	O
5	전화번호	NNP	O
6	주	VX	O
7	어	EC	O

; {row.Dictionary.word.upper()} 주문하려고하는데 어디 전화하면되죠
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하려고하는데 어디 전화하면되죠
2	주문	NNG	O
3	하	XSV	O
4	려고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	하	VX	O
6	는데	EC	O
7	어디	NP	O
8	전화	NNG	O
9	하	XSV	O
10	면	EC	O
11	되	VV	O
12	죠	EC	O

; {row.Dictionary.word.upper()} 주문하고싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하고싶어요
2	주문	NNG	O
3	하	XSV	O
4	고	EC	O
5	싶	VX	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	어요	EC	O

; {row.Dictionary.word.upper()} 진료 주문 방법
$<{row.Dictionary.word.upper()}:CK_WORD> 진료 주문 방법
2	진료	NNG	O
3	주문	NNP	O
4	방법	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

; {row.Dictionary.word.upper()} 주문하는데 오늘 가도 되나요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하는데 오늘 가도 되나요
2	주문	NNG	O
3	하	XSV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
4	는데	EC	O
5	오늘	NNG	O
6	가도	NNP	O
7	되	VV	O
8	나요	EC	O

; {row.Dictionary.word.upper()} 지금 음식 받을수 있나요
$<{row.Dictionary.word.upper()}:CK_WORD> 지금 음식 받을수 있나요
2	지금	MAG	O
3	음식	NNG	O
4	받	VV	O
5	을	ETM	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	수	NNB	O
7	있	VV	O
8	나요	EC	O

; {row.Dictionary.word.upper()} 주문할수 있나요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문할수 있나요
2	주문	NNG	O
3	하	XSV	O
4	ㄹ	ETM	O
5	수	NNB	O
6	있	VV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
7	나요	EC	O

; {row.Dictionary.word.upper()} 주문하고 싶어요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하고 싶어요
2	주문	NNG	O
3	하	XSV	O
4	고	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	싶	VX	O
6	어요	EC	O

; {row.Dictionary.word.upper()} 주문 카톡으로 진행할께요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 카톡으로 진행할께요
2	주문	NNP	O
3	카	MAG	O
4	톡	MAG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	으로	JKB	O
6	진행	NNG	O
7	하	XSV	O
8	ㄹ께	EC	O
9	요	JX	O

; {row.Dictionary.word.upper()} 음식 주문 톡으로도 가능할지?
$<{row.Dictionary.word.upper()}:CK_WORD> 음식 주문 톡으로도 가능할지?
2	음식	NNG	O
3	주문	NNP	O
4	톡	MAG	O
5	으로	JKB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	도	JX	O
7	가능	XR	O
8	하	XSA	O
9	ㄹ지	EF	O
10	?	SF	O

; {row.Dictionary.word.upper()} 음식 카톡으로도 주문 되나요?
$<{row.Dictionary.word.upper()}:CK_WORD> 음식 카톡으로도 주문 되나요?
2	음식	NNG	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
3	카	MAG	O
4	톡	MAG	O
5	으로	JKB	O
6	도	JX	O
7	주문	NNP	O
8	되	VV	O
9	나요	EF	O
10	?	SF	O

; {row.Dictionary.word.upper()} 메뉴 카톡으로도 주문 되나요?
$<{row.Dictionary.word.upper()}:CK_WORD> 메뉴 카톡으로도 주문 되나요?
2	메뉴	NNP	O
3	카	MAG	O
4	톡	MAG	O
5	으로	JKB	O
6	도	JX	O
7	주문	NNP	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
8	되	VV	O
9	나요	EF	O
10	?	SF	O

; {row.Dictionary.word.upper()} 음식 주문 가능한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 음식 주문 가능한가요
2	음식	NNG	O
3	주문	NNP	O
4	가능	XR	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	하	XSA	O
6	ㄴ	ETM	O
7	가요	NNP	O

; {row.Dictionary.word.upper()} 메뉴 주문 가능한가요
$<{row.Dictionary.word.upper()}:CK_WORD> 메뉴 주문 가능한가요
3	주문	NNP	O
2	메뉴	NNP	O
4	가능	XR	O
5	하	XSA	O
6	ㄴ	ETM	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
7	가요	NNP	O

; {row.Dictionary.word.upper()} 주문하고싶은데 진행을 어떻게 하면 되나요
$<{row.Dictionary.word.upper()}:CK_WORD> 주문하고싶은데 진행을 어떻게 하면 되나요
2	주문	NNG	O
3	하	XSV	O
4	고	EC	O
5	싶	VX	O
6	은데	EC	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
7	진행	NNG	O
8	을	JKO	O
9	어떻	VA	O
10	게	EC	O
11	하	VV	O
12	면	EC	O
13	되	VV	O
14	나요	EC	O

; {row.Dictionary.word.upper()} 방문이나 전화로 주문가능합니까?
$<{row.Dictionary.word.upper()}:CK_WORD> 방문이나 전화로 주문가능합니까?
2	방문	NNG	O
3	이나	JC	O
4	전화	NNG	O
5	로	JKB	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
6	주문	NNG	O
7	가능	XR	O
8	하	XSA	O
9	ㅂ니까	EF	O
10	?	SF	O

; {row.Dictionary.word.upper()} 주문 오케?
$<{row.Dictionary.word.upper()}:CK_WORD> 주문 오케?
2	주문	NNP	O
3	오	NNG	O
4	하	XSV	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD
5	게	EF	O
6	?	SF	O

; {row.Dictionary.word.upper()} 여기서 주문 가능
$<{row.Dictionary.word.upper()}:CK_WORD> 여기서 주문 가능
2	여기	NP	O
3	서	JKB	O
4	주문	NNP	O
5	가능	XR	O
1	{row.Dictionary.word.upper()}	NNG	CK_WORD

""")

pass