from fastapi import FastAPI
from pydantic import BaseModel

class StringRequest(BaseModel):
    value: str


class filterRequest(BaseModel):
    is_palindrome: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    word_count: int | None = None
    contains_character: str | None = None