from http import HTTPStatus
from typing import List

from fastapi import Depends, HTTPException, Response
from starlette.responses import RedirectResponse

from app.main import app
from app.schemas import AuthorIn, AuthorOut, BookIn, BookOut
from database.database import (
    DatabaseIntegrityError,
    DatabaseItemNotFound,
    DbSession,
    Session,
    create_db_item,
    delete_db_item,
    filter_db_items,
    get_db,
    get_db_item,
    get_db_items,
    update_db_item,
)
from database.models import Author, Book


@app.get("/")
async def main():
    return RedirectResponse(url="/docs/")


@app.get("/authors", response_model=list[AuthorOut])
async def list_authors(db: Session = Depends(get_db)):
    return await get_db_items(db, Author)


@app.get("/authors/{id}", response_model=AuthorOut)
async def get_author_by_id(id: int, db: Session = Depends(get_db)):
    author = await get_db_item(db, Author, id)

    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.post("/authors", response_model=AuthorOut)
async def create_author(author: AuthorIn, db: DbSession = Depends(DbSession.create)):
    author_model = Author(**author.model_dump())
    return await db.create_db_item(author_model)


@app.patch("/authors/{id}", response_model=AuthorOut)
async def update_author(id: int, author: AuthorIn, db: Session = Depends(get_db)):
    db_author = await update_db_item(db, Author, author, id)

    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    return db_author


@app.delete("/authors/{id}", status_code=204, response_model=None)
async def delete_author(id: int, db: Session = Depends(get_db)):
    try:
        await delete_db_item(db, Author, id)
    except DatabaseItemNotFound:
        raise HTTPException(status_code=400, detail="Author does not exist")


@app.get("/books", response_model=list[BookOut])
async def list_books(author_id: str = None, db: Session = Depends(get_db)):
    if author_id is not None:
        return await filter_db_items(db, Book, author_id=author_id)
    return await get_db_items(db, Book)


@app.get("/books/{id}", response_model=BookOut)
async def get_book_by_id(id: str, db: Session = Depends(get_db)):
    book = await get_db_item(db, Book, id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=BookOut)
async def create_book(book: BookIn, db: Session = Depends(get_db)):
    author = await get_db_item(db, Author, book.author_id)
    if author is None:
        raise HTTPException(status_code=400, detail="Author does not exist")

    book_model = Book(**book.model_dump(exclude="author_id"), author_id=author.id)

    try:
        return await create_db_item(db, book_model)
    except DatabaseIntegrityError:
        raise HTTPException(status_code=400, detail="Author can have only one book")


@app.patch("/books/{id}", response_model=BookOut)
async def update_book(id: int, book: BookIn, db: Session = Depends(get_db)):
    db_book = await update_db_item(db, Book, book, id)

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    return db_book


@app.delete("/books/{id}", status_code=204, response_model=None)
async def delete_book(id: int, db: Session = Depends(get_db)):
    try:
        await delete_db_item(db, Book, id)
    except DatabaseItemNotFound:
        raise HTTPException(status_code=400, detail="Book does not exist")
