from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response
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
import requests
import string
import random

version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)
# BTC TEST
# block_io = BlockIo('c11b-501c-0192-ab2c', 'SECRET PIN', version) 
__author__ = 'carlozamagni'

deposit_ctrl = Blueprint('deposit', __name__, static_folder='static', template_folder='templates')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True
def format_usd(value):
    value = float(value)
    return '{:20,.2f}'.format(value)
def format_btc(value):
    value = float(value)
    return '{:20,.8f}'.format(value)


@deposit_ctrl.route('/api/team-volume-commission', methods=['GET', 'POST'])
def TeamVolumeCommission():
    # return json.dumps({'status' : 'off'})
    listcustomer = db.tradings.find({"level": { "$gt": 0 }})
    i = 0
    for x in listcustomer:
        if float(x['level']) == 1:
            percentx = 0.05
        if float(x['level']) == 2:
            percentx = 0.2
        if float(x['level']) == 3:
            percentx = 0.4
        if float(x['level']) == 4:
            percentx = 0.6
        if float(x['level']) == 5:
            percentx = 0.8
        if float(x['level']) == 6:
            percentx = 0.9
        i = i + 1
        find_f1 = db.tradings.find({'p_node': x['user_id']})
        # sva_usd_cms = float(x['sva_usd_cms'])
        customer = db.users.find_one({'_id': ObjectId(x['user_id'])})
        balance_commission = customer['balance_commission']
        new_balance_commission = 0
        amount_cms = 0

        for y in find_f1:
            percenty = 0
            if float(y['level']) == 1:
                percenty = 0.05
            if float(y['level']) == 2:
                percenty = 0.2
            if float(y['level']) == 3:
                percenty = 0.4
            if float(y['level']) == 4:
                percenty = 0.6
            if float(y['level']) == 5:
                percenty = 0.8
            if float(y['level']) == 6:
                percenty = 0.9
     
            if float(y['team_volume']) > 0 and float(percentx) > float(percenty):
                percent = float(percentx) - float(percenty)
                commission = float(percent)/100
                amount_daily = float(y['team_volume'])*commission
                new_balance_commission = new_balance_commission + amount_daily

                # data_history = {
                #     'uid' : x['customer_id'],
                #     'user_id': str(x['_id']),
                #     'username' : x['username'],
                #     'amount': format_usd(amount_daily),
                #     'type' : 'receive',
                #     'wallet': 'Enterprise Commission',
                #     'date_added' : datetime.utcnow(),
                #     'detail': 'Get '+ str(percent) +'% Enterprise commission from F1 '+ str(y['username']) +', team volume '+ str(format_usd(y['total_amount_team'])) +' USD',
                #     'rate': '',
                #     'txtid' : '' ,
                #     'amount_sub' : 0,
                #     'amount_add' : 0,
                #     'amount_rest' : 0
                # }
                # id_history = db.historys.insert(data_history)
                # db.users.update({ "_id" :ObjectId(y['_id']) }, { '$set': { "team_volume": 0 } })
        if float(new_balance_commission) > 0:
            print new_balance_commission
            print x['user_id']
            new_balance_commission = float(new_balance_commission) + float(balance_commission)
            # new_sva_usd_cms = float(new_sva_usd_cms)
            # new_sva_usd_cms = round(new_sva_usd_cms,2)

            db.users.update({ "_id" :ObjectId(x['user_id']) }, { '$set': {"balance_commission": float(new_balance_commission)} })
    return json.dumps({'status' : 'update team_volume success'})

@deposit_ctrl.route('/api/referral', methods=['GET', 'POST'])
def depositApiRefferal():
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    getTrading = db.tradings.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = 0
            if float(x['amount']) >= 100:
                level = 1
            check_start_ib = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 1}] })
            check_startIB = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 2}] })
            check_master_ib = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 5}] })
            if float(x['amount']) >= 200 and check_start_ib.count() >= 3:
                level = 2
            if float(x['amount']) >= 400 and check_start_ib.count() >= 10:
                level = 3
            if float(x['amount']) >= 600 and check_start_ib.count() >= 15:
                level = 4
            if float(x['amount']) >= 800 and check_start_ib.count() >= 20:
                level = 5
            if float(x['amount']) >= 1000 and check_startIB.count() >= 10 and check_master_ib.count() >= 10:
                level = 6
            db.tradings.update({ "user_id" : x['user_id'] }, { '$set': {'level': level} })
        return json.dumps({'success' : 1})
    else:
        return json.dumps({'success' : 0})

@deposit_ctrl.route('/api/caculate-referral', methods=['GET', 'POST'])
def CaculateRefferal():
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    getTrading = db.tradings.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = 0
            percent = 0
            if float(x['total_f1']) >= 100 and float(x['level']) == 1:
                percent = 0.05
            if float(x['total_f1']) >= 100 and float(x['level']) == 2:
                percent = 0.2
            if float(x['total_f1']) >= 100 and float(x['level']) == 3:
                percent = 0.4
            if float(x['total_f1']) >= 100 and float(x['level']) == 4:
                percent = 0.6
            if float(x['total_f1']) >= 100 and float(x['level']) == 5:
                percent = 0.8
            if float(x['total_f1']) >= 100 and float(x['level']) == 6:
                percent = 0.9

            if float(percent) > 0:
                commission = float(percent)* float(x['total_f1'])
                commission = float(commission)/100
                customer = db.users.find_one({'_id': ObjectId(x['user_id'])})
                if customer is not None and customer.has_key("balance_commission"):
                    balance_commission = customer['balance_commission']
                    new_balance_commission = float(balance_commission)+ float(commission)
                    db.users.update(
                        { "_id" : ObjectId(x['user_id']) }, 
                        { 
                            '$set': {
                            "balance_commission": float(new_balance_commission)
                            }
                        }
                    )

                # db.users.update(
                # { "_id" : ObjectId(x['user_id']) }, 
                #     { 
                #         '$set': {
                #               "balance.coin_wallet.available": float(new_coin_balance)
                #           },
                #         '$push': {
                #               'balance.coin_wallet.history': {
                #                 'date': datetime.utcnow(), 
                #                 'type': 'received', 
                #                 'amount': float(win_bet), 
                #                 'detail': "You have won "+str(win_bet)+" CUP"
                #               }
                #             }
                #     }
                # )

                # customer = db.users.find_one({'_id': ObjectId(x['user_id'])})
                # db.users.update({ "_id" : ObjectId(x['user_id']) }, { '$set': {"sva_balance": new_sva_balance, 'btc_balance': new_btc_balance, "total_invest": new_total_invest, 'max_out': max_out, 'level': 2 } })
                # data_history = {
                # 'uid' : uid,
                # 'user_id': user_id,
                # 'username' : user['username'],
                # 'amount': float(convert_usd_sva),
                # 'type' : 'send',
                # 'wallet': 'SVA',
                # 'date_added' : datetime.utcnow(),
                # 'detail': 'Paid for invest %s SVA' %(convert_usd_sva),
                # 'rate': '1 SVA = %s USD' %(sva_usd),
                # 'txtid' : '' ,
                # 'amount_sub' : 0,
                # 'amount_add' : 0,
                # 'amount_rest' : 0
                # }
                # db.historys.insert(data_history)

        return json.dumps({'success' : 1})
    else:
        return json.dumps({'success' : 0})


@deposit_ctrl.route('/api/caculate-teamvolume', methods=['GET', 'POST'])
def CaculateTeamvolume():
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    getTrading = db.tradings.find({'check_team_volume': 0})
    if getTrading.count()  > 0:
        for x in getTrading:
            if float(x['amount']) > 0:
                binaryAmount(x['user_id'], x['amount'])
            db.tradings.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'check_team_volume': 1} })
        return json.dumps({'success' : 1})
    else:
        return json.dumps({'success' : 0})

@deposit_ctrl.route('/api/deposit/<customer_id>/<amount_trade>', methods=['GET', 'POST'])
def depositApi(customer_id, amount_trade):
    checkUser = db.tradings.find_one({'user_id': str(customer_id)})
    if checkUser is None:
        return json.dumps({'success' : 0})
    else:
        print checkUser['p_node']
        if checkUser['p_node'] != '0':
            parrent = db.tradings.find_one({'user_id': str(checkUser['p_node'])})
            if parrent is not None:
                reFerralBonus(str(checkUser['p_node']), amount_trade)
        binaryAmount(customer_id, amount_trade)
    return json.dumps({'success' : 1})
def reFerralBonus(user_id, amount_invest):
    customer = db.tradings.find_one({"user_id" : user_id })
    if customer is not None:
        total_f1 = customer['total_f1']
        new_total_f1 = float(total_f1) + float(amount_invest)
        db.tradings.update({ "user_id" : user_id }, { '$set': {'total_f1': new_total_f1} })
def binaryAmount(user_id, amount_invest):
    customer_ml = db.tradings.find_one({"user_id" : user_id })
    amount = customer_ml['amount']
    new_amount = float(amount) + float(amount_invest)
    new_amount = round(new_amount, 2)
    # db.tradings.update({ "_id" : ObjectId(customer_ml['_id']) }, { '$set': {'amount': new_amount} })
    # print customer_ml['p_node']
    if customer_ml['p_node'] != '' or customer_ml['p_node'] != '0':
        i = 0
        while (True):
            customer_ml_p_node = db.tradings.find_one({"user_id" : customer_ml['p_node'] })
            if customer_ml_p_node is None:
                break
            else:
                print customer_ml_p_node['p_node']
                team_volume = customer_ml_p_node['team_volume']
                new_team_volume = float(team_volume) + float(amount_invest)
                new_team_volume = round(new_team_volume, 2)
                # i = i + 1
                # if i >= 2:
                db.tradings.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume': new_team_volume} })
                checkNode = db.tradings.find({"user_id" : customer_ml_p_node['user_id'] })
                # print checkNode.count()
                if checkNode.count() == 0 or customer_ml_p_node['p_node'] == '' or customer_ml_p_node['p_node'] == '0':
                    break
            customer_ml = db.tradings.find_one({"user_id" : customer_ml_p_node['user_id'] })
            if customer_ml is None:
                break
    return True
def SaveHistory(uid, user_id, username, amount, types, wallet, detail, rate, txtid):
    if types == 'BTC' or types == 'BTC Commission':
        amount_save = format_btc(amount)
    else:
        amount_save = format_usd(amount)
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : username,
        'amount': amount_save,
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
def FnRefferalProgramAuto(user_id, amount_invest):
    customer = db.users.find_one({"customer_id" : user_id })
    username_invest = customer['username']
    if customer['p_node'] != '0' or customer['p_node'] != '':
        for x in xrange(1,6):
            customer_p_node = db.users.find_one({"customer_id" : customer['p_node'] })
            if customer_p_node is None:
                return True
            else:

                if customer_p_node:
                    if x == 1 and customer_p_node['level'] >= 2:
                        print(customer_p_node['username'], 'F1')
                        commission = float(amount_invest)*0.07
                        commission = round(commission,2)
                        usd_balance = float(customer_p_node['usd_balance'])
                        new_usd_balance = float(commission) + float(usd_balance)
                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)

                        print total_max_out
                        print customer_p_node['max_out']
                        # =======================
                        if float(total_max_out) < float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"total_max_out":new_total_max_out, "sva_direct_cms": new_sva_direct_cms, "usd_balance": new_usd_balance, 'total_earn': new_total_earn } })
                            detail = 'Get 7 '+"""%"""+' referral bonus from member %s invest %s USD' %(username_invest, amount_invest)
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'USD', detail, '', '')
                        #========================
                checkNode = db.users.find({"customer_id" : customer_p_node['customer_id'] })
                if checkNode.count() == 0 or customer_p_node['customer_id'] == '11201729184651' or customer_p_node['p_node'] == '0' or customer_p_node['p_node'] == '':
                    return True
            customer = db.users.find_one({"customer_id" : customer_p_node['customer_id'] })
    return True
def FnRefferalProgram(user_id, amount_invest, btc_usd):
    customer = db.users.find_one({"customer_id" : user_id })
    username_invest = customer['username']
    if customer['p_node'] != '0' or customer['p_node'] != '':
        for x in xrange(1,10):
            customer_p_node = db.users.find_one({"customer_id" : customer['p_node'] })
            if customer_p_node is None:
                return True
            else:
                if customer_p_node:
                    if x == 1 and customer_p_node['level'] >= 2:
                        print(customer_p_node['username'], 'F1')
                        commission = float(amount_invest)*0.07
                        commission = round(commission,2)
                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)
                        
                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 7 '+"""%"""+' referral bonus from F1 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                        #========================
                    if x == 2 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 1:
                        print(customer_p_node['username'], 'F2')
                        commission = float(amount_invest)*0.03
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 3 '+"""%"""+' referral bonus from F2 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                    if x == 3 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 2:
                        print(customer_p_node['username'], 'F3')
                        commission = float(amount_invest)*0.015
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 1.5 '+"""%"""+' referral bonus from F3 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                        #========================
                    if x == 4 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 3:
                        print(customer_p_node['username'], 'F4')
                        commission = float(amount_invest)*0.0075
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.75 '+"""%"""+' referral bonus from F4 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                        #========================
                    if x == 5 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 4:
                        print(customer_p_node['username'], 'F5')
                        commission = float(amount_invest)*0.0075
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.75 '+"""%"""+' referral bonus from F5 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                    if x == 6 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 5:
                        print(customer_p_node['username'], 'F6')
                        commission = float(amount_invest)*0.0025
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)


                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.25 '+"""%"""+' referral bonus from F6 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                    if x == 7 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 6:
                        print(customer_p_node['username'], 'F7')
                        commission = float(amount_invest)*0.0025
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.25 '+"""%"""+' referral bonus from F7 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')    
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                    if x == 8 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 7:
                        print(customer_p_node['username'], 'F8')
                        commission = float(amount_invest)*0.00125
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.125 '+"""%"""+' referral bonus from F8 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                    if x == 9 and customer_p_node['level'] >= 2 and customer_p_node['ranking'] >= 7:
                        print(customer_p_node['username'], 'F9')
                        commission = float(amount_invest)*0.00125
                        commission = round(commission,2)

                        usd_commission_btc = float(commission)*0.8
                        usd_commission_usdsva = float(commission)*0.2

                        btc_commission = float(usd_commission_btc)/float(btc_usd)
                        btc_commission = round(btc_commission,8)
                        btc_balance = float(customer_p_node['btc_balance'])
                        btc_commission_satoshi = float(btc_commission)*100000000
                        btc_balance_satoshi = float(btc_balance)*100000000
                        new_btc_balance_satoshi = float(btc_commission_satoshi) + float(btc_balance_satoshi)
                        new_btc_balance = float(new_btc_balance_satoshi)/100000000
                        new_btc_balance = round(new_btc_balance, 8)

                        btc_direct_commission = float(customer_p_node['btc_direct_commission'])
                        btc_direct_commission_satoshi = btc_direct_commission*100000000
                        new_btc_direct_commission_satoshi  = btc_direct_commission_satoshi + btc_commission_satoshi
                        new_btc_direct_commission = float(new_btc_direct_commission_satoshi)/100000000
                        new_btc_direct_commission = round(new_btc_direct_commission,8)

                        sva_usdsva_balance = float(customer_p_node['usd_balance'])
                        new_usdsva_balance = float(sva_usdsva_balance) + float(usd_commission_usdsva)
                        new_usdsva_balance = round(new_usdsva_balance, 2)

                        sva_usd_cms = float(customer_p_node['sva_usd_cms'])
                        new_sva_usd_cms = float(commission) + float(sva_usd_cms)
                        new_sva_usd_cms = float(new_sva_usd_cms)
                        new_sva_usd_cms = round(new_sva_usd_cms,2)

                        total_earn = float(customer_p_node['total_earn'])
                        new_total_earn = float(total_earn) + float(commission)
                        new_total_earn = float(new_total_earn)
                        new_total_earn = round(new_total_earn,2)

                        total_max_out = float(customer_p_node['total_max_out'])
                        new_total_max_out = float(commission)+ float(total_max_out)
                        new_total_max_out = float(new_total_max_out)
                        new_total_earn = round(new_total_earn,2)

                        sva_direct_cms = float(customer_p_node['sva_direct_cms'])
                        new_sva_direct_cms = float(commission) + float(sva_direct_cms)
                        new_sva_direct_cms = float(new_sva_direct_cms)
                        new_sva_direct_cms = round(new_sva_direct_cms,2)
                        # =======================
                        if float(total_max_out) <= float(customer_p_node['max_out']):
                            db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {"btc_direct_commission":new_btc_direct_commission, "btc_balance": new_btc_balance, "usd_balance": new_usdsva_balance, "sva_usd_cms": new_sva_usd_cms, 'total_earn': new_total_earn, 'sva_direct_cms': new_sva_direct_cms, 'total_max_out':  new_total_max_out} })
                            detail = 'Get 0.125 '+"""%"""+' referral bonus from F9 %s invest %s USD' %(username_invest, format_usd(amount_invest))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'Direct Commission', detail, '', '')
                            detail_usd = 'Get 20 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], usd_commission_usdsva, 'receive', 'USD', detail_usd, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC Commission', detail_btc, '', '')
                            detail_btc = 'Get 80 '+"""%"""+' from Direct commission %s USD' %(format_usd(commission))
                            # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], btc_commission, 'receive', 'BTC', detail_btc, '', '')
                checkNode = db.users.find({"customer_id" : customer_p_node['customer_id'] })
                if checkNode.count() == 0 or customer_p_node['customer_id'] == '11201729184651' or customer_p_node['p_node'] == '0' or customer_p_node['p_node'] == '':
                    return True
            customer = db.users.find_one({"customer_id" : customer_p_node['customer_id'] })
    return True

@deposit_ctrl.route('/LendingConfirm', methods=['GET', 'POST'])
def LendingConfirm():
    # return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            sva_amount = request.form['sva_amount']
            usd_amount = request.form['usd_amount']
            checkIsNumberSVA = is_number(sva_amount)
            if sva_amount == '' or checkIsNumberSVA == False:
                return json.dumps({
                    'status': 'error', 
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })

            data_ticker = db.tickers.find_one({})
            sva_usd = data_ticker['sva_usd']
            btc_usd = data_ticker['btc_usd']
            usd_amount = float(request.form['usd_amount'])
            usd_amount = round(usd_amount, 0)
            convert_usd_sva_btc = float(usd_amount)/2
            convert_usd_sva = float(convert_usd_sva_btc)/float(sva_usd)
            convert_usd_sva = round(convert_usd_sva, 8)
            sva_balance = float(user['sva_balance'])
            if float(convert_usd_sva) > float(sva_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your SVA balance is not enough' 
                })
            convert_usd_btc = float(convert_usd_sva_btc)/float(btc_usd)
            convert_usd_btc = round(convert_usd_btc, 8)
            convert_btc_satoshi = float(convert_usd_btc)*100000000
            btc_balance = float(user['btc_balance'])
            btc_balance_satoshi = float(btc_balance)*100000000
            if float(convert_btc_satoshi) > float(btc_balance_satoshi):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your BTC balance is not enough' 
                })

            new_sva_balance = float(sva_balance) - float(convert_usd_sva)
            new_sva_balance = round(new_sva_balance, 8)

            new_btc_balance = float(btc_balance_satoshi) - float(convert_btc_satoshi)
            new_btc_balance = float(new_btc_balance)/100000000

            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)
            max_out = new_total_invest*3
            max_out = round(max_out,0)
            binary = binaryAmount(uid, usd_amount)
            FnRefferalProgram(uid, usd_amount, btc_usd)
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"sva_balance": new_sva_balance, 'btc_balance': new_btc_balance, "total_invest": new_total_invest, 'max_out': max_out, 'level': 2 } })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_sva),
                'type' : 'send',
                'wallet': 'SVA',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s SVA' %(convert_usd_sva),
                'rate': '1 SVA = %s USD' %(sva_usd),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)
            data_historys = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_sva),
                'type' : 'send',
                'wallet': 'BTC',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s BTC' %(convert_usd_btc),
                'rate': '1 SVA = %s USD' %(sva_usd),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_historys)
            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 180
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 180
            if float(usd_amount) >= 5000 and float(usd_amount) < 10000:
                day = 150
            if float(usd_amount) >= 10000 and float(usd_amount) < 50000:
                day = 120
            if float(usd_amount) >= 50000 and float(usd_amount) < 100000:
                day = 90
            if float(usd_amount) >= 100000:
                day = 90
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': float(convert_usd_sva),
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  0,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0,
                'type_invest': 0
            }
            db.deposits.insert(data_deposit)
            return json.dumps({
                'status': 'success', 
                'message': 'Investment success',
                'new_sva_balance': new_sva_balance,
                'new_total_invest': new_total_invest
            })

@deposit_ctrl.route('/InvestConfirm', methods=['GET', 'POST'])
def InvestConfirm():
    # return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        print request.form
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            sva_amount = request.form['sva_amount']
            usd_amount = request.form['usd_amount']
            checkIsNumberSVA = is_number(sva_amount)
            if sva_amount == '' or checkIsNumberSVA == False:
                return json.dumps({
                    'status': 'error', 
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })

            data_ticker = db.tickers.find_one({})
            sva_usd = data_ticker['sva_usd']
            btc_usd = data_ticker['btc_usd']
            usd_amount = float(request.form['usd_amount'])
            usd_amount = round(usd_amount, 0)
            convert_usd_sva_btc = float(usd_amount)/2

            convert_30_sva = float(convert_usd_sva_btc)*0.6
            convert_20_usdsva = float(convert_usd_sva_btc)*0.4

            convert_usd_sva = float(convert_30_sva)/float(sva_usd)
            convert_usd_sva = round(convert_usd_sva, 8)

            sva_balance = float(user['sva_balance'])
            sva_satoshi = sva_balance*100000000
            convert_usd_sva_satoshi = convert_usd_sva*100000000
            if float(convert_usd_sva_satoshi) > float(sva_satoshi):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your SVA balance is not enough' 
                })

            usdsva_balance = float(user['sva_usdsva'])

            if float(convert_20_usdsva) > float(usdsva_balance):
                return json.dumps({
                'status': 'error', 
                'message': 'Your USDSVA balance is not enough' 
                })

            convert_usd_btc = float(convert_usd_sva_btc)/float(btc_usd)
            convert_usd_btc = round(convert_usd_btc, 8)
            convert_btc_satoshi = float(convert_usd_btc)*100000000
            btc_balance = float(user['btc_balance'])
            btc_balance_satoshi = float(btc_balance)*100000000
            if float(convert_btc_satoshi) > float(btc_balance_satoshi):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your BTC balance is not enough' 
                })

            new_usdsva_balance = float(usdsva_balance) - float(convert_20_usdsva)
            new_usdsva_balance = round(new_usdsva_balance, 2)

            new_sva_balance = float(sva_satoshi) - float(convert_usd_sva_satoshi)
            new_sva_balance = float(new_sva_balance)/100000000
            new_sva_balance = round(new_sva_balance, 8)

            new_btc_balance = float(btc_balance_satoshi) - float(convert_btc_satoshi)
            new_btc_balance = float(new_btc_balance)/100000000
            new_btc_balance = round(new_btc_balance, 8)

            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)
            max_out = new_total_invest*3
            max_out = round(max_out,0)
            binary = binaryAmount(uid, usd_amount)
            FnRefferalProgram(uid, usd_amount, btc_usd)
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"sva_usdsva": float(new_usdsva_balance), "sva_balance": new_sva_balance, 'btc_balance': new_btc_balance, "total_invest": new_total_invest, 'max_out': max_out, 'level': 2 } })
            convert_20_usdsva = round(convert_20_usdsva,2)
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_sva),
                'type' : 'send',
                'wallet': 'SVA',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s SVA' %(convert_usd_sva),
                'rate': '1 SVA = %s USD' %(sva_usd),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)
            data_historys = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_20_usdsva),
                'type' : 'send',
                'wallet': 'USDSVA',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s USDSVA' %(convert_20_usdsva),
                'rate': '1 SVA = %s USD' %(sva_usd),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_historys)
            data_historyss = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_btc),
                'type' : 'send',
                'wallet': 'BTC',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s BTC' %(convert_usd_btc),
                'rate': '1 SVA = %s USD' %(sva_usd),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_historyss)
            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 180
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 180
            if float(usd_amount) >= 5000 and float(usd_amount) < 10000:
                day = 150
            if float(usd_amount) >= 10000 and float(usd_amount) < 50000:
                day = 120
            if float(usd_amount) >= 50000 and float(usd_amount) < 100000:
                day = 90
            if float(usd_amount) >= 100000:
                day = 90
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': float(convert_usd_sva),
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  0,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0,
                'type_invest': 1
            }
            db.deposits.insert(data_deposit)
            return json.dumps({
                'status': 'success', 
                'message': 'Investment success',
                'new_sva_balance': new_sva_balance,
                'new_total_invest': new_total_invest
            })

@deposit_ctrl.route('/LendingConfirmRe', methods=['GET', 'POST'])
def LendingConfirmRe():
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            sva_amount = request.form['sva_amount']
            usd_amount = request.form['usd_amount']
            checkIsNumberSVA = is_number(sva_amount)
            usd_amount = round(float(usd_amount), 0)
            if sva_amount == '' or checkIsNumberSVA == False:
                return json.dumps({
                    'status': 'error', 
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100 or float(usd_amount) > 100000:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            usd_balance = float(user['usd_balance'])
            if float(usd_amount) > float(usd_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your balance is not enough' 
                })
            new_usd_balance = float(usd_balance) - float(usd_amount)
            new_usd_balance = round(new_usd_balance, 2)
            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)
            max_out = new_total_invest*3
            max_out = round(max_out,0)
            binary = binaryAmount(uid, float(usd_amount))
            FnRefferalProgram(uid, float(usd_amount))
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"usd_balance": new_usd_balance, "total_invest": new_total_invest, 'max_out': max_out } })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(usd_amount),
                'type' : 'send',
                'wallet': 'USD',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for invest %s USD from USD wallet' %(usd_amount),
                'rate': '',
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)
            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 180
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 180
            if float(usd_amount) >= 5000 and float(usd_amount) < 10000:
                day = 150
            if float(usd_amount) >= 10000 and float(usd_amount) < 50000:
                day = 120
            if float(usd_amount) >= 50000 and float(usd_amount) < 100000:
                day = 90
            if float(usd_amount) >= 100000:
                day = 90
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': 0,
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  0,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0
            }
            db.deposits.insert(data_deposit)
            return json.dumps({
                'status': 'success', 
                'message': 'Lending success',
                'new_sva_balance': new_usd_balance,
                'new_total_invest': new_total_invest
            })


def AutoLendingConfirm(user_id, uid, sva_amount, usd_amount):
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })

    user = db.users.find_one({'_id': ObjectId(user_id)})

    checkIsNumberSVA = is_number(sva_amount)
    if sva_amount == '' or checkIsNumberSVA == False:
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter valid quantity (quantity > 100)' 
        })
    checkIsNumberUSD = is_number(usd_amount)
    if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100:
        return json.dumps({
            'status': 'error',
            'message': 'Please enter valid quantity (quantity > 100)' 
        })

    data_ticker = db.tickers.find_one({})
    sva_usd = 3
    usd_amount = round(usd_amount, 0)
    convert_usd_sva = float(usd_amount)/float(sva_usd)
    convert_usd_sva = round(convert_usd_sva, 8)
    sva_balance = float(user['sva_balance'])
    if float(convert_usd_sva) > float(sva_balance):
        return json.dumps({
            'status': 'error', 
            'message': 'Your balance is not enough' 
        })
    new_sva_balance = float(sva_balance) - float(convert_usd_sva)
    new_sva_balance = round(new_sva_balance, 8)
    total_invest = float(user['total_invest'])

    new_total_invest = float(usd_amount) + float(total_invest)
    new_total_invest = round(new_total_invest, 2)
    new_total_invest = float(new_total_invest)

    binary = binaryAmount(uid, usd_amount)
    FnRefferalProgram(uid, usd_amount)
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount': float(convert_usd_sva),
        'type' : 'send',
        'wallet': 'SVA',
        'date_added' : datetime.utcnow(),
        'detail': 'Paid for lent %s SVA ($ %s)' %(convert_usd_sva, usd_amount),
        'rate': '1 SVA = %s USD' %(sva_usd),
        'txtid' : '' ,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    if usd_amount >= 100 and usd_amount < 1000:
        day = 180
    if usd_amount >= 1000 and usd_amount < 5000:
        day = 180
    if usd_amount >= 5000 and usd_amount < 10000:
        day = 150
    if usd_amount >= 10000 and usd_amount < 50000:
        day = 120
    if usd_amount >= 50000 and usd_amount < 100000:
        day = 90
    data_deposit = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount_usd' : float(usd_amount),
        'amount_sva': float(convert_usd_sva),
        'status' : 1,
        'date_added' : datetime.utcnow(),
        'num_frofit' : 0,
        'types' : 0,
        'percent' :  0,
        'total_day': day,
        'total_day_earn': 0,
        'amount_daily' : 0,
        'num_profit' : 0,
        'lock_profit': 0
    }
    db.deposits.insert(data_deposit)
    return 1

@deposit_ctrl.route('/autolendingstep1', methods=['GET', 'POST'])
def autolending():
    return json.dumps({'status':'off'})
    listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    # listUser = db.users.find({ 'username':'haidat99' } )
    # i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)
        balance = round(float(x['sva_balance']), 8)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
        # amount = float(x['sva_balance'])*0.9
        # amount_invest = amount* 4
        # amount_invest= round(amount_invest, 0)
        # if float(amount_invest) >= 100 and x['username'] != 'svaindia':
        #     uid= x['customer_id']
        #     user_id = x['_id']
        #     username = x['username']
        #     sva_usd = 4
        #     i = i + 1
        #     max_out = 0
        #     level = 0
        #     day = 0
        #     if amount_invest >= 100 and amount_invest < 1000:
        #         max_out = 1000
        #         level =2
        #         day = 180
        #     if amount_invest >= 1000 and amount_invest < 5000:
        #         max_out = 5000
        #         level =3
        #         day = 180
        #     if amount_invest >= 5000 and amount_invest < 10000:
        #         max_out = 10000
        #         level =4
        #         day = 150
        #     if amount_invest >= 10000 and amount_invest < 50000:
        #         max_out = 20000
        #         level =5
        #         day = 120
        #     if amount_invest >= 50000 and amount_invest < 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if amount_invest > 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if max_out > 0:
        #         balance = round(float(x['sva_balance']), 8)
        #         new_sva_balance = float(balance) - amount
                # time.sleep(1)
                # print(i, x['username'], balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out, level)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                # For mat sva_balance 8
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
                
            

    return json.dumps({'paymentSVA':'success'})

@deposit_ctrl.route('/autolendingstep2', methods=['GET', 'POST'])
def autolendingautolending():
    return json.dumps({'status':'off'})
    # listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    listUser = db.users.find({ 'username':'giadam1' } )
    i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)

        amount = 3125
        amount_invest = 5000
        amount_invest= round(amount_invest, 0)
        if float(amount_invest) >= 100 and x['username'] != 'svaindia':
            uid= x['customer_id']
            user_id = x['_id']
            username = x['username']
            sva_usd = 1.6
            i = i + 1
            max_out = 0
            level = 0
            day = 0
            total_invest = float(x['total_invest'])
            new_total_invest = total_invest + amount_invest
            new_total_invest = round(new_total_invest,2)
            max_out = float(new_total_invest)*3
            if max_out > 0:
                balance = round(float(x['sva_balance']), 8)
                new_sva_balance = float(balance) - float(amount)
                # time.sleep(1)
                print(i, x['username'], new_sva_balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                
                # 2
                binaryAmount(uid, amount_invest)
                btc_usd = 7038
                FnRefferalProgram(uid, amount_invest, btc_usd)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {"level":2, "sva_balance": round(float(new_sva_balance), 8), "total_invest": round(new_total_invest), "max_out": round(max_out,2) } })
                data_deposit = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount_usd' : float(amount_invest),
                    'amount_sva': float(amount),
                    'status' : 1,
                    'date_added' : datetime.utcnow(),
                    'num_frofit' : 0,
                    'types' : 0,
                    'percent' :  0,
                    'total_day': day,
                    'total_day_earn': 0,
                    'amount_daily' : 0,
                    'num_profit' : 0,
                    'lock_profit': 0,
                    'type_invest': 0
                }
                db.deposits.insert(data_deposit)
                data_history = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount': float(amount),
                    'type' : 'send',
                    'wallet': 'SVA',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Paid for invest %s SVA' %(amount),
                    'rate': '1 SVA = %s USD' %(sva_usd),
                    'txtid' : '' ,
                    'amount_sub' : 0,
                    'amount_add' : 0,
                    'amount_rest' : 0
                }
                db.historys.insert(data_history)


                # time.sleep(3)

    return json.dumps({'paymentSVA':'success'})