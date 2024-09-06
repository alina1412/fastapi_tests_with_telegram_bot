import sqlalchemy as sa

# from sqlalchemy import select, update, or_, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import lazyload, joinedload, load_only

from service.db_setup.models import Answer, User, Question
from service.schemas import QuestionListRequest


class QuestionDb:
    session = None

    def __init__(self, session) -> None:
        self.session = session

    async def add_question(self, vals):
        q = insert(Question).values(**vals).on_conflict_do_nothing()
        result = await self.session.execute(q)
        if result.rowcount:
            return result.returned_defaults[0]  # id
        return None

    async def remove_question(self, id_):
        stmt = sa.delete(Question).where(*(Question.id == id_,))
        result = await self.session.execute(stmt)
        # result.rowcount
        return

    async def deactivate_question(self, id_):
        vals = {Question.active.key: 0}
        conds = (Question.id == id_,)
        stmt = sa.update(Question).where(*conds).values(**vals).returning(Question.id)
        result = list(await self.session.execute(stmt))
        return result

    async def find_all_answers(self, q_id):
        pass

    async def find_correct_answer(self, q_id):
        q = sa.select(Answer).where(
            (Answer.question_id == q_id) & (Answer.correct == True)
        )
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_question_by_id(self, id_):
        q = sa.select(Question).where(Question.id == id_)
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_questions(self, data: QuestionListRequest):
        data = data.dict()
        order = Question.id.desc() if data["order"] == "id" else None

        q = (
            sa.select(Question)
            .where(Question.active == data["active"])
            .order_by(order)
            .limit(data["limit"])
            .offset(data["offset"])
        )
        if data["text"]:
            q = q.where(Question.text.ilike(f"%{data['text']}%"))
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_questions_with_answers(self, data: QuestionListRequest):
        data = data.dict()
        order = Question.id.desc() if data["order"] == "id" else None

        q = (
            sa.select(Question, Answer)
            .where(Question.active == data["active"])
            .order_by(order)
            .limit(data["limit"])
            .offset(data["offset"])
        )
        if data["text"]:
            q = q.where(Question.text.ilike(f"%{data['text']}%"))

        q = q.join(Answer, Question.id == Answer.question_id)
        # q = q.options(
        #         joinedload(Question.answers).options(
        #             load_only(
        #                 Answer.id,
        #                 Answer.text,
        #                 Answer.correct,
        #             )
        #         ),
        #         load_only(
        #             Question.id,
        #             Question.text,
        #             Question.active,
        #         ),)
        result = await self.session.execute(q)
        # result = result.scalars()
        # result = result.scalars().all()
        return result


class AnswerDb:
    session = None

    def __init__(self, session) -> None:
        self.session = session

    async def add_answer(self, vals):
        q = insert(Answer).values(**vals).on_conflict_do_nothing()
        result = await self.session.execute(q)
        if result.rowcount and result.returned_defaults:
            return result.returned_defaults[0]  # id
        return None

    async def remove_answer(self, id_):
        stmt = sa.delete(Answer).where(Answer.id == id_)
        result = await self.session.execute(stmt)

    async def get_answer_by_id(self, ans_id):
        q = sa.select(Answer).where(Answer.id == ans_id)
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_answers_for_question(self, q_id):
        q = sa.select(Answer).where(Answer.question_id == q_id)
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res


class UserDb:
    model = None

    def __init__(self, model) -> None:
        self.model = model

    async def select_all(self, session):
        conds = (1 == 1,)
        q = sa.select(self.model).where(*conds)
        result = await session.execute(q)
        res = result.scalars().all()
        data = [{"username": u.username, "id": u.id} for u in res]
        return data

    async def put(self, session, username, password):
        vals = {"username": username, "password": password}
        q = insert(self.model).values(**vals).on_conflict_do_nothing()

        result = await session.execute(q)
        if result.rowcount:
            return result.returned_defaults[0]  # id
        return None

    async def update(self, session):
        vals = {"id": 100, User.active.key: User.active or 0}
        conds = (
            User.id == vals["id"],
            sa.or_(
                User.active == 1,
                User.password.is_(None),
            ),
        )
        # {self.model.active.key: self.model.active or data["active"]}
        if not conds:
            conds = (1 == 1,)  # conds = (User.id == 103,)
        stmt = (
            sa.update(self.model).where(*conds).values(**vals).returning(self.model.id)
        )
        result = list(await session.execute(stmt))
        return result

    async def delete(self, session, id_):
        stmt = sa.delete(self.model).where(*(User.id == id_,))
        result = await session.execute(stmt)
        # result.rowcount
        return
