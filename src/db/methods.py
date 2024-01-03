from sqlalchemy import delete, update, func
from sqlalchemy.future import select


async def wrapped_methods(wrapped_models: list, async_session) -> list:
    return [Methods(model, async_session) for model in wrapped_models]


def wrap_async(func):
    async def wrapper(*args, **kwargs):
        async with args[0]._session() as session:
            async with session.begin():
                kwargs = {**kwargs, **{'session': session}}
                result = await func(*args, **kwargs)
                return result

    return wrapper


class Methods:

    def __init__(self, model: object(), session):
        self.__model = model
        self._session = session

    @wrap_async
    async def commit(self, session):
        await session.commit()

    @wrap_async
    async def paste_row(self, kwargs, session):
        session.add(self.__model(**kwargs))
        await session.flush()

    @wrap_async
    async def delete_old(self, block, th, session) -> int:
        return await session.execute(
            delete(self.__model).where(getattr(self.__model, 'block') < block - th))

    @wrap_async
    async def delete_old_by_timestamp(self, timestamp, session) -> int:
        return await session.execute(
            delete(self.__model).where(getattr(self.__model, 'timestamp') < timestamp))

    @wrap_async
    async def delete_row_by_contract(self, contract, session) -> int:
        return await session.execute(
            delete(self.__model).where(getattr(self.__model, 'pool_contract') == contract))

    @wrap_async
    async def get_all_rows(self, session) -> tuple or None:
        q = await session.execute(select(self.__model))
        data = q.scalars().all()
        return data

    @wrap_async
    async def update_row_by_criteria(self, row: dict, criteria: dict, session):
        q = update(self.__model).where(getattr(self.__model, list(criteria.keys())[0]) == list(criteria.values())[0])
        for _ in zip(row.keys(), row.values()):
            q = q.values(**row)
        await session.execute(q)

    @wrap_async
    async def get_row_by_criteria(self, criteria: dict, session) -> object or None:
        q = await session.execute(
            select(self.__model).where(getattr(self.__model, list(criteria.keys())[0]) == list(criteria.values())[0]))
        return q.scalars().first()

    @wrap_async
    async def get_all_rows_by_criteria(self, criteria: dict, session) -> object or None:
        q = await session.execute(
            select(self.__model).where(getattr(self.__model, list(criteria.keys())[0]) == list(criteria.values())[0]))
        return q.scalars().all()

    @wrap_async
    async def count_rows(self, session) -> object or None:
        q = await session.execute(func.count(self.__model.id))
        return q.scalar()

    @wrap_async
    async def count_rows_by_criteria(self, criteria: dict, session) -> object or None:
        q = await session.execute(func.count(self.__model.id).where(
            getattr(self.__model, list(criteria.keys())[0]) == list(criteria.values())[0]))
        return q.scalar()
