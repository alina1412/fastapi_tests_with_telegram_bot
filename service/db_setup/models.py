from datetime import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text as sa_text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declarative_base,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from service.config import utcnow


class Base(DeclarativeBase):
    pass


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""

    pass


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(50), nullable=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    answers = relationship("Answer", backref="questions")
    # answers: Mapped[List["Answer"]] = relationship()
    updated_dt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default_factory=utcnow,
        server_default=sa_text("TIMEZONE('utc', now())"),
        onupdate=sa_text("TIMEZONE('utc', now())"),
    )


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=True)
    correct = Column(Boolean, default=0)
    # question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Integer, nullable=False, default=1)


# create_engine
# Base.metadata.create_all()
