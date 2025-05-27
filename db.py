from peewee import *
import uuid

db = SqliteDatabase('contador.db')

class Detection(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    zona = CharField()
    clase = CharField()
    fecha = DateTimeField()
    enviado_a = TextField(default="")

    class Meta:
        database = db 
        primary_key = False

db.connect()
db.create_tables([Detection])
