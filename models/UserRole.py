from .BaseModel import *
from .User import User
from .Role import Role
from flask_security import RoleMixin

class UserRole(BaseModel, RoleMixin):
    id = BigAutoField()
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

    class Meta:
        table_name = 'users_roles'

