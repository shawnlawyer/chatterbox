from .BaseModel import *
from flask_security import UserMixin

class User(BaseModel, UserMixin):
    id = BigAutoField()
    email = CharField(unique=True)
    password = CharField()
    active = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)\

    class Meta:
        table_name = 'users'



