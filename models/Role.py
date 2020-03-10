from .BaseModel import *
from flask_security import RoleMixin

class Role(BaseModel, RoleMixin):
    id = BigAutoField()
    name = CharField(unique=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'roles'

