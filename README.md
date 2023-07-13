# Simple REST application with Fast API and SQlite

CRUD operations on bookstore database with authors and books.

Endpoints for authors:

- GET `/authors`
- GET `/authors/{id}`
- POST `/authors`
- PATCH `/authors/{id}`
- DELETE `/authors/{id}`

Endpoints for books:

- GET `/books/?author_id={author_id}` (optional filter author_id )
- GET `/books/{id}`
- POST `/books`
- PATCH `/books/{id}`
- DELETE `/books/{id}`

## Prerequisites

python +3.9

## Setup

Follow this instructions to run locally.

1. Clone this repository

2. Create a python virtual environment:

```
python -m venv .venv
```

3. Activate the virtual environment:

```
source .venv/bin/activate
```

4. Update pip

```
pip install --upgrade pip

```

5. Install [Python library dependencies](requirements.txt):

```
pip install -r requirements.txt
```

6. Before start the application set the following environment variable:

```
export DATABASE_URL='sqlite:///./prod.db'
```

## Usage

1. Start the application

```
uvicorn app.main:app --reload
```

To run the application with a specific database start it using:

```
DATABASE_URL='sqlite:///./database_name.db' uvicorn app.main:app --reload
```

2. Open the http://127.0.0.1:8000  url in the browser

## Docker

The application can be run within a docker container:

**Prerequisite:** Docker version 20.10+


1. Build the image

```
docker build -t bookstore_image .
```

2. Run the container

```
docker run -d --name bookstore_api -p 8000:8000 bookstore_image
```

## Tests


To run all tests, execute from the root directory of the repository:

```
DATABASE_URL="sqlite:///./test.db"  pytest -vvv
```

### Coverage

To check the coverage with a nice html view:

1. `DATABASE_URL="sqlite:///./test.db" coverage run -m pytest -v`

2. `coverage html`

3. Open the generated html report (`/bookstore/htmlcov/index.html`) in the browser


## References

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/faq/sessions.html)
- [SQL and FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/update/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Pytest](https://docs.pytest.org/en/stable/index.html)

## Author

- **Angela Checa** - [Trjegul84](https://github.com/Trjegul84)
