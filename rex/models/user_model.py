import datetime
from mongokit import Document
from rex import app, db
import validators
from bson.objectid import ObjectId
__author__ = 'taijoe'


class User(Document):
    __collection__ = 'users'

    structure = {
        'name': unicode,
        'ico_max': float,
        'customer_id' : unicode,
        'email': unicode,
        'username': unicode,
        'password': unicode,
        'role': int,
        'creation': datetime.datetime,
        'p_binary' : unicode,
        'left' : unicode,
        'right' : unicode,
        'telephone' : float,
        'p_node' : unicode,
        'password_transaction' : unicode,
        'btc_wallet' : unicode,
        'level' : int,
        'password_custom' : unicode,
        'img_profile' : unicode,
        'input_wallet' : unicode,
        'total_team' : float,
        'total_amount_team' : float,
        'm_wallet' : float,
        'r_wallet' : float,
        's_wallet' : float,
        'status_authen' : int,
        'authentication' : unicode,
        'token_ico' : float,
        'max_out' : float,
        'total_max_out' : float,
        'total_earn' : float,
        'position' : unicode,
        'country' : unicode,
        'total_invest' : float,
        'roi' : float,
        'max_binary' : float,
        'code_active': unicode,
        'status':int,
        'type': int,
        'sva_balance': float,
        'sva_address': unicode,
        'btc_balance': float,
        'btc_address': unicode,
        'usd_balance': float,
        'total_capital_back': float,
        'total_commission': float,
        'secret_2fa': unicode,
        'status_2fa': int,
        'max_daily': float,
        'current_max_daily': float,
        'sva_usd_cms': float,
        'sva_static_interest': float,
        'sva_monthly_bonus': float,
        'sva_sharing_bonus': float,
        'sva_direct_cms': float,
        'sva_enterprise_cms': float,
        'ranking': float,
        'total_f1': float,
        'ltc_address': unicode,
        'ltc_balance': float,
        'sva_usdsva': float,
        'btc_direct_commission': float
    }
    validators = {
        'name': validators.max_length(50),
        'email': validators.max_length(120)
    }
    default_values = {
        'creation': datetime.datetime.utcnow(),
        'm_wallet' : 0,
        'r_wallet' : 0,
        's_wallet' : 0,
        'max_out' : 0,
        'total_earn' : 0,
        'level' : 0,
        'token_ico' : 0,
        'status_authen' : 0,
        'authentication' : '',
        'left' : '',
        'right' : '',
        'p_binary' : '',
        'type': 0

        }
    use_dot_notation = True

    

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def get_role(self):
        return self.role

    def get_user_home(self):
        role = db['roles'].find_one({'_id': self.get_role()})
        return role['home_page']


db.register([User])