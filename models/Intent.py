from .BaseModel import *
from .Module import *

class Intent(BaseModel):
    id = BigAutoField()
    module = ForeignKeyField(column_name='module_id', field='id', model=Module, backref='intents')
    name = CharField()

    class Meta:
        table_name = 'intents'

    def __str__(self):
        return self.name


