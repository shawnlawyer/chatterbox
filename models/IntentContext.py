from .BaseModel import *
from .Intent import *

class IntentContext(BaseModel):
    id = BigAutoField()
    intent = ForeignKeyField(column_name='intent_id', field='id', model=Intent, backref='contexts')
    text = TextField()

    class Meta:
        table_name = 'intent_contexts'

    def __str__(self):
        return self.text
