from models import *

from flask_login import login_user, logout_user

from flask_security.utils import encrypt_password, verify_and_update_password
from flask_security import current_user

class Controller:

    def login(self, email, secret):

        user = User().select().where(User.email==email).first()
        if user and verify_and_update_password(secret, user):
            login_user(user)

        else:
            user = None

        if user:
            return "Welcome back!"

        else:
            return "Login Failed!"


    def logout(self):

        logout_user()

        return "Logout Done!"
