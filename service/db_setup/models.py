from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base


Base = declarative_base()



class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=True)
    active = Column(Integer, nullable=False, default=1)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=True)
    correct = Column(Integer, default=0)
    question = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Integer, nullable=False, default=1)

