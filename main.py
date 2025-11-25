from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import func

app = FastAPI()

sqlite_url = "sqlite:///./books.db"
engine = create_engine(sqlite_url, echo=False)


class Book(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    author: str


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=100)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


init_db()


@app.get("/")
def homepage():
    return {"message": "This is your homepage"}


@app.get("/books")
def list_books(
    author: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
):
    query = select(Book)
    if author:
        query = query.where(func.lower(Book.author).like(f"%{author.lower()}%"))
    all_matches = session.exec(query).all()
    items = all_matches[skip : skip + limit]
    return {"items": items, "total": len(all_matches)}


@app.post("/books", status_code=201)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Book).where(func.lower(Book.title) == book.title.lower())
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book title already exists")
    db_book = Book(**book.model_dump())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books/{book_id}")
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    conflict = session.exec(
        select(Book).where(Book.id != book_id, func.lower(Book.title) == book.title.lower())
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Book title already exists")
    db_book.title = book.title
    db_book.author = book.author
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.patch("/books/{book_id}")
def partial_update_book(
    book_id: int, book: BookUpdate, session: Session = Depends(get_session)
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book.model_dump(exclude_unset=True)
    if "title" in book_data:
        conflict = session.exec(
            select(Book).where(
                Book.id != book_id,
                func.lower(Book.title) == book_data["title"].lower(),
            )
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Book title already exists")
        db_book.title = book_data["title"]
    if "author" in book_data:
        db_book.author = book_data["author"]
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(db_book)
    session.commit()
    return
