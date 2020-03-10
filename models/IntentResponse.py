from .BaseModel import *
from .Intent import *

class IntentResponse(BaseModel):
    id = BigAutoField()
    intent = ForeignKeyField(column_name='intent_id', field='id', model=Intent, backref='responses')
    text = TextField()

    class Meta:
        table_name = 'intent_responses'

    def __str__(self):
        return self.text
