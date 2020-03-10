from .BaseModel import *

class Module(BaseModel):
    id = BigAutoField()
    name = CharField(null=True)

    class Meta:
        table_name = 'modules'

    def __str__(self):
        return self.name
