#!/usr/bin/python3
'''
    Implementation of the Review class
'''
from models.base_model import BaseModel, Base
from models.vehicle import Vehicle
from sqlalchemy import Column, String, ForeignKey
from os import getenv


storage_type = getenv("HBNB_TYPE_STORAGE")


class Rental(BaseModel, Base):
    '''
        Implementation for the Review.
    '''
    __tablename__ = 'rentals'
    __table_args__ = ({'mysql_default_charset': 'latin1'})
    if storage_type == 'db':
        vehicle_id = Column(String(60), ForeignKey("vehicles.id"), nullable=False)
        user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
        start_date = Column(String(60), nullable=False)
        end_date = Column(String(60), nullable=False)
        total_cost = Column(String(60), nullable=True)
    else:
        vehicle_id = ""
        user_id = ""
        start_date = ""
        end_date = ""
        total_cost = ""


