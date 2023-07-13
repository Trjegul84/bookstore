import sys

from fastapi import FastAPI

description = """
# Bookstore API

Bookstore application allows you to do basic querys in a Sqlite database
with two tables Authors and Books.

## Operations

List, create, update and delete books and authors.

One author can be linked to only one book.

Books can be listed and filtered by author_id
"""

app = FastAPI(
    title="Bookstore REST Api",
    description=description,
    summary="CRUD of authors and books",
    version="1.0.0",
    terms_of_service="",
    contact={
        "name": "Angela Checa",
        "url": "https://github.com/Trjegul84",
        "email": "angela@gmail.com",
    },
    license_info="",
)
