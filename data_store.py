
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object


metadata = MetaData()
Base = declarative_base()


def add_viewed(owner_id, user_id):
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        to_bd = Viewed(profile_id=owner_id, worksheet_id=user_id)
        session.add(to_bd)
        session.commit()
    return "успешно добавлен в БД"


def insert_viewed(owner_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id == owner_id).all()
        for item in from_bd:
            return item.profile_id


def add_favourite(owner_id, user_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        to_fav = Favourite(profile_id=owner_id, worksheet_id=user_id)
        session.add(to_fav)
        session.commit()
        return "Пользователь в избранных!"


def show_favourite(user_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        show_fav = session.query(Favourite.profile_id).filter(Favourite.worksheet_id == user_id).all()
        return show_fav


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

class Favourite(Base):
    __tablename__ = 'favourites'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)



if __name__ == '__main__':
    Base.metadata.drop_all()
    Base.metadata.create_all()
