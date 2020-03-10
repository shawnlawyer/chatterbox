class Routes:

    def __init__(self, controllers):
        self.controller = controllers.auth
        self.result = None
        self.routes = [
            'login', 'logout'
        ]

    def handle_route(self, route, slots):

        if route in ["login"]:
            self.result = self.controller.login(**slots)

        if route in ["logout"]:
            self.result = self.controller.logout()

        return self.result


