from pydantic import BaseModel


class BookBase(BaseModel):
    author: str
    title: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    author:str|None = None
    title:str|None = None


class BookOut(BookBase):
    id:int

    class Config:
        orm_mode = True