from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from enum import Enum
from pydantic import BaseModel, Field, conlist


class UserInput(BaseModel):
    username: str


class AnswersList(BaseModel):
    answers: List[int] = Field(default_factory=list, min_items=1)


class QuestionOrderSchema(str, Enum):
    id = "id"
    active = "active"
    updated_dt = "updated_dt"


class QuestionListRequest(BaseModel):
    text: Optional[str] = Field(
        example="question", description="search by text", default=None
    )
    active: Optional[int] = Field(
        example=1, description="if question is active", default=1
    )
    order: Optional[QuestionOrderSchema] = Field(
        example="updated_dt", description="order of results", default="id"
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

    class Config:
        schema_extra = {
            "example": {
                "text": "question1",
                "active": 1,
                "id": None,
            }
        }


class QuestionEditRequest(BaseModel):
    id: int = Field(description="id of question")
    text: Optional[str] = Field(description="text", min_length=1, max_length=255)
    active: Optional[int] = Field(description="if question is active")

    class Config:
        schema_extra = {
            "example": {
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
    updated_dt: datetime = Field(
        example="2024-09-10T08:19:54.531503+00:00", description="date"
    )


class QuizListResponse(BaseModel):
    id: int = Field(example=1, description="id of question")
    text: str = Field(example="question 1", description="text")
    active: int = Field(example=1, description="if question is active")
    answers: List[Any]


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


class AnswerInResponse(BaseModel):
    id: int
    text: str
    correct: bool


class QuestionResponseInQuiz(BaseModel):
    id: int
    text: str
    active: int
    answers: List[AnswerInResponse]


class QuizResponse(BaseModel):
    __root__: Dict[str, QuestionResponseInQuiz]
