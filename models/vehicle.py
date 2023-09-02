#!/usr/bin/python3
'''
    Implementation of the User class which inherits from BaseModel
'''
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from os import getenv

storage_type = getenv("HBNB_TYPE_STORAGE")


class Vehicle(BaseModel, Base):
    '''
        Definition of the User class
    '''
    __tablename__ = 'vehicles'
    __table_args__ = ({'mysql_default_charset': 'latin1'})
    if storage_type == 'db':
        capacity = Column(String(128), nullable=False)
        price_per_day = Column(String(128), nullable=False)
        model = Column(String(128), nullable=True)
        type = Column(String(128), nullable=True)
        color = Column(String(60), nullable=True)
        brand = Column(String(60), nullable=True)
        rentals = relationship("Rental", backref="vehicle",
                              cascade="all, delete-orphan")
    else:
        capacity = ""
        price_per_day = ""
        model = ""
        type = ""
        color = ""
        brand = ""


