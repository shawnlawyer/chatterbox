from .BaseModel import *
from .Intent import *

class IntentDialog(BaseModel):
    id = BigAutoField()
    intent = ForeignKeyField(column_name='intent_id', field='id', model=Intent, backref='dialogs')
    name = CharField()
    slot = CharField()
    input_type = CharField()

    class Meta:
        table_name = 'intent_dialogs'

    def __str__(self):
        return self.slot

