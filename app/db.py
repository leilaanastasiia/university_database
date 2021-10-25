from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///dataset.db', echo=True)


class Physiology(Base):
    __tablename__ = 'physiology'

    lecture_id = Column(Integer, primary_key=True)
    topic = Column(String, unique=True)
    lecture_link = Column(String, nullable=False)
    practise_link = Column(String, nullable=False)
    labprot_link = Column(String, nullable=False)
    comments = Column(String, nullable=False)


def get_session(engine):
    _session = sessionmaker(bind=engine)
    session_class = _session()
    return session_class


def insert_row(data: str):
    splitted = data.split('\n')
    new_row = Physiology(
        topic=splitted[0],  # key-name
        lecture_link=splitted[1],  # presentation
        practise_link=splitted[2],  # lab youtube
        labprot_link=splitted[3],  # lab pdf
        comments=splitted[4]
    )
    session = get_session(engine)
    with session as s:
        s.add(new_row)
        s.commit()


def delete_row(request: str) -> None:
    session = get_session(engine)
    with session as s:
        row = s.query(Physiology).filter(Physiology.topic == request)
        row.delete()
        s.commit()


def delete_rows():
    session = get_session(engine)
    with session as s:
        rows = s.query(Physiology)
        rows.delete()
        s.commit()


def get_topics_list() -> list:
    session = get_session(engine)
    result = []
    with session as s:
        for t in s.query(Physiology.topic):
            result.append(t[0])
        return result


def get_row(request: str) -> list[tuple]:
    session = get_session(engine)
    with session as s:
        row = s.query(
            Physiology.topic,
            Physiology.lecture_link,
            Physiology.practise_link,
            Physiology.labprot_link,
            Physiology.comments
        ).where(Physiology.topic == request)
        return row[::]


def create_table():
    Base.metadata.create_all(bind=engine)
