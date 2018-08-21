from json import dumps
import json
from flask import Flask, send_from_directory, send_file, Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash, send_file
from flask.ext.login import login_required, LoginManager, current_user
from flask.ext.mongokit import MongoKit
from flask.templating import render_template
import os
import settings
from random import randint
from hashlib import sha256
import string
import random
from datetime import datetime
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
import requests
import json
from flask_socketio import emit
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# from flask_recaptcha import ReCaptcha
__author__ = 'carlozamagni'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.from_object(settings)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO()
socketio.init_app(app)

db = MongoKit(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = '/invest/home'


from rex.controllers import deposit_controller
app.register_blueprint(blueprint=deposit_controller.deposit_ctrl, url_prefix='')

from rex.controllers import admin_controller
app.register_blueprint(blueprint=admin_controller.admin_ctrl, url_prefix='/admin')

from rex.controllers import admin
app.register_blueprint(blueprint=admin.admin1_ctrl, url_prefix='/admin')

from rex.controllers import personal_controller
app.register_blueprint(blueprint=personal_controller.personal_ctrl, url_prefix='/personal')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.template_filter()
def format_date(date): # date = datetime object.
    return date.strftime('%Y-%m-%d %H:%M:%S')
@app.template_filter()
def format_only_date(date): # date = datetime object.
    return date.strftime('%Y-%m-%d')
@app.template_filter()
def find_username(uid): # date = datetime object.
    if uid:
        uid = uid
    else:
        uid ='1111111'
    user = db.User.find_one({'customer_id': uid})
    if user is None:
        return ''
    else:
        return user.username

@app.template_filter()
def find_user_usd(uid): # date = datetime object.
    if uid:
        uid = str(uid)
    else:
        uid ='1111111'
    user = db.users.find_one({'_id': ObjectId(uid)})
    if user is None:
        return ''
    else:
        return user['usd_balance']

@app.template_filter()
def find_user_sva(uid): # date = datetime object.
    if uid:
        uid = uid
    else:
        uid ='1111111'
    user = db.users.find_one({'_id': ObjectId(uid)})
    if user is None:
        return ''
    else:
        return user['sva_balance']

@app.template_filter()
def to_string(value):
    
    return str(value)
@app.template_filter()
def number_format(value, tsep=',', dsep='.'):
    s = unicode(value)
    cnt = 0
    numchars = dsep + '0123456789'
    ls = len(s)
    while cnt < ls and s[cnt] not in numchars:
        cnt += 1

    lhs = s[:cnt]
    s = s[cnt:]
    if not dsep:
        cnt = -1
    else:
        cnt = s.rfind(dsep)
    if cnt > 0:
        rhs = dsep + s[cnt+1:]
        s = s[:cnt]
    else:
        rhs = ''

    splt = ''
    while s != '':
        splt = s[-3:] + tsep + splt
        s = s[:-3]

    return lhs + splt[:-1] + rhs
@app.template_filter()
def format_round(value):
    value = float(value)
    return '{:20,.8f}'.format(value)
@app.template_filter()
def format_usd(value):
    value = float(value)
    return '{:20,.2f}'.format(value)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def set_password(password):
    return generate_password_hash(password)
@app.route('/setup')
def setup():
    inserted = []
    return json.dumps({'status' : 'error'})
    
    # db.users.update({'customer_id': '1010101001'}, {'$set': {'creation':datetime.utcnow()}})
    # return json.dumps({'status' : 'error'})
    users = [{"_id" : "5995a569587b3b15a14174e0",
    "roi" : 100920,
    "right" : "",
    "p_binary" : "",
    "m_wallet" : 600000000,
    "creation" : datetime.utcnow(),
    "telephone" : "000000000",
    "password_transaction" : set_password('12345'),
    "total_amount_right" : int("0"),
    "total_pd_right" : int("0"),
    "btc_wallet" : "19WpQavvcEcy4MmWk7szPoiY2cwvi8jt9E",
    "p_node" : "",
    "r_wallet" : 600000000,
    "password_custom" : set_password('12345'),
    "total_pd_left" : 9700,
    "customer_id" : "1010101001",
    "email" : "meccafunds@meccafund.org",
    "total_amount_left" : 10500,
    "username" : "root",
    "s_wallet" : 1000000000,
    "total_invest" : 100000,
    "password" : set_password('12345'),
    "img_profile" : "",
    "max_out" : 500000,
    "max_binary" : 500000,
    "name" : "MECCAFUND",
    "level" : int("3"),
    "country" : "French Southern territories",
    "wallet" : "",
    "status" : 1,
    "total_earn" : 10000,
    "position" : "",
    'sva_balance': 0,
    'sva_address': '',
    'btc_balance': 0,
    'btc_address': '',
    'usd_balance': 0,
    'total_max_out': 0,
    'total_capital_back': 0,
    'total_commission': 0,
    'secret_2fa':'',
    'status_2fa': 0,
    "left" : "",
    's_left': 0,
    's_right': 0,
    's_p_node': 0,
    's_p_binary': 0,
    's_token': 0,
    's_id': 0
    }]
    db['users'].drop()
    db['users'].insert(users)
    inserted.append(users)

    admin = [{
        "_id" : "1175a9437u2b3b15a14174e0",
        'username':  'admin',
        'email' :  'admin@admin.com',
        'password': set_password('12345'),
        'sum_withdraw': 0,
        'sum_invest' : 0
    }]
    db['admins'].drop()
    db['admins'].insert(admin)
    inserted.append(admin)

    ticker = [{
        'btc_usd' : 7500,
        'sva_btc' : 0.00013333,
        'sva_usd' : 1
    }]
    db['tickers'].drop()
    db['tickers'].insert(ticker)

    return json.dumps(inserted)
   



