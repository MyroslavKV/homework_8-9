from sqlalchemy import Column, Integer, String, Float
from init_db import Base

class MovieDB(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    director = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
