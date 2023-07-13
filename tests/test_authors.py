from unittest.mock import ANY

from fastapi.testclient import TestClient
import pytest

from app.main import app
from database.database import Base, engine


@pytest.fixture
def client(tmp_path):
    override_db()
    return TestClient(app)


def override_db():
    with engine.connect() as connection, connection.begin():
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


def create_author(client, name):
    author = {'name': name}
    response = client.post('/authors', json=author)
    return response.json()


def test_create_author(client):
    author = create_author(client, "Stephen King")
    response = client.post('/authors', json=author)
    assert response.status_code == 200
    assert response.json() == dict(author, id=ANY)


def test_get_author_by_id(client):
    author_id = create_author(client, "Arthur C. Clarke")["id"]
    response = client.get(f'/authors/{author_id}')
    assert response.status_code == 200
    assert response.json() == dict(name="Arthur C. Clarke", id=author_id)


def test_get_author_does_no_exist(client):
    author_id = create_author(client, "Arthur C. Clarke")["id"] + 1
    response = client.get(f'/authors/{author_id}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Author not found'}


def test_list_authors(client):
    author_id = create_author(client, "Isaac Asimov")["id"]
    response = client.get('/authors')
    assert response.status_code == 200
    assert response.json() == [dict(name="Isaac Asimov", id=author_id)]


def test_update_author(client):
    author_id = create_author(client, "Stephen King")["id"]
    alter_author = {'name': 'Stephen Hopkins'}
    response = client.patch(f'/authors/{author_id}', json=alter_author)
    assert response.status_code == 200
    assert response.json() == dict(name="Stephen Hopkins", id=author_id)


def test_update_author_does_not_exist(client):
    author_id = create_author(client, "William Gibson")["id"] + 1
    alter_author = {'name': 'William Ford Gibson'}
    response = client.patch(f'/authors/{author_id}', json=alter_author)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Author not found'}


def test_delete_author(client):
    author_id = create_author(client, "Stephen King")["id"]
    response = client.delete(f'/authors/{author_id}')
    assert response.status_code == 200
    assert response.json() == {"delete status": "success"}


def test_delete_author_does_not_exist(client):
    author_id = create_author(client, "Stephen King")["id"] + 1
    response = client.delete(f'/authors/{author_id}')
    assert response.status_code == 400
    assert response.json() == {"detail": "Author does not exist"}


def create_book(client, name, author):
    author_id = create_author(client, author)["id"]
    data = {'name': name, "author_id": author_id}
    response = client.post('/books', json=data)
    return response.json()


def test_list_all_books(client):
    book1 = create_book(client, "Rama", "Arthur C. Clarke")
    book2 = create_book(client, "Tales", "J.P. Lovecraft")
    response = client.get(f"/books")
    assert response.status_code == 200
    assert response.json() == [
        dict(id=book1["id"], name=book1["name"], author_id=book1["author_id"]),
        dict(id=book2["id"], name=book2["name"], author_id=book2["author_id"])
    ]


def test_list_books_by_author(client):
    book = create_book(client, "Rama", "Arthur C. Clarke")
    book2 = create_book(client, "Tales", "J.P. Lovecraft")
    book_id = book["id"]
    author_id = book["author_id"]
    response = client.get(f"/books/?author_id={author_id}")
    assert response.status_code == 200
    assert response.json() == [dict(id=book_id, name=book["name"], author_id=author_id)]


def test_list_authors_can_have_one_book(client):
    book1 = create_book(client, "Carrie", "Stephen King")
    book2_data = { "name": "El Resplandor", "author_id": book1["author_id"]}
    response = client.post(f"/books", json=book2_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Author can have only one book"}
