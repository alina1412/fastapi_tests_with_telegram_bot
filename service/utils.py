import sqlalchemy as sa

# from sqlalchemy import select, update, or_, delete
from sqlalchemy.dialects.postgresql import insert


from service.db_setup.models import User


class Db:
    model = None

    def __init__(self, model) -> None:
        self.model = model

    async def select(self, session, conds=None):
        if not conds:
            conds = (1 == 1,)
        q = sa.select(self.model).where(*conds)
        result = await session.execute(q)
        res = result.scalars().all()
        data = [{"username": u.username, "id": u.id} for u in res]
        return data

    async def put(self, session, vals):
        # username=data["name"], password=data["password"]
        q = insert(self.model).values(**vals).on_conflict_do_nothing()

        result = await session.execute(q)
        if result.rowcount:
            return result.returned_defaults[0]  # id
        return None

    async def update(self, session, vals, conds=None):
        # {self.model.active.key: self.model.active or data["active"]}
        if not conds:
            conds = (1 == 1,)
        stmt = (
            sa.update(self.model).where(*conds).values(**vals).returning(self.model.id)
        )
        result = list(await session.execute(stmt))
        return result

    async def delete(self, session, conds=None):
        stmt = sa.delete(self.model).where(conds)
        result = await session.execute(stmt)
        # result.rowcount
        return
