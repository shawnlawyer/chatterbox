from .BaseModel import *
from .Intent import *

class IntentPattern(BaseModel):
    id = BigAutoField()
    intent = ForeignKeyField(column_name='intent_id', field='id', model=Intent, backref='patterns')
    text = TextField()

    class Meta:
        table_name = 'intent_patterns'

    def __str__(self):
        return self.text

