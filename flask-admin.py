from models import *
from flask import Flask, render_template, redirect, request, url_for, abort, jsonify, json, Markup
from flask_security import current_user, login_required, RoleMixin, Security, PeeweeUserDatastore, UserMixin, utils
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib import peewee
from flask_admin import helpers as admin_helpers
from envs import env
from pusher import Pusher
from wtforms.fields import PasswordField, SelectField, SelectMultipleField
from models.BaseModel import *
from databases import MySQL as database
from flask_admin.model.form import InlineFormAdmin
from flask_admin.menu import MenuCategory, MenuView, MenuLink, SubMenuCategory
from flask_wtf.csrf import CSRFProtect
from flask_admin.form.fields import Select2TagsField
from flask_security.utils import hash_password
from lib import *

import logging

user_datastore = PeeweeUserDatastore(database, User, Role, UserRole)

app = Flask(__name__,'/')
admin_url = ''
app.config['DEBUG'] = env('SECRET_KEY', False)
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email']
app.config['SECRET_KEY'] = env('SECRET_KEY')
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = env('SECRET_KEY')
app.config['SECURITY_POST_LOGIN_VIEW'] = '/admin'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/'
app.config['SECURITY_LOGIN_URL'] = '/admin/login'
app.config['SECURITY_LOGOUT_URL'] = '/admin/logout'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.filters['json'] = lambda v: Markup(json.dumps(v))


csrf = CSRFProtect(app)


class BaseAdminView():

    def is_visible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('security.login', next=None))

class BaseAdminModelView(peewee.ModelView, BaseAdminView):


    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('security.login', next=None))

    column_auto_select_related = True
    can_set_page_size = True
    page_size = 10
    can_export = True
    edit_modal = False
    create_modal = False
    details_modal = False
    columns_hidden_list = ()
    can_view_details = True

class IndexAdmin(AdminIndexView, BaseAdminView):

    def is_visible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=None))

class UserAdmin(BaseAdminModelView):

    column_exclude_list = ('select', 'password',)
    form_excluded_columns = ('password',)

    def scaffold_form(self):

        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        form_class.roles = SelectMultipleField(
            'Roles',
            choices=[(role.id, role.name) for role in Role.select()]
        )

        return form_class

    def validate_form(self, form):
        role_ids = []
        if form.roles.data:
            for id in form.roles.data:
                role_ids.append(int(id))

        form.roles.data = role_ids
        return super(UserAdmin, self).validate_form(form)

    def on_form_prefill(self, form, id):

        role_ids = []
        for id in form.roles.data:
            role = UserRole.select().where(UserRole.id == id).first()
            role_ids.append(str(role.role_id))

        form.roles.data = role_ids

    def on_model_change(self, form, model, is_created):
        roles = Role.select()
        for role in roles:
            user_datastore.remove_role_from_user(model.email, role.name)

        for id in form.roles.data:
            role = Role.select().where(Role.id == id).first()
            if role:
                user_datastore.add_role_to_user(model.email, role.name)
        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)

class AgentAdmin(BaseAdminModelView):
    column_searchable_list = ['name']
    column_exclude_list = ('id')

    def scaffold_form(self):

        form_class = super(AgentAdmin, self).scaffold_form()
        form_class.modules = SelectMultipleField(
            'Modules',
            choices=[(module.id, module.name) for module in Module.select()]
        )

        return form_class

    def validate_form(self, form):
        module_ids = []
        if form.modules.data:
            for id in form.modules.data:
                module_ids.append(int(id))

        form.modules.data = module_ids
        return super(AgentAdmin, self).validate_form(form)

    def on_form_prefill(self, form, id):

        module_ids = []
        for id in form.modules.data:
            agent_module = AgentModule.select().where(AgentModule.id == id).first()
            module_ids.append(str(agent_module.module_id))

        form.modules.data = module_ids


    def on_model_change(self, form, model, is_created):

        AgentModule.delete().where(AgentModule.agent_id==model.id).execute()

        for id in form.modules.data:
            module = Module.select().where(Module.id == id).first()
            if module:
                AgentModule.create(agent=model.id, module=module.id)


class RoleAdmin(BaseAdminModelView):

    def after_model_change(self, form, model, is_created):

        for view in admin._views:
            if view.name == 'User':
                view._refresh_cache()

class ModuleAdmin(BaseAdminModelView):
    column_searchable_list = ['name']
    column_list = ('name', 'Actions')

    @expose('/fit', methods=["POST"])
    @csrf.exempt
    def fit(self):
        model = Module().select().where(Module.id == int(request.values.get('id'))).first()
        if model:
            chat_module = ChatModule(name=model.name, load=False)
            chat_module.fit()
        return jsonify(['1'])

    @expose('/restart')
    def restart(self):
        restart_chat_application()
        return jsonify([1])

    def _format_actions(view, context, model, name):

        _html = '''
            <a href="javascript:$.post('/admin/module/fit', {id:%s}, function(data) {alert('Training Complete.');});">Train</a>
        ''' % (model.id)

        return Markup(_html)

    column_formatters = {
        'Actions': _format_actions
    }

    column_exclude_list = ('id')
    form_ajax_refs = {
        'intents': {
            'fields': (Intent.module, Intent.name)
        }
    }

    inline_models = [
        (Intent, dict(form_args = dict(id = dict(default = 0))))
    ]


    def after_model_change(self, form, model, is_created):

        for view in admin._views:
            if view.name == 'Agent':
                view._refresh_cache()

class IntentAdmin(BaseAdminModelView):
    column_select_related_list = (Intent.module,)
    column_searchable_list = ['name']
    column_exclude_list = ('id')
    form_ajax_refs = {
        'patterns': {
            'fields': (IntentPattern.intent, IntentPattern.text)
        },'responses': {
            'fields': (IntentResponse.intent, IntentResponse.text)
        },'dialogs': {
            'fields': (IntentDialog.intent, IntentDialog.name, IntentDialog.slot)
        },'contexts': {
            'fields': (IntentContext.intent, IntentContext.text)
        },
    }
    inline_models = [
        (IntentPattern, dict(form_args = dict(id = dict(default = 0)))),
        (IntentResponse, dict(form_args = dict(id = dict(default = 0)))),
        (IntentDialog, dict(form_args = dict(id = dict(default = 0)))),
        (IntentContext, dict(form_args = dict(id = dict(default = 0)))),
    ]

class BaseChatAdminModelView(BaseAdminModelView):
    column_searchable_list = ['text']
    column_exclude_list = ('id')
    def is_visible(self):
        return False

class IntentPatternAdmin(BaseChatAdminModelView):
    column_select_related_list = (IntentPattern.intent,)

class IntentResponseAdmin(BaseChatAdminModelView):
    column_select_related_list = (IntentResponse.intent,)

class IntentContextAdmin(BaseChatAdminModelView):
    column_select_related_list = (IntentContext.intent,)

class IntentDialogAdmin(BaseChatAdminModelView):
    column_select_related_list = (IntentDialog.intent,)
    column_searchable_list = ['slot']


@app.before_first_request
def create_user():
    #user_datastore.create_user(email='admin@email.com', password=hash_password('password'))
    pass

@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response

admin = Admin(
    app,
    'Dashboard',
    template_mode='bootstrap3',

    index_view=IndexAdmin()
)

security = Security(app, user_datastore)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

admin.add_view(UserAdmin(User, category='Admin'))
admin.add_view(RoleAdmin(Role, category='Admin'))
admin.add_view(AgentAdmin(Agent, category='Chat Agents'))
admin.add_view(ModuleAdmin(Module, category='Chat Agents'))
admin.add_view(IntentAdmin(Intent, category='Chat Agents'))
admin.add_view(IntentPatternAdmin(IntentPattern))
admin.add_view(IntentResponseAdmin(IntentResponse))
admin.add_view(IntentDialogAdmin(IntentDialog))
admin.add_view(IntentContextAdmin(IntentContext))
admin.add_link(MenuLink(name='Restart Chat', category='Chat Agents', url="javascript:$.get('/admin/intent/restart', function(data) {alert('Restart Complete.');});"))


def run_app(app, log=False, debug=False):

    if not log:
        logger = logging.getLogger('werkzeug')
        logger.disabled = True
        app.logger.disabled = True

    app.run(debug=debug, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    run_app(app, True, True)
