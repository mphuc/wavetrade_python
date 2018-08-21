from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model, admin_model, trading
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from time import gmtime, strftime
import time
import json
import os
from bson import ObjectId, json_util
import codecs
from random import randint
from hashlib import sha256
import urllib
import urllib2
from block_io import BlockIo
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)
__author__ = 'carlozamagni'

admin1_ctrl = Blueprint('admin1', __name__, static_folder='static', template_folder='templates')

def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)

def set_password(password):
    return generate_password_hash(password)
def format_usd(value):
    value = float(value)
    return '{:20,.2f}'.format(value)
@admin1_ctrl.route('/profit', methods=['GET', 'POST'])
def ProfitDaiyly():
    error = None
    if session.get('logged_in_admin') is None:
        return redirect('/admin/login')
    Query = db.profits.find({})
  

    data ={
            'menu' : 'profit',

            'data_query': Query
       
        }
    return render_template('admin/profit.html', data=data)
@admin1_ctrl.route('/updatePercent', methods=['POST'])
def updatePercent():
    error = None
    if session.get('logged_in_admin') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please login' 
        })
    percent = request.form['percent']
    if percent =='' or float(percent) == 0:
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter percent' 
        })

    date_ = datetime.utcnow()+ relativedelta(days=1)

    data_New = {
        'date_added' : date_,
        'percent': percent,
        'status': 0
    }
    db.profits.insert(data_New)
    return json.dumps({
        'status': 'success', 
        'message': 'Update Success ' 
    })
@admin1_ctrl.route('/resetPprofitdaily', methods=['GET', 'POST'])
def resetPprofitdaily():
    db.deposits.update({},{'$set': {'amount_daily':0}},multi=True)
    db.users.update({},{'$set': {'current_max_daily': 0, 'max_daily':30}},multi=True)
    return json.dumps({'status' : 'success'})

@admin1_ctrl.route('/update-ranking', methods=['GET', 'POST'])
def UpdateRanking():
    # return json.dumps({'status' : 'off'})
    listcustomer = db.users.find({})
    i = 0
    for x in listcustomer:
        i = i + 1
        total_team = 0
        total_team = float(x['total_team'])+float(x['total_invest'])
        total_team = round(total_team,0)
        ranking = 0
        # starter
        if total_team >= 10000:
            count_f1 = db.users.find({'p_node': x['customer_id']}).count()
            if float(count_f1) >= 2:
                ranking = 1
        # Gold
        if total_team >= 50000:
            count_f1 = db.users.find({'p_node': x['customer_id']}).count()
            if float(count_f1) >= 3:
                ranking = 2
        # Platinum
        if total_team >= 150000:
            count_gold = db.users.find({'p_node': x['customer_id'],  "ranking": 2}).count()
            if float(count_gold) >= 2:
                ranking = 3
        # Ruby
        if total_team >= 350000:
            count_starter = db.users.find({'p_node': x['customer_id'],  "ranking": 1}).count()
            count_gold = db.users.find({'p_node': x['customer_id'],  "ranking": 2}).count()
            count_platinum = db.users.find({'p_node': x['customer_id'],  "ranking": 3}).count()
            if float(count_gold) >= 1 and float(count_platinum) >= 1 and float(count_starter) >= 1:
                ranking = 4
        # Diamond
        if total_team >= 1000000:
            count_ruby = db.users.find({'p_node': x['customer_id'],  "ranking": 4}).count()
            count_platinum = db.users.find({'p_node': x['customer_id'],  "ranking": 3}).count()
            count_gold = db.users.find({'p_node': x['customer_id'],  "ranking": 2}).count()
            if float(count_ruby) >= 1 and float(count_platinum) >= 2 and float(count_gold) >=1:
                ranking = 5
        # Blue Diamond
        if total_team >= 2500000:
            count_ruby = db.users.find({'p_node': x['customer_id'],  "ranking": 4}).count()
            count_diamond = db.users.find({'p_node': x['customer_id'],  "ranking": 5}).count()
            count_platinum = db.users.find({'p_node': x['customer_id'],  "ranking": 3}).count()
            if float(count_ruby) >= 1 and float(count_diamond) >= 1 and float(count_platinum) >= 3:
                ranking = 6
        # AMBASSADOR
        if total_team >= 7000000:
            count_ruby = db.users.find({'p_node': x['customer_id'],  "ranking": 4}).count()
            count_diamond = db.users.find({'p_node': x['customer_id'],  "ranking": 5}).count()
            count_bluediamond = db.users.find({'p_node': x['customer_id'],  "ranking": 6}).count()
            if float(count_ruby) >= 2 and float(count_diamond) >= 1 and float(count_bluediamond) >=1:
                ranking = 7       
        if ranking > 0:
            print(i, ranking, x['username'])
            db.users.update({ "_id" :ObjectId(x['_id']) }, { '$set': { "ranking": float(ranking) } })
    return json.dumps({'status' : 'update ranking success'})

@admin1_ctrl.route('/update-sharing-bonusmonthqerqwerwqr', methods=['GET', 'POST'])
def updateSharingBonus():
    # return json.dumps({'status' : 'off'})
    listcustomer = db.users.find({"total_invest": { "$ne": 0 }})
    start = start = datetime(2018, 03, 01)
    end = datetime(2018, 03, 31, 23, 59, 59)
    for x in listcustomer:
        checkF1 = db.users.find({"creation":{'$gte':start,'$lt':end},'total_invest':{'$ne':0}, 'p_node':x['customer_id']}).count()
        if checkF1 >= 4:
            get_invest = db.deposits.find({ "status": 1, "uid": x['customer_id']})
            print(x['username'], checkF1, get_invest.count(), x['total_invest'])
            percent = 6
            commission = float(percent)/100
            amount_usd_invest = float(x['total_invest'])
            amount_daily = float(amount_usd_invest)*commission
            usd_balance = float(x['usd_balance'])
            new_usd_balance = float(amount_daily) + float(usd_balance)
            new_usd_balance = float(new_usd_balance)
            new_usd_balance = round(new_usd_balance,2)

            total_earn = float(x['total_earn'])
            new_total_earn = float(total_earn) + float(amount_daily)
            new_total_earn = float(new_total_earn)
            new_total_earn = round(new_total_earn,2)

            total_max_out = float(x['total_max_out'])
            new_total_max_out = float(amount_daily)+ float(total_max_out)
            new_total_max_out = float(new_total_max_out)
            new_total_earn = round(new_total_earn,2)

            sva_monthly_bonus = float(x['sva_monthly_bonus'])
            new_sva_monthly_bonus = float(amount_daily) + float(sva_monthly_bonus)
            new_sva_monthly_bonus = float(new_sva_monthly_bonus)
            new_sva_monthly_bonus = round(new_sva_monthly_bonus,2)
            roi = float(x['roi'])+float(amount_daily)
            roi =round(roi,2)

            sva_sharing_bonus = float(x['sva_sharing_bonus'])
            new_sva_sharing_bonus = float(amount_daily) + float(sva_sharing_bonus)
            new_sva_sharing_bonus = float(new_sva_sharing_bonus)
            new_sva_sharing_bonus = round(new_sva_sharing_bonus,2)
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {"sva_sharing_bonus": new_sva_sharing_bonus, "total_max_out": new_total_max_out,  "total_earn": new_total_earn, "usd_balance": new_usd_balance, "roi": roi } })
            data_history = {
                'uid' : x['customer_id'],
                'user_id': x['_id'],
                'username' : x['username'],
                'amount': format_usd(amount_daily),
                'type' : 'receive',
                'wallet': 'Sharing Bonus',
                'date_added' : datetime.utcnow(),
                'detail': 'Get '+ str(percent) +'% sharing bonus from total invest '+ str(format_usd(amount_usd_invest)) +' USD',
                'rate': '',
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            id_history = db.historys.insert(data_history)
    return json.dumps({'status' : 'update sharing success'})


@admin1_ctrl.route('/update-enterprise-commission', methods=['GET', 'POST'])
def UpdateEnterPrise():
    # return json.dumps({'status' : 'off'})
    listcustomer = db.users.find({"ranking": { "$gt": 0 }})
    data_ticker = db.tickers.find_one({})
    sva_usd = data_ticker['sva_usd']
    btc_usd = data_ticker['btc_usd']
    i = 0
    for x in listcustomer:
        if float(x['ranking']) == 1:
            percentx = 0.5
        if float(x['ranking']) == 2:
            percentx = 1
        if float(x['ranking']) == 3:
            percentx = 1.6
        if float(x['ranking']) == 4:
            percentx = 2.2
        if float(x['ranking']) == 5:
            percentx = 2.8
        if float(x['ranking']) == 6:
            percentx = 3.5
        if float(x['ranking']) == 7:
            percentx = 4
        if float(x['ranking']) == 8:
            percentx = 4.5
        i = i + 1
        find_f1 = db.users.find({'p_node': x['customer_id']})
        sva_usd_cms = float(x['sva_usd_cms'])
        total_earn = float(x['total_earn'])
        total_max_out = float(x['total_max_out'])
        sva_enterprise_cms = float(x['sva_enterprise_cms'])
        btc_balance = float(x['btc_balance'])
        btc_balance_satoshi = float(btc_balance)*100000000
        btc_direct_commission = float(x['btc_direct_commission'])
        btc_direct_commission_satoshi = btc_direct_commission*100000000
        sva_usdsva_balance = float(x['usd_balance'])
        amount_cms = 0
        amount_btc_cms_satoshi = 0
        amount_btc_direct_cms_satoshi = 0
        usd_commission = 0
        for y in find_f1:
            percenty = 0
            if float(y['ranking']) == 1:
                percenty = 0.5
            if float(y['ranking']) == 2:
                percenty = 1
            if float(y['ranking']) == 3:
                percenty = 1.6
            if float(y['ranking']) == 4:
                percenty = 2.2
            if float(y['ranking']) == 5:
                percenty = 2.8
            if float(y['ranking']) == 6:
                percenty = 3.5
            if float(y['ranking']) == 7:
                percenty = 4
            if float(y['ranking']) == 8:
                percenty = 4.5
            if float(y['total_amount_team']) > 0 and float(percentx) >= float(percenty):
                if float(percentx) == float(percenty):
                    percent = 0.5
                else:
                    percent = float(percentx) - float(percenty)

                commission = float(percent)/100
                amount_daily = float(y['total_amount_team'])*commission
                amount_cms = amount_cms + amount_daily

                usd_commission_btc = float(amount_daily)*0.8
                usd_commission_usdsva = float(amount_daily)*0.2

                btc_commission = float(usd_commission_btc)/float(btc_usd)
                btc_commission = round(btc_commission,8)
                btc_commission_satoshi = float(btc_commission)*100000000

                amount_btc_cms_satoshi = float(amount_btc_cms_satoshi) + float(btc_commission_satoshi)

                amount_btc_direct_cms_satoshi = float(amount_btc_direct_cms_satoshi) + float(btc_commission_satoshi)

                usd_commission = float(usd_commission) + float(usd_commission_usdsva)

                data_history = {
                    'uid' : x['customer_id'],
                    'user_id': str(x['_id']),
                    'username' : x['username'],
                    'amount': format_usd(amount_daily),
                    'type' : 'receive',
                    'wallet': 'Enterprise Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+ str(percent) +'% Enterprise commission from F1 '+ str(y['username']) +', team volume '+ str(format_usd(y['total_amount_team'])) +' USD',
                    'rate': '',
                    'txtid' : '' ,
                    'amount_sub' : 0,
                    'amount_add' : 0,
                    'amount_rest' : 0
                }
                id_history = db.historys.insert(data_history)
                db.users.update({ "_id" :ObjectId(y['_id']) }, { '$set': { "total_amount_team": 0 } })
        print(i, amount_cms, x['username'])
        if float(amount_cms) > 0:
            new_sva_usd_cms = float(amount_cms) + float(sva_usd_cms)
            new_sva_usd_cms = float(new_sva_usd_cms)
            new_sva_usd_cms = round(new_sva_usd_cms,2)

            new_total_earn = float(total_earn) + float(amount_cms)
            new_total_earn = float(new_total_earn)
            new_total_earn = round(new_total_earn,2)
            
            new_total_max_out = float(amount_cms)+ float(total_max_out)
            new_total_max_out = float(new_total_max_out)
            new_total_earn = round(new_total_earn,2)
            
            new_sva_enterprise_cms = float(amount_cms) + float(sva_enterprise_cms)
            new_sva_enterprise_cms = float(new_sva_enterprise_cms)
            new_sva_enterprise_cms = round(new_sva_enterprise_cms,2)

            new_btc_balance_satoshi = float(amount_btc_cms_satoshi) + float(btc_balance_satoshi)
            new_btc_balance = float(new_btc_balance_satoshi)/100000000
            new_btc_balance = round(new_btc_balance, 8)

            new_btc_direct_commission_satoshi  = amount_btc_direct_cms_satoshi + btc_direct_commission_satoshi
            new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
            new_btc_direct_commission = round(new_btc_direct_commission,8)

            new_usd_balance = float(sva_usdsva_balance) + float(usd_commission)
            new_usd_balance = round(new_usd_balance, 2)

            db.users.update({ "_id" :ObjectId(x['_id']) }, { '$set': {"btc_balance": float(new_btc_balance), "usd_balance": float(new_usd_balance), "btc_direct_commission": float(new_btc_direct_commission), "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_enterprise_cms': new_sva_enterprise_cms, 'total_max_out':  new_total_max_out} })
        total_team = 0
        total_team = float(x['total_team'])
    return json.dumps({'status' : 'update Enterprise success'})

@admin1_ctrl.route('/update_maxout', methods=['GET', 'POST'])
def madwqer():
    return json.dumps({'status' : 'off'})
    get_invest = db.users.find({})
    i = 0
    for x in get_invest:
        i = i + 1
        new_total_invest = 0
        new_total_invest = float(x['total_invest'])
        max_out = 0
        if new_total_invest >= 100 and new_total_invest < 1000:
            max_out = 1000
            level =2
        if new_total_invest >= 1000 and new_total_invest < 5000:
            max_out = 5000
            level =3
        if new_total_invest >= 5000 and new_total_invest < 10000:
            max_out = 10000
            level =4
        if new_total_invest >= 10000 and new_total_invest < 50000:
            max_out = 20000
            level =5
        if new_total_invest >= 50000:
            max_out = 30000
            level =6
        print(i, max_out, x['username'])
        db.users.update({ "_id" :ObjectId(x['_id']) }, { '$set': { "max_out": float(max_out) } })
    return json.dumps({'status' : 'error'})
    # else:
    #     db.profits.update({ "status" :0 }, { '$set': { "status": 1 } })