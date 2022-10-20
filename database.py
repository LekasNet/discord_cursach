import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

engine = create_engine('sqlite:///Trees.db')
print(0)

class Trees(Base):
    __tablename__ = 'tournaments'

    tour_id = Column(Integer, primary_key=True, unique=True)
    tour_nm = Column(String(250), nullable=False)
    tour_dc = Column(String(250))
    tour_us = Column(String(250))


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, unique=True)
    user_nm = Column(String(250), nullable=False)
    tour_ct = Column(Integer, default=0)


class Registers(Base):
    __tablename__ = 'registers'

    regs_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, nullable=False)
    tour_id = Column(Integer, nullable=False)
    regs_dt = Column(DateTime)


class Servers(Base):
    __tablename__ = 'servers'

    oper_id = Column(Integer, primary_key=True, unique=True)
    serv_id = Column(Integer)
    serv_nm = Column(String(250), nullable=False)
    func_nm = Column(String(250), nullable=False, unique=True)

Base.metadata.create_all(engine)