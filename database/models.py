from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, relationship, backref

from .database import Base, engine


class Book(Base):
   __tablename__ = 'books'
   id = Column(Integer, primary_key=True, nullable=False, index=True)
   name = Column(String(50))
   author_id = Column(Integer, ForeignKey('authors.id', ondelete='CASCADE'), nullable=False, unique=True)
   author = relationship('Author', back_populates='book')


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String(50))
    book = relationship('Book', uselist=False, back_populates='author', lazy=True, cascade='all, delete-orphan')


Base.metadata.create_all(bind=engine)
