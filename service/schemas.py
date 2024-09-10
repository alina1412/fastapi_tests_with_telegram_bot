from datetime import datetime
from typing import List, Optional, Union

from enum import Enum
from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str


class AnswersList(BaseModel):
    answers: List[int] = Field(default_factory=list, min_items=1)


class QuestionOrderSchema(str, Enum):
    id = "id"
    active = "active"


class QuestionListRequest(BaseModel):
    text: Optional[str] = Field(
        example="question 1", description="search by text", default=None
    )
    active: Optional[int] = Field(
        example=1, description="if question is active", default=1
    )
    order: Optional[QuestionOrderSchema] = Field(
        example="id", description="order of results", default="id"
    )
    offset: Optional[int] = Field(
        example=0, description="offset to show on page", default=0
    )
    limit: Optional[int] = Field(
        example=50, description="limit to show on page", default=50
    )


class QuestionAddRequest(BaseModel):
    text: str = Field(description="text", min_length=1, max_length=255)
    active: Optional[int] = Field(description="if question is active", default=1)

    # edit_date: datetime.datetime = Field(
    #     example="2022-01-05T16:41:24+03:30", description="date"
    # )

    class Config:
        schema_extra = {
            "example": {
                # "edit_date": "2022-01-05T16:41:24+03:30",
                "text": "question1",
                "active": 1,
                "id": None,
            }
        }


class QuestionEditRequest(BaseModel):
    id: int = Field(description="id of question")
    text: Optional[str] = Field(description="text", min_length=1, max_length=255)
    active: Optional[int] = Field(description="if question is active")

    # edit_date: datetime.datetime = Field(
    #     example="2022-01-05T16:41:24+03:30", description="date"
    # )

    class Config:
        schema_extra = {
            "example": {
                # "edit_date": "2022-01-05T16:41:24+03:30",
                "text": "question1",
                "active": 1,
                "id": None,
            }
        }


class QuestionResponse(BaseModel):
    """
    Schema for output.
    """

    id: int = Field(example=1, description="id of question")
    text: str = Field(example="question 1", description="text")
    active: int = Field(example=1, description="if question is active")
    updated_dt: datetime


class AnswerRequest(BaseModel):
    """
    Schema for input.
    """

    id: Optional[int] = Field(example=1, description="id of answer", default=None)
    text: str = Field(
        example="answer 1", description="text", min_length=1, max_length=50
    )
    correct: bool = Field(example=True, description="if answer is correct")
    question_id: int = Field(example=1, description="id of question")


class AnswerAddRequest(BaseModel):
    """
    Schema for input.
    """

    text: str = Field(
        example="answer 1", description="text", min_length=1, max_length=50
    )
    correct: bool = Field(example=True, description="if answer is correct")
    question_id: int = Field(example=1, description="id of question")


class AnswerSubmitRequest(BaseModel):
    question_id: int = Field(example=1, description="id of question")
    answer_ids: AnswersList


class AnswerResponse(BaseModel):
    """
    Schema for output.
    """

    id: int = Field(example=1, description="id of answer")
    text: str = Field(example="question 1", description="text")
    correct: bool = Field(example=True, description="if answer is correct")
    question_id: int = Field(example=1, description="id of question")
