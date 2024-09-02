import sqlalchemy as sa

# from sqlalchemy import select, update, or_, delete
from sqlalchemy.dialects.postgresql import insert


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
        pass

    async def find_all_answers(self, q_id):
        pass

    async def find_correct_answer(self, q_id):
        pass

    async def get_question_by_id(self, id_):
        q = sa.select(Answer).where(Question.id == id_)
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_questions(self, data: QuestionListRequest):
        offset = data.offset or 0
        limit = data.limit or 50
        order = Question.id.desc() if data.order == "id" else None

        q = sa.select(Question).order_by(order).offset(offset).limit(limit)
        # if data.
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res


class AnswerDb:
    session = None

    def __init__(self, session) -> None:
        self.session = session

    async def add_answer(self, vals):
        q = insert(Answer).values(**vals).on_conflict_do_nothing()
        result = await self.session.execute(q)
        if result.rowcount:
            return result.returned_defaults[0]  # id
        return None

    async def remove_answer(self, id_):
        pass

    async def get_answer(self, ans_id):
        q = sa.select(Answer).where(Answer.id == ans_id)
        result = await self.session.execute(q)
        res = result.scalars().all()
        return res

    async def get_answers_for_question(self, q_id):
        q = sa.select(Answer).where(Answer.question == q_id)
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
