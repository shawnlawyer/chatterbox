from .BaseModel import *

class Agent(BaseModel):
    id = BigAutoField()
    name = CharField(null=True)

    class Meta:
        table_name = 'agents'

    def __str__(self):
        return self.name


