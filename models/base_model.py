#!/usr/bin/python3

from datetime import datetime
import uuid


class BaseModel:
    def __init__(self, *args, **kwargs):
        if kwargs:
            for arg, val in kwargs.items():
                if arg in ('created_at', 'updated_at'):
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%f')

                if arg != '__class__':
                    setattr(self, arg, val)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at

    def __str__(self):
        return '[{0}] ({1}) {2}'.format(
                self.__class__.__name__, self.id, self.__dict__
            )

    def save(self):
        self.updated_at = datetime.now()

    def to_dict(self):
        class_info = self.__dict__.copy()
        class_info['__class__'] = self.__class__.__name__
        class_info['created_at'] = self.created_at.isoformat()
        class_info['updated_at'] = self.updated_at.isoformat()

        return class_info
    

    