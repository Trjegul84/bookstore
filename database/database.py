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


class RecordNotFound(Exception):
    pass


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


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
    db_item = db.get(model, id)
    if not db_item:
        return

    data = input_model.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


async def delete_db_item(db: Session, model: Base, id: int):
    item = db.query(model).filter(model.id == id).first()
    db.delete(item)
    db.commit()
    return {"delete status": "success"}
