from pydantic import BaseModel


class ChatResponse(BaseModel):
    Query: str
    Answer: str
    keyword: str
    keyword_answer: str
    NER: str
    url: str | None
    usruse: int
    category: str
    input: str
    depth: int
    parent_idx: int | None
