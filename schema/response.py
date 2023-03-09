from pydantic import BaseModel


class ChatResponse(BaseModel):
    Query: str
    Answer: str
    keyword: list | None
    keyword_answer: str | None
    NER: str | None
    url: str | None
    usruse: str | None
    category: str | None
    input: str | None
    depth: int | None
    parent_idx: int | None
