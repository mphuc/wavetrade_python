import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Trading(Document):
    __collection__ = 'trading'

    structure = {
        'amount' : unicode,
        'p_node': unicode,
        'user_id' : unicode,
        'date' : datetime.datetime,
        'team_volume': unicode
    }
    use_dot_notation = True

db.register([Trading])