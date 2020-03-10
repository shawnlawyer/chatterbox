from peewee import *
from databases import MySQL as database

class BaseModel(Model):
    class Meta:
        database = database
