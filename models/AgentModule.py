from .BaseModel import *
from .Agent import Agent
from .Module import Module

class AgentModule(BaseModel):
    id = BigAutoField()
    agent = ForeignKeyField(Agent, backref='modules')
    module = ForeignKeyField(Module, backref='agents')

    class Meta:
        table_name = 'agents_modules'

