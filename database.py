from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy import text, column
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///users.db')

Base = declarative_base()

Session = sessionmaker(bind=create_engine("sqlite:///users.db"))
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return f"{self.username = }, {self.email = }"


class Sessions(Base):
    __tablename__ = "sessions"

    session_id = Column(Text, primary_key=True)
    user_id = Column(String)


Base.metadata.create_all(engine)


def get_user_by_id(user_id):
    return session.query(User).filter_by(id=user_id).first()

def get_users():
    users = session.query(User).all()
    return users

def get_session_by_user_id(user_id):
    return session.query(Sessions).filter_by(user_id=user_id).first()


def add_session(session_id, user_id):
    user_session = Sessions(session_id=session_id, user_id=user_id)
    if get_session_by_user_id(user_id):
        del_session(Sessions(session_id=session_id, user_id=user_id))
    session.add(user_session)
    session.commit()
    return user_session


def get_session(session_id):
    return session.query(Sessions).filter_by(session_id=session_id).first()


def del_session(sessions):
    session.delete(session.query(Sessions).filter_by(user_id=sessions.user_id).first())
    session.commit()


def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    if get_user(username):
        return False
    session.add(user)
    session.commit()
    return user


def get_user(username):
    user = session.query(User).filter_by(username=username).first()
    return user
