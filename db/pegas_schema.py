from sqlalchemy import (Column, DateTime, Float, Integer, String,
                        Table)


def pegas_schema(meta_data):
    return Table('pegas', meta_data,
                 Column('id', String(64), primary_key=True),
                 Column('created', DateTime(), nullable=False),
                 Column('updated', DateTime(), nullable=False),
                 Column('name', String(150), nullable=False),
                 Column('cost', String(64)),
                 Column('cost_coin_id', String(64)),
                 Column('market_value', String(64)),
                 Column('market_value_coin_id', String(64)),
                 Column('earned_to_date', String(64)),
                 Column('earned_to_date_coin_id', String(64)),
                 Column('place_rate', Float()),
                 Column('total_races', Integer()),
                 Column('owner_player_id', String(64), nullable=False),
                 )
