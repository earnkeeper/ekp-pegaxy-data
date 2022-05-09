from sqlalchemy import MetaData, create_engine

from db.market_buys_schema import market_buys_schema
from db.pegas_schema import pegas_schema
from db.players_schema import players_schema

DATABASE_URI = 'postgresql+psycopg2://postgres:pythonista0505@localhost:5432/pegaxy'


def init_db():
    meta_data = MetaData()

    engine = create_engine(DATABASE_URI)

    players = players_schema(meta_data)
    market_buys = market_buys_schema(meta_data)
    paegas = pegas_schema(meta_data)

    try:
        conn = engine.connect()
        print('db connected')
        print('connection object is :{}'.format(conn))

    except:
        print('db not connected')

    meta_data.create_all(engine)
