from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Deep Work", "author": "Cal Newport"},
    {"id": 3, "title": "Atomic Habits", "author": "James Clear"},
]


@app.get("/")
def homepage():
    return {"message": "This is your homepage"}


@app.get("/books")
def list_books(author: str | None = None, skip: int = 0, limit: int = 10):
    filtered = BOOKS
    if author:
        filtered = [book for book in BOOKS if author.lower() in book["author"].lower()]
    return {"items": filtered[skip : skip + limit], "total": len(filtered)}


class BookCreate(BaseModel):
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    new_id = BOOKS[-1]["id"] + 1 if BOOKS else 1
    new_book = {"id": new_id, **book.model_dump()}
    BOOKS.append(new_book)
    return new_book


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(BOOKS):
        if existing_book["id"] == book_id:
            updated = {"id": book_id, **book.model_dump()}
            BOOKS[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Book not found")


@app.patch("/books/{book_id}")
def partial_update_book(book_id: int, book: BookUpdate):
    for index, existing_book in enumerate(BOOKS):
        if existing_book["id"] == book_id:
            book_data = book.model_dump(exclude_unset=True)
            BOOKS[index] = {**existing_book, **book_data}
            return BOOKS[index]
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for index, existing_book in enumerate(BOOKS):
        if existing_book["id"] == book_id:
            BOOKS.pop(index)
            return
    raise HTTPException(status_code=404, detail="Book not found")
