from flask import Flask, jsonify, request, render_template, session, url_for
from flask_login import LoginManager
from flask_security import current_user, login_required, RoleMixin, Security, PeeweeUserDatastore, UserMixin, utils
import urllib.parse
import json
import random
from envs import env
import logging
from models import *
from lib import *

from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
from flask_security.utils import encrypt_password
from flask_security import current_user

agent = Agent().select().where(Agent.name == 'main').first()
modules = []
for module in agent.modules:
    agent_module = AgentModule().select().where(AgentModule.id == module).first()
    modules.append(Module.select().where(Module.id == agent_module.module).first().name)

box = ChatterBox(None, modules)

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')

app.config['DEBUG'] = env('SECRET_KEY', False)
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email']
app.config['SECRET_KEY'] = env('SECRET_KEY')
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = env('SECRET_KEY')
app.config['SECURITY_POST_LOGIN_VIEW'] = '/'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/'
app.config['SECURITY_LOGIN_URL'] = '/admin/login'

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response


from databases import MySQL as database

user_datastore = PeeweeUserDatastore(database, User, Role, UserRole)

security = Security(app, user_datastore)

@security.context_processor
def security_context_processor():
    return dict(
        h=admin_helpers,
        get_url=url_for
    )

def run_app(app, log=False, debug=False):

    if not log:
        logger = logging.getLogger('werkzeug')
        logger.disabled = True
        app.logger.disabled = True

    app.run(debug=debug, host='0.0.0.0', port=5002)

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def assistant():
    return render_template('assistant.html')

@app.route("/chat/clear", methods=["GET"])
def clean_session():
    box.clean_session()
    return '1'

@app.route("/chat", methods=["POST"])
def chat():

    sentence = urllib.parse.unquote_plus(request.values.get('message')) if request.values.get('message') else ''
    response = box.chat(sentence)
    return jsonify({
        'classification': response.classification,
        'response': response.response,
        'confindence': response.confidence,
        'input_type': response.input_type,
        'csrf_token': generate_csrf()
    })


if __name__ == "__main__":

    run_app(app, True, True)

