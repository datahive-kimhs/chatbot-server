import openpyxl
import pandas as pd
import csv

from typing import Any
import logging

from sqlalchemy import select, update, delete

from core import ckline_db
from models.dictionary_ja import Dictionaryja


def make_train_ja():
    with ckline_db.get_db_session() as session:
        stmt = select(Dictionaryja)
        rows = session.execute(stmt).all()

        with open("ner/ner_train_ja.txt", 'w', encoding='utf-8', newline='') as f:
            for row in rows:      
                f.write(f"""; {row.Dictionaryja.word.upper()} 照会したいです
$<{row.Dictionaryja.word.upper()}:CK_WORD> 照会したいです
1	{row.Dictionaryja.word.upper()}	名詞    CK_WORD
2	照会    名詞	O
3	し  動詞	O
4	た  助動詞  O
5	です    助動詞	O

; {row.Dictionaryja.word.upper()} 食べたいです
$<{row.Dictionaryja.word.upper()}:CK_WORD> 食べたいです
2	食べ	動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
3	たい	助動詞	O
4	です	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

; {row.Dictionaryja.word.upper()} したいです
$<{row.Dictionaryja.word.upper()}:CK_WORD> したいです
2	し	動詞	O
3	たい	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
4	です	助動詞	O

; {row.Dictionaryja.word.upper()} 欲しいです
$<{row.Dictionaryja.word.upper()}:CK_WORD> 欲しいです
2	欲しい	形容詞	O
3	です	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

; {row.Dictionaryja.word.upper()} どうすればいいですか?
$<{row.Dictionaryja.word.upper()}:CK_WORD> どうすればいいですか?
2	どう	副詞	O
3	すれ	動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
4	ば	助詞	O
5	いい	形容詞	O
6	です	助動詞	O
7	か	助詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
8	?   補助記号    O

; {row.Dictionaryja.word.upper()} どうすればいいんだ
$<{row.Dictionaryja.word.upper()}:CK_WORD> どうすればいいんだ
2	どう	副詞	O
3	すれ	動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
4	ば	助詞	O
5	いい	形容詞	O
6	ん	助詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
7	だ	助動詞	O

; {row.Dictionaryja.word.upper()} やりたいんだけど
$<{row.Dictionaryja.word.upper()}:CK_WORD> やりたいんだけど
2	やり	動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
3	たい	助動詞	O
4	ん	助詞	O
5	だ	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
6   けど	助詞	O

; {row.Dictionaryja.word.upper()} 教えて
$<{row.Dictionaryja.word.upper()}:CK_WORD> 教えて
2	教え	動詞	O
3	て	助詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

; {row.Dictionaryja.word.upper()} やりたい
$<{row.Dictionaryja.word.upper()}:CK_WORD> やりたい
2	やり	動詞	O
3	たい	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

; {row.Dictionaryja.word.upper()} やりたいんだけど
$<{row.Dictionaryja.word.upper()}:CK_WORD> やりたいんだけど
2	やり	動詞	O
3	たい	助動詞	O
4	ん	助詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
5	だ	助動詞	O
6	けど	助詞	O

; {row.Dictionaryja.word.upper()} やります
$<{row.Dictionaryja.word.upper()}:CK_WORD> やります
2	やり	動詞	O
3	ます	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

; {row.Dictionaryja.word.upper()} 助けてく
$<{row.Dictionaryja.word.upper()}:CK_WORD> 助けてく
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD
2	助け	動詞	O
3	てく	助動詞	O
1	{row.Dictionaryja.word.upper()}	名詞	CK_WORD

""")

pass