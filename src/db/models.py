from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base


async def wrapped_models(Base: declarative_base):
    class Swaps(Base):
        __tablename__ = 'swaps'

        id = Column(Integer, primary_key=True, autoincrement=True)
        timestamp = Column(Integer)
        block = Column(Integer)
        pool_contract = Column(String)
        amount0 = Column(String)
        amount1 = Column(String)
        price = Column(Float)
        network = Column(String)
        # Add this line to store the specific asset information
        asset = Column(String)

    class Pools(Base):
        __tablename__ = 'pools'

        id = Column(Integer, primary_key=True, autoincrement=True)
        pool_contract = Column(String)
        token0 = Column(String)
        token1 = Column(String)
        network = Column(String)
        # Add this line to store the specific asset information
        asset = Column(String)

    class Future(Base):
        __tablename__ = 'future'
        id = Column(Integer, primary_key=True, autoincrement=True)
        pool_contract = Column(String)
        timestamp = Column(Integer)
        price = Column(Float)
        price_upper = Column(Float)
        price_lower = Column(Float)
        network = Column(String)
        # Add this line to store the specific asset information
        asset = Column(String)

    return Swaps, Pools, Future
