from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient

from app.main import app
from database.database import Base, engine


@pytest.fixture
def client(tmp_path):
    clear_db()
    return TestClient(app)


def clear_db():
    with engine.connect() as connection, connection.begin():
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


def create_author(client, name):
    author = {"name": name}
    response = client.post("/authors", json=author)
    return response.json()


def test_create_author(client):
    author = {"name": "William Shakespeare"}
    response = client.post("/authors", json=author)
    assert response.status_code == 200
    assert response.json() == dict(author, id=ANY)


def test_get_author_by_id(client):
    author = create_author(client, "Arthur C. Clarke")
    response = client.get(f"/authors/{author['id']}")
    assert response.status_code == 200
    assert response.json() == author


def test_get_author_does_no_exist(client):
    author_id = create_author(client, "Arthur C. Clarke")["id"] + 1
    response = client.get(f"/authors/{author_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found"}


def test_list_authors(client):
    author1 = create_author(client, "Isaac Asimov")
    author2 = create_author(client, "Arthur C. Clarke")
    response = client.get("/authors")
    assert response.status_code == 200
    assert response.json() == [author1, author2]


def test_update_author(client):
    author_id = create_author(client, "Stephen King")["id"]
    altered_author = {"name": "Stephen Hopkins"}
    response = client.patch(f"/authors/{author_id}", json=altered_author)
    assert response.status_code == 200
    assert response.json() == dict(altered_author, id=author_id)


def test_update_author_does_not_exist(client):
    author_id = create_author(client, "William Gibson")["id"] + 1
    altered_author = {"name": "William Ford Gibson"}
    response = client.patch(f"/authors/{author_id}", json=altered_author)
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found"}


def test_delete_author(client):
    author_id = create_author(client, "Stephen King")["id"]
    response = client.delete(f"/authors/{author_id}")
    assert response.status_code == 204


def test_delete_author_does_not_exist(client):
    author_id = create_author(client, "Stephen King")["id"] + 1
    response = client.delete(f"/authors/{author_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Author does not exist"}


def create_book(client, name, author):
    author_id = create_author(client, author)["id"]
    data = {"name": name, "author_id": author_id}
    response = client.post("/books", json=data)
    return response.json()


def test_create_book_error_when_author_does_not_exists(client):
    data = {"name": "Book title", "author_id": 123}
    response = client.post("/books", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Author does not exist"}


def test_list_all_books(client):
    book1 = create_book(client, "Rama", "Arthur C. Clarke")
    book2 = create_book(client, "Tales", "J.P. Lovecraft")
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == [book1, book2]


def test_list_books_by_author(client):
    book = create_book(client, "Rama", "Arthur C. Clarke")
    create_book(client, "Tales", "J.P. Lovecraft")
    response = client.get(f"/books/?author_id={book['author_id']}")
    assert response.status_code == 200
    assert response.json() == [book]


def test_list_authors_can_have_one_book(client):
    book1 = create_book(client, "Carrie", "Stephen King")
    book2 = {"name": "El Resplandor", "author_id": book1["author_id"]}
    response = client.post("/books", json=book2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Author can have only one book"}
