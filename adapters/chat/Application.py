from flask import session

from .routes import *

from controllers import AuthController
from databases import MySQL as database

class Application():
    def __init__(self):

        # basics
        self.database = Database()
        self.session = Session()

        # controller
        self.controllers = Controllers()

        # routes
        self.routes = Routes(self.controllers)

        # router
        self.router = Router(self.routes)

    def handle_request(self, intent, slots={}):
        return self.router.handle_request( intent, slots)

class Database():

    def open(self):
        database.connect()

    def close(self):
        database.close()

class Session():

    def has(self, key):
        return key in session.attributes

    def get(self, key):
        return session.attributes.get(key)

    def set(self, key, value):
        session.attributes[key] = value

    def pop(self, key, default=None):
        return session.pop(key, default)

class Controllers():

    def __init__(self):
        self.auth = AuthController()

    def get(self):
        return {
            'auth' : self.auth
        }

class Routes():

    def __init__(self, controllers):
        self.controllers = controllers
        self.application = AuthRoutes(self.controllers)


    def get(self):
        return {
            'application' : self.application
        }

class Router:

    def __init__(self, routes):
        self.routes = routes
        self.controllers = routes.controllers
        self.slots = {}
        self.route = ''

    def handle_request(self, intent, slots={}):

        result = None

        self.route = intent
        for slot in slots:
            self.slots[slot] = slots[slot]

        for route in self.routes.get().values():
            if self.route in route.routes:
                if route.handle_route(self.route, self.slots):
                    try:
                        result = route.result
                    except:
                        pass

        return result
