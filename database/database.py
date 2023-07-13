import os

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prod.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DatabaseIntegrityError(Exception):
    pass


class DatabaseItemNotFound(Exception):
    pass


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


class DbSession:
    @staticmethod
    def create():
        db = session()
        try:
            yield DbSession(db)
        finally:
            db.close()

    def __init__(self, db) -> None:
        self.db = db

    async def create_db_item(self, model: Base):
        self.db.add(model)
        try:
            self.db.commit()
        except IntegrityError as exc:
            raise DatabaseIntegrityError from exc

        self.db.refresh(model)
        return model


async def get_db_items(db: Session, model: Base):
    return db.query(model).all()


async def filter_db_items(db: Session, model: Base, **filter):
    obj = db.query(model)

    for attr, value in filter.items():
        return obj.filter(getattr(model, attr).like("%%%s%%" % value))


async def get_db_item(db: Session, model: Base, id: int):
    return db.query(model).filter(model.id == id).first()


async def create_db_item(db: Session, model: Base):
    db.add(model)
    try:
        db.commit()
    except IntegrityError as exc:
        raise DatabaseIntegrityError from exc

    db.refresh(model)
    return model


async def update_db_item(db: Session, model: Base, input_model: BaseModel, id: int):
    obj = db.get(model, id)
    if not obj:
        return

    data = input_model.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(obj, key, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


async def delete_db_item(db: Session, model: Base, id: int):
    item = await get_db_item(db, model, id)
    if not item:
        raise DatabaseItemNotFound()
    db.delete(item)
    db.commit()
