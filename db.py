from peewee import *

db = SqliteDatabase('contador')

class Detection(Model):
    zona = CharField()
    clase = CharField()
    fecha = DateTimeField()
    enviado = BooleanField()

    class Meta:
        database = db 
        primary_key = False

db.connect()
db.create_tables([Detection])
