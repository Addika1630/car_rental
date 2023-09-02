#!/usr/bin/python3
'''
    Implementation of the User class which inherits from BaseModel
'''
from models.base_model import BaseModel, Base
from models.rental import Rental
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from os import getenv

storage_type = getenv("HBNB_TYPE_STORAGE")


class User(BaseModel, Base):
    '''
        Definition of the User class
    '''
    __tablename__ = 'users'
    __table_args__ = ({'mysql_default_charset': 'latin1'})
    if storage_type == 'db':
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        phone_no = Column(String(20), nullable=True)
        rentals = relationship("Rental", backref="user",
                              cascade="all, delete-orphan")
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""
        phone_no = ""


