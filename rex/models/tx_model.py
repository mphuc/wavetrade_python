import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Tx(Document):
    __collection__ = 'tx'

    structure = {
        'status': int
        'tx':  unicode,
        'date_added' : datetime.datetime
    }
    use_dot_notation = True

db.register([Tx])