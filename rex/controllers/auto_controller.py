from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model, wallet_model
import json
import urllib
import urllib2
from bson.objectid import ObjectId
from block_io import BlockIo
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time


version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)

__author__ = 'carlozamagni'

auto_ctrl = Blueprint('auto', __name__, static_folder='static', template_folder='templates')

def binaryInsert(customer_ml_p_binary, binary_amount_recieve):
    binary_amount_recieves = float(customer_ml_p_binary.r_wallet) + float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "r_wallet": binary_amount_recieves } })

    binary_amount_sum = float(customer_ml_p_binary.s_wallet) + float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "s_wallet": binary_amount_sum } })

    binary_total_earns = float(customer_ml_p_binary.total_earn)+float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "total_earn": binary_total_earns } })

    binary_data_send = {
        'date_added': datetime.utcnow(),
        'uid' : customer_ml_p_binary.customer_id,
        'name' : customer_ml_p_binary.username,
        'amount_sub' : 0,
        'amount_add' : binary_amount_recieve/1000000,
        'amount_rest' : binary_amount_sum/1000000,
        'type' : "Binary Commission ",
        'detail' : 'Earn 4% Binary bonus on downline'
    }
    history_ids = db.history.insert(binary_data_send)
    return history_ids

def SaveHistory(uid, user_id, username, amount, types, wallet, detail, rate, txtid):
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : username,
        'amount': float(amount),
        'type' : types,
        'wallet': wallet,
        'date_added' : datetime.utcnow(),
        'detail': detail,
        'rate': rate,
        'txtid' : txtid,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    return True

@auto_ctrl.route('/binaryBonusOprHJhEp/4cLi4bO4ISCjVauHrkNa5oIc/<ids>', methods=['GET', 'POST'])
def caculator_binary(ids):
    # return json.dumps({'status' : 'off'})
    if ids =='RsaW3Kb1gDkdRUGDo':
        countUser = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]}).count()
        if countUser > 0:
            user = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]})
            # user = db.users.find({'username':'robertnguyen'})
            for x in user:
                if x['total_pd_left'] > x['total_pd_right']:
                    balanced = x['total_pd_right']
                    pd_left = float(x['total_pd_left'])-float(x['total_pd_right'])
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_left": pd_left } })
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_right": 0 } })
                else:
                    balanced = x['total_pd_left']
                    pd_right = float(x['total_pd_right'])-float(x['total_pd_left'])
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_left": 0 } })
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_right": pd_right } })
                percent = 0
                total_invest = float(x['total_invest'])
                if float(total_invest) < 10000:
                    percent = 3
                if float(total_invest) < 50000 and float(total_invest) >= 10000:
                    percent = 4
                if float(total_invest) >= 50000:
                    percent = 5
                percent_commission = float(percent)/100
                amount_recieve = balanced*percent_commission
                total_maxout_week =  float(x['total_max_out'])
                max_out = float(x['max_out'])
                total_maxout_week = round(total_maxout_week, 2)
                
                total_max_earn = amount_recieve
                if float(total_max_earn) > float(x['max_out']):
                    amount_recieve = float(max_out)
                    print str(x['username']) + '=============='+str(amount_recieve)
                amount_recieve = round(float(amount_recieve), 2)
                # amount_recieves = float(x['r_wallet']) + float(amount_recieve)
                usd_balance = float(x['usd_balance'])
                new_usd_balance = float(amount_recieve) + float(usd_balance)
                total_earn = float(x['total_earn'])
                new_total_earn = float(total_earn) + float(amount_recieve)
                new_total_earn = float(new_total_earn)
                total_max_out = float(x['total_max_out'])
                new_total_max_out = float(amount_recieve)+ float(total_max_out)
                new_total_max_out = float(new_total_max_out)
                print(x['username'], total_invest, percent, balanced, amount_recieve, total_maxout_week)
                print "======================================="
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { "usd_balance": round(new_usd_balance,2), 'total_earn': round(new_total_earn,0), 'total_max_out': round(new_total_max_out,0) } })
                detail = 'Get '+str(percent)+' '+"""%"""+' binary bonus (small tree %s USD)' %(balanced)
                SaveHistory(x['customer_id'],x['_id'],x['username'], amount_recieve, 'receive', 'USD', detail, '', '')
                # db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "r_wallet": amount_recieves } })

                # amount_sum = float(x['s_wallet']) + float(amount_recieve)
                # db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "s_wallet": amount_sum } })

                # total_earns = float(x['total_earn'])+float(amount_recieve)
                # db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_earn": total_earns } })
                # data_send = {
                #     'date_added': datetime.utcnow(),
                #     'uid' : x['customer_id'],
                #     'name' : x['username'],
                #     'amount_sub' : 0,
                #     'amount_add' : amount_recieve/1000000,
                #     'amount_rest' : amount_sum/1000000,
                #     'type' : "Binary Commission",
                #     'detail' : 'Earn 10% Binary commission'
                # }
                # history_id = db.history.insert(data_send)
                # count = 0
                # customer_ml = db.User.find_one({"customer_id" : x['customer_id'] })
                # percent_binary = 4
                # percent_binary_commission = 0.04
                # binary_amount_recieve = amount_recieve*percent_binary_commission
         
                # while (True):
                #     customer_ml_p_binary = db.User.find_one({"customer_id" : customer_ml.p_binary })

                #     if count == 0 and int(customer_ml_p_binary.level) >= 2:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)

                #     if count == 1 and int(customer_ml_p_binary.level) >= 2:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)

                #     if count == 2 and int(customer_ml_p_binary.level) >= 3:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)

                #     if count == 3 and int(customer_ml_p_binary.level) >= 4:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)

                #     if count == 4 and int(customer_ml_p_binary.level) >= 5:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)

                #     if count == 5 and int(customer_ml_p_binary.level) >= 6:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)
                        
                #     if count == 6 and int(customer_ml_p_binary.level) >= 7:
                #         binaryInsert(customer_ml_p_binary, binary_amount_recieve)
                    
                #     count = count + 1
                #     if count == 7 or customer_ml_p_binary.customer_id== '1010101001':
                #         break
                #     customer_ml = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
                # else:
                #     return json.dumps({'status' : 'error'})

        return json.dumps({'status' : 'success'})
    else:
        return json.dumps({'status' : 'error'})