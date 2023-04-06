from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# in python, asynchronous program is typically implemented using the asyncio library
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .db_utils import db_utils
from .models import wrapped_models as wrapped_models_func
from .methods import wrapped_methods

# this initializes an asyncrhonous SQLAlchemy database session and creates corresponding
# database tables using the SQL Alchemy declarative base approach.


async def init_async_db(test=False):
    name = "test" if test else "main"
    # creates a new SQLite database file in the current working directory if one doesn't exist already
    # fr creates an f-string to insert variables

    engine = create_async_engine(
        fr'sqlite+aiosqlite:///./{name}.db', future=True, echo=False)

    # creates an asynchronous session factory using sessionmaker function from SQL Alchemy
    session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    # creates a new declarative base class in SQL Alchemy that will be used to define database models
    base = declarative_base()
    db_utils.set_base(base)
    # creates a set of database models based on a given SQL Alchemy declarative base class
    wrapped_models = await wrapped_models_func(base)

    # creates the tables in the database
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    # creates a set of database methods that can be used to interact with the data base
    swaps, pools, future = await wrapped_methods(wrapped_models, session)
    return swaps, pools, future
