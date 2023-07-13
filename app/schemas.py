from pydantic import BaseModel


class BookIn(BaseModel):
    name: str
    author_id: int

    class ConfigDict:
        orm_mode = True


class BookOut(BaseModel):
    id: int
    name: str
    author_id: int

    class ConfigDict:
        orm_mode = True


class AuthorIn(BaseModel):
    name: str


class AuthorOut(BaseModel):
    id: int
    name: str

    class ConfigDict:
        orm_mode = True
