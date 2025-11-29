from fastapi import FastAPI, Depends, HTTPException, status
from database import Base, engine, get_db
from schemas import BookOut, BookUpdate, BookCreate
from sqlalchemy.orm import Session
import models


app = FastAPI()


@app.get("/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books


@app.get("/books/{id}", response_model=BookOut)
def get_book_by_id(id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return db_book


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


@app.put("/books/{id}", response_model=BookOut)
def update_book(id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )

    db_book.title = book.title
    db_book.author = book.author

    db.commit()
    db.refresh(db_book)

    return db_book


@app.patch("/books/{id}", response_model=BookOut)
def patch_book(id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )

    update_data = book.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )

    db.delete(db_book)
    db.commit()

    return None
