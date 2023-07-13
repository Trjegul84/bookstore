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


class DbSession:
    @staticmethod
    def create():
        db = session()
        try:
            yield DbSession(db)
        finally:
            db.close()

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_items(self, model: Base):
        return self.db.query(model).all()

    async def filter_items(self, model: Base, **filter):
        obj = self.db.query(model)

        for attr, value in filter.items():
            return obj.filter(getattr(model, attr).like("%%%s%%" % value))

    async def get_item(self, model: Base, id: int):
        return self.db.query(model).filter(model.id == id).first()

    async def create_item(self, model: Base):
        self.db.add(model)
        try:
            self.db.commit()
        except IntegrityError as exc:
            raise DatabaseIntegrityError from exc

        self.db.refresh(model)
        return model

    async def update_item(self, model: Base, input_model: BaseModel, id: int):
        obj = self.db.get(model, id)
        if not obj:
            return

        data = input_model.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(obj, key, value)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    async def delete_item(self, model: Base, id: int):
        item = await self.get_item(model, id)
        if not item:
            raise DatabaseItemNotFound()
        self.db.delete(item)
        self.db.commit()
