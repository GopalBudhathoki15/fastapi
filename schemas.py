from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    author: str
    title: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None


class BookOut(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
