from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
import json
from rex.models import user_model, deposit_model, history_model, invoice_model
from bson import ObjectId, json_util
import pprint

import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import requests
import string
import random
__author__ = 'carlozamagni'

personal_ctrl = Blueprint('personal', __name__, static_folder='static', template_folder='templates')

def reduceTree (uid):
    json = []
    array = []
    user = db.User.find_one({'_id': ObjectId(uid)}, {'displayName': 1, 'total_invest':1})
    tree = {
        "id":str(user['_id']),
        "displayName":str(user['displayName']),
        "fl":0,
        "children" : []
    }
    json.append(tree)
    children_tree(tree,array,0)
    
    return array    

def get_level_user_id(user_id):
    level = 'IB'
    percent = 0
    data = {}
    user = db.User.find_one({'_id': ObjectId(user_id)})
    
    if (int(user['level']) == 1):
        level = 'Active IB'
        percent = 0.05
    if (int(user['level']) == 2):
        level = 'Star IB'
        percent = 0.2
    if (int(user['level']) == 3):
        level = 'Super IB'
        percent = 0.4
    if (int(user['level']) == 4):
        level = 'Pro IB'
        percent = 0.6
    if (int(user['level']) == 5):
        level = 'Master IB'
        percent = 0.8

    if (int(user['level']) == 6):
        level = 'Diamond Master IB'
        percent = 0.9
        # count_f1 = db.User.find({'$and' : [{ 'betting': { '$gte': 100 } },{'p_node': user_id}]}).count()
        # if (count_f1 >=5 and float(user['betting']) >= 200):
        #     level = 'Star IB'
        #     percent = 0.2

        #     count_f1 = db.User.find({'$and' : [{ 'betting': { '$gte': 100 } },{'p_node': user_id}]}).count()
        #     if (count_f1 >= 10 and float(user['betting']) >= 400):
        #         level = 'Super IB'
        #         percent = 0.4

        #         count_f1 = db.User.find({'$and' : [{ 'betting': { '$gte': 100 } },{'p_node': user_id}]}).count()
        #         if (count_f1 >= 15 and float(user['betting']) >= 600):
        #             level = 'Pro IB'
        #             percent = 0.6

        #             count_f1 = db.User.find({'$and' : [{ 'betting': { '$gte': 100 } },{'p_node': user_id}]}).count()
        #             if (count_f1 >= 20 and float(user['betting']) >= 800):
        #                 level = 'Master IB'
        #                 percent = 0.8

        #                 count_f1 = db.User.find({'$and' : [{ 'betting': { '$gte': 100 } },{'p_node': user_id}]}).count()
        #                 if (count_f1 >= 20 and float(user['betting']) >= 1000):
        #                     level = 'Diamond Master IB'
        #                     percent = 0.9
    data['level'] = level
    data['percent'] = percent
    return data    

def children_tree (json,array,floor):
    customer = db.User.find({'p_node': json['id']}) 
    floor = floor + 1
    for x in customer:
        tree = {
            "id":str(x['_id']),
            "displayName":str(x['displayName']),
            "fl":"F"+str(floor),
            "children" : []
        }
        count_f1 = db.User.find({'p_node': str(x['_id'])}).count()
        sponsor = db.User.find_one({'_id': ObjectId(x['p_node'])})
        sponsor_name = ''
        if sponsor:
            sponsor_name = sponsor['email']
        percent =  0
        if int(x['level']) == 1:
            percent = 0.05
        if int(x['level']) == 2:
            percent = 0.2
        if int(x['level']) == 3:
            percent = 0.4
        if int(x['level']) == 4:
            percent = 0.6
        if int(x['level']) == 5:
            percent = 0.8
        if int(x['level']) == 6:
            percent = 0.9
        

        children = {
            "id":str(x['_id']),
            "signupDate":str(x['signupDate']),
            "email":str(x['email']),
            "level" : str(percent),
            "count_f1" : str(count_f1),
            "floor":"F"+str(floor),
            "sponsor" :  str(sponsor_name),
            "balance":str(x['balance']),
            "balance_commision":str(x['balance_commision']),
            "betting" : str(x['betting'])
        }
        array.append(children)
        json['children'].append(tree)
        
        children_tree (tree,array,floor)
    
def reduceTree_dashboard (uid):
    json = []
    array = []
    user = db.User.find_one({'_id': ObjectId(uid)}, {'displayName': 1, 'total_invest':1})
    tree = {
        "id":str(user['_id']),
        "displayName":str(user['displayName']),
        "fl":0,
        "children" : []
    }
    json.append(tree)
    Active_IB = 0
    Star_IB = 0
    Master_IB = 0
    return (children_tree_dashboard(tree,0,Active_IB,Star_IB,Master_IB))


def children_tree_dashboard (json,floor,Active_IB,Star_IB,Master_IB):
    customer = db.User.find({'p_node': json['id']}) 
    floor = floor + 1
    for x in customer:
        tree = {
            "id":str(x['_id']),
            "children" : []
        }
        
        if (get_level_user_id(x['_id'])['level'] == 'Active IB'):
            Active_IB = Active_IB + 1
        if (get_level_user_id(x['_id'])['level'] == 'Star IB'):
            Star_IB +=1
        if (get_level_user_id(x['_id'])['level'] == 'Master IB'):
            Master_IB +=1
        
        children = {
            "id":str(x['_id'])
        }

        json['children'].append(tree)
        children_tree_dashboard (tree,floor,Active_IB,Star_IB,Master_IB)
    data = {}
    data['Active_IB'] = Active_IB
    data['Star_IB'] = Star_IB
    data['Master_IB'] = Master_IB
    return data
#http://0.0.0.0:58056/personal/json_tree?id_user=5a4da0c69220f213157a9bc5
def renderJson(uid):
    user = db.User.find_one({'_id': ObjectId(uid)}, {'displayName': 1, 'total_invest':1})
    return reduceTree(user)
@personal_ctrl.route('/json_tree', methods=['GET', 'POST'])
def json_tree():
    uid =  request.args.get('id_user')
    page_sanitized = json_util.dumps(reduceTree(uid))
    return page_sanitized  
# get level print(get_level_user_id(uid))
# get active,start, master ID json_util.dumps(reduceTree_dashboard(uid))
@personal_ctrl.route('/get_dashboard', methods=['GET', 'POST'])
def get_dashboard_level():
    uid =  request.args.get('id_user')
    #get_ib = json_util.dumps(reduceTree_dashboard(uid))
    level = json_util.dumps(get_level_user_id(uid))
    return level
    
@personal_ctrl.route('/get_dashboard_id', methods=['GET', 'POST'])
def get_dashboard_id():
    uid =  request.args.get('id_user')
    #get_ib = json_util.dumps(reduceTree_dashboard(uid))
    level = json_util.dumps(reduceTree_dashboard(uid))
    return level


def reduceTree_tree (user):
    
    json = []
    tree = {
        "id":str(user['_id']),
        "text":str(user['displayName']),
        "empty":False,
        "iconCls":"level2",
        "fl":1,
        'children' : []
    }

    json.append(tree)
    children_tree_tree(tree)
    return json
def children_tree_tree (json):
    customer = db.User.find({'p_node': json['id']}, {'displayName':1})
    if customer:
        for x in customer:
            checkF1 = db.User.find({'p_node': str(x['_id'])}).count()
            
            if int(checkF1) > 0:
                dataChild = True
            else:
                dataChild = ''
            tree = {
                "id":str(x['_id']),
                "text":str(x['displayName']),
            
                "empty":False,
                "iconCls":"level2",
                "fl":1,
                'children' : dataChild
            }
            json['children'].append(tree)
            # children_tree(tree)
    else:
        json['children']=0
    return json
def renderJson_tree(uid):
    user = db.User.find_one({'_id': ObjectId(uid)}, {'displayName': 1})
   
    return reduceTree_tree(user)

@personal_ctrl.route('/tree/<uid>', methods=['GET', 'POST'])
def json_tree_tree(uid):
    id_request =  request.args.get('id')
    if id_request == '#':
        uid = str(uid)
    else:
        uid = str(id_request)
   
    page_sanitized = json_util.dumps(renderJson_tree(uid))
    return page_sanitized  






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


@personal_ctrl.route('/api/team-volume-commission', methods=['GET', 'POST'])
def TeamVolumeCommission():
    # return json.dumps({'status' : 'off'})
    listcustomer = db.users.find({"level": { "$gt": 0 }})
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
        find_f1 = db.users.find({'p_node': str(x['_id'])})
        # sva_usd_cms = float(x['sva_usd_cms'])
        print x['_id']
        customer = db.users.find_one({'_id': ObjectId(x['_id'])})
        if customer.has_key("balance_commision"):
            print customer['email']
        else:
            db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {'balance_commision': 0} })
        print customer['email']
        balance_commision = customer['balance_commision']
        balance = customer['balance']
        new_balance_commision = 0
        new_balance = 0
        amount_cms = 0

        for y in find_f1:
            customer2 = db.users.find_one({'_id': ObjectId(y['_id'])})
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
                new_balance_commision = new_balance_commision + amount_daily
                new_balance = new_balance + amount_daily
                print('co,mmission',amount_daily)
                data_history_one = {
                'user_id': str(customer['_id']),
                'username' : customer['displayName'],
                'amount': str(amount_daily),
                'type' : 'Team Commission',
                'date_added' : datetime.utcnow(),
                'detail': 'Get '+str(percent)+' '+"""%"""+' commission from Team of '+str(customer2['displayName'])+' trading $' +str(y['team_volume']) 
                }
                db.historycommissions.insert(data_history_one)
        if float(new_balance_commision) > 0:
            print new_balance_commision
            print x['_id']
            new_balance_commision = float(new_balance_commision) + float(balance_commision)
            new_balance_commision = round(new_balance_commision,2)
            new_balance = float(new_balance) + float(balance)
            new_balance = round(new_balance, 2)
            # new_sva_usd_cms = float(new_sva_usd_cms)
            # new_sva_usd_cms = round(new_sva_usd_cms,2)
            
            db.users.update({ "_id" :ObjectId(x['_id']) }, { '$set': {"balance": float(new_balance), "balance_commision": float(new_balance_commision)} })
    return json.dumps({'status' : 'update team_volume success'})
def ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            if float(x['betting']) >= 100:
                level = 1
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True
def start_ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            check_start_ib = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':0}}] })
            if float(x['betting']) >= 200 and check_start_ib.count() >= 5:
                level = 2
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True

def supper_ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            check_start_ib = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':0}}] })
            if float(x['betting']) >= 400 and check_start_ib.count() >= 10:
                level = 3
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True
def pro_ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            check_start_ib = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':0}}] })
            if float(x['betting']) >= 600 and check_start_ib.count() >= 15:
                level = 4
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True
def master_ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            check_start_ib = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':0}}] })
            if float(x['betting']) >= 800 and check_start_ib.count() >= 20:
                level = 5
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True

def diamond_master_ib():
    getTrading = db.users.find({})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = x['level']
            check_startIB = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':1}}] })
            check_master_ib = db.users.find({"$and" :[{'p_node': str(x['_id'])}, {'level':{'$gt':4}}] })
            if float(x['betting']) >= 1000 and check_startIB.count() >= 10 and check_master_ib.count() >= 10:
                level = 6
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
        return True
    else:
        return True

@personal_ctrl.route('/api/referral', methods=['GET', 'POST'])
def depositApiRefferal():
    print 'IB'
    ib()
    print 'Start IB'
    start_ib()
    print 'Supper IB'
    supper_ib()
    print 'Pro IB'
    pro_ib()
    print 'Master IB'
    master_ib()
    print 'Diamond Master IB'
    diamond_master_ib()

    db.users.update({'email' : {'$in' : ['queen.ht2015@gmail.com','globalteamsg@gmail.com','adafxteamsg@gmail.com','adafxteamvn@gmail.com','duongthanh410@gmail.com','tradeadaforex@gmail.com','adafxpro.co@gmail.com','tinhngo543321@gmail.com',]}},{'$set' : {'level' : 6}}, multi=True)
    return json.dumps({'success' : 0})
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    # getTrading = db.tradings.find({})
    # if getTrading.count()  > 0:
    #     for x in getTrading:
    #         amount_direct = 0
    #         level = 0
    #         if float(x['amount']) >= 100:
    #             level = 1
    #         check_start_ib = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 1}] })
    #         check_startIB = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 2}] })
    #         check_master_ib = db.tradings.find({"$and" :[{'p_node': str(x['user_id'])}, {'level': 5}] })
    #         if float(x['amount']) >= 200 and check_start_ib.count() >= 3:
    #             level = 2
    #         if float(x['amount']) >= 400 and check_start_ib.count() >= 10:
    #             level = 3
    #         if float(x['amount']) >= 600 and check_start_ib.count() >= 15:
    #             level = 4
    #         if float(x['amount']) >= 800 and check_start_ib.count() >= 20:
    #             level = 5
    #         if float(x['amount']) >= 1000 and check_startIB.count() >= 10 and check_master_ib.count() >= 10:
    #             level = 6
    #         db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'level': level} })
    #     return json.dumps({'success' : 1})
    # else:
    #     return json.dumps({'success' : 0})

@personal_ctrl.route('/api/global_commission', methods=['GET', 'POST'])
def GlobalCommission():
    getTrading = db.users.find({'betting':{'$ne':0}})
    if getTrading.count()  > 0:
        total_betting = 0
        for x in getTrading:
            amount_direct = 0
            betting = float(x['betting'])
            if betting > 0:
                total_betting = float(total_betting) + betting
        total_betting = round(total_betting, 2)
        if float(total_betting) > 0:
            percent = 0.05
            get_master_ib = db.users.find({'level':5})
            if get_master_ib.count() > 0:
                for master in get_master_ib:
                    check_startIB = db.users.find({"$and" :[{'p_node': str(master['_id'])}, {'level': 2}] })
                    # Code here

                    # End code
                
            get_diamond_master_ib = db.users.find({'level':6})
            if get_diamond_master_ib.count() > 0:
                for dmaster in get_diamond_master_ib:
                    check_master_ib = db.users.find({"$and" :[{'p_node': str(master['_id'])}, {'level': 5}] })
                    if check_master_ib.count() >= 10:
                        commission = float(percent)* float(total_betting)
                        commission = float(commission)/100
                        balance_commision = dmaster['balance_commision']
                        new_balance_commision = float(balance_commision)+ float(commission)
                        new_balance_commision = round(new_balance_commision,2)
                        balance = float(dmaster['balance']) + float(commission)
                        new_balance = round(balance, 2)
                        db.users.update(
                            { "_id" : ObjectId(dmaster['_id']) }, 
                                { 
                                '$set': {
                                'balance': float(new_balance)
                                }
                            }
                        )
                        data_history_one = {
                            'user_id': str(dmaster['_id']),
                            'username' : dmaster['displayName'],
                            'amount': round(float(commission), 2),
                            'type' : 'Global Commission',
                            'date_added' : datetime.utcnow(),
                            'detail': 'Get '+str(percent)+' '+"""%"""+' Global Commission team volume $ '+str(betting)
                        }

    return json.dumps({'success' : 0})
@personal_ctrl.route('/api/caculate-referral', methods=['GET', 'POST'])
def CaculateRefferal():
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    getTrading = db.users.find({'level':{'$ne':0}})
    if getTrading.count()  > 0:
        for x in getTrading:
            amount_direct = 0
            level = float(x['level'])
            percent = 0
            
            get_refferal = db.users.find({'p_node':str(x['_id']), 'betting': {'$ne': 0}})
            if get_refferal.count() > 0:
                total_f1 = 0
                for y in get_refferal:
                    amount_f1 = float(y['betting'])
                    total_f1 = float(total_f1) + float(amount_f1)
                if float(total_f1) >= 100 and float(level) == 1:
                    percent = 0.05
                if float(total_f1) >= 100 and float(level) == 2:
                    percent = 0.2
                if float(total_f1) >= 100 and float(level) == 3:
                    percent = 0.4
                if float(total_f1) >= 100 and float(level) == 4:
                    percent = 0.6
                if float(total_f1) >= 100 and float(level) == 5:
                    percent = 0.8
                if float(total_f1) >= 100 and float(level) == 6:
                    percent = 0.9
                if float(percent) > 0:
                    commission = float(percent)* float(total_f1)
                    commission = float(commission)/100
                    # db.users.update( { "_id" : ObjectId(x['_id']) }, { '$set': { 'total_f1': round(total_f1,2) } } )
                    customer = db.users.find_one({'_id': ObjectId(x['_id'])})
                    if customer is not None and customer.has_key("balance_commision"):
                        balance_commision = customer['balance_commision']
                    else:
                        balance_commision = 0
                    new_balance_commision = float(balance_commision)+ float(commission)
                    new_balance_commision = round(new_balance_commision,2)
                    balance = float(customer['balance']) + float(commission)
                    new_balance = round(balance, 2)
                    db.users.update(
                        { "_id" : ObjectId(x['_id']) }, 
                        { 
                            '$set': {
                            'balance': float(new_balance),
                            'total_f1': round(total_f1,2)
                            }
                        }
                    )
                    data_history_one = {
                    'user_id': str(customer['_id']),
                    'username' : customer['displayName'],
                    'amount': round(float(commission), 2),
                    'type' : 'Refferall Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+str(percent)+' '+"""%"""+' commission directly from total F1 trading $ '+str(total_f1)
                    }
                    db.historycommissions.insert(data_history_one)


        return json.dumps({'success' : 1})
    else:
        return json.dumps({'success' : 0})


@personal_ctrl.route('/api/caculate-teamvolume', methods=['GET', 'POST'])
def CaculateTeamvolume():
    # db.tradings.update({}, {'$set':{'level': 0}},{'multi':True})
    getTrading = db.users.find({'check_team_volume': 0})
    if getTrading.count()  > 0:
        for x in getTrading:
            if float(x['betting']) > 0 and x['p_node'] != '0' and x['p_node'] != '':
                binaryAmount(str(x['_id']), x['betting'])
            db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'check_team_volume': 1} })
        return json.dumps({'success' : 1})
    else:
        return json.dumps({'success' : 0})

@personal_ctrl.route('/api/update-check_volume', methods=['GET', 'POST'])
def UpdateCheckVolume():
    db.users.update({}, {'$set':{'check_team_volume': 0, 'team_volume': 0, 'team_volume_supper': 0, 'team_volume_pro': 0, 'team_volume_master': 0, 'team_volume_diamond': 0, 'total_team_volume': 0, 'check_referral': 0, 'level':0,'total_f1':0}},multi=True)
    return json.dumps({'success' : 0})

@personal_ctrl.route('/api/reset_amount', methods=['GET', 'POST'])
def UpdateSetAmount():
    db.users.update({}, {'$set':{'betting': 0, 'total_f1': 0,'balance_commision' : 0 }},multi=True)
    return json.dumps({'success' : 0})


def binaryAmount(user_id, amount_invest):
    customer_ml = db.users.find_one({"_id" : ObjectId(user_id) })
    amount = customer_ml['betting']
    new_amount = float(amount) + float(amount_invest)
    new_amount = round(new_amount, 2)
    # db.tradings.update({ "_id" : ObjectId(customer_ml['_id']) }, { '$set': {'amount': new_amount} })
    # print customer_ml['p_node']
    if customer_ml['p_node'] != '' or customer_ml['p_node'] != '0':
        i = 0
        while (True):
            print customer_ml['p_node']
            # print customer_ml['displayName']
            customer_ml_p_node = db.users.find_one({"_id" : ObjectId(customer_ml['p_node']) })
            #print(customer_ml_p_node['p_node'],customer_ml_p_node['email'])
            if customer_ml_p_node is None:
                break
            else:
                i = i + 1
                # print customer_ml_p_node['p_node']
                # print customer_ml_p_node['email']
                # print amount_invest
                new_team_volume_supper = float(customer_ml_p_node['team_volume_supper']) + float(amount_invest)
                new_team_volume_supper = round(new_team_volume_supper, 2)

                new_team_volume_pro = float(customer_ml_p_node['team_volume_pro']) + float(amount_invest)
                new_team_volume_pro = round(new_team_volume_pro, 2)

                new_team_volume_master = float(customer_ml_p_node['team_volume_master']) + float(amount_invest)
                new_team_volume_master = round(new_team_volume_master, 2)

                new_team_volume_diamond = float(customer_ml_p_node['team_volume_diamond']) + float(amount_invest)
                new_team_volume_diamond = round(new_team_volume_diamond, 2)

                if float(i) <= 5:
                    db.users.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume_diamond': new_team_volume_diamond, 'team_volume_master': new_team_volume_master, 'team_volume_pro': new_team_volume_pro, 'team_volume_supper': new_team_volume_supper} })
                elif float(i) > 5 and float(i) <= 10:
                    db.users.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume_diamond': new_team_volume_diamond, 'team_volume_master': new_team_volume_master, 'team_volume_pro': new_team_volume_pro} })
                elif float(i) > 10 and float(i) <= 15:
                    db.users.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume_diamond': new_team_volume_diamond, 'team_volume_master': new_team_volume_master} })
                elif float(i) > 16 and float(i) <= 20:
                    db.users.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume_diamond': new_team_volume_diamond } })
                else:
                    print i
                team_volume = customer_ml_p_node['team_volume']
                new_team_volume = float(team_volume) + float(amount_invest)
                new_team_volume = round(new_team_volume, 2)
                # i = i + 1
                # if i >= 2:
                db.users.update({ "_id" : ObjectId(customer_ml_p_node['_id']) }, { '$set': {'team_volume': new_team_volume} })
                checkNode = db.users.find({"_id" : ObjectId(customer_ml_p_node['_id']) })
                print checkNode.count()
                # print customer_ml_p_node['p_node']
                if checkNode.count() == 0 or customer_ml_p_node['p_node'] == '' or customer_ml_p_node['p_node'] == '0':
                    break
            customer_ml = db.users.find_one({"_id" : ObjectId(customer_ml_p_node['_id']) })
            print customer_ml['email']
            print '================'
            if customer_ml is None:
                break
    return True
def commission_supper_ib():
    getTrading = db.users.find({'level': 3})
    if getTrading.count()  > 0:
        for x in getTrading:
            percent = 0.05
            if float(x['team_volume_supper']) > 0:
                commission = float(x['team_volume_supper'])*0.05
                commission = float(commission)/100
                balance = float(commission) + float(x['balance'])
                balance = round(balance, 2)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'balance': balance} })
                data_history_one = {
                    'user_id': str(x['_id']),
                    'username' : x['displayName'],
                    'amount': round(float(commission), 2),
                    'type' : 'Floor Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+str(percent)+' '+"""%"""+' commission from team trading $ '+str(x['team_volume_supper'])
                }
                db.historycommissions.insert(data_history_one)
        return True
    else:
        return True
def commission_pro_ib():
    getTrading = db.users.find({'level': 4})
    if getTrading.count()  > 0:
        for x in getTrading:
            percent = 0.05
            if float(x['team_volume_supper']) > 0:
                commission = float(x['team_volume_supper'])*0.05
                commission = float(commission)/100
                balance = float(commission) + float(x['balance'])
                balance = round(balance, 2)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'balance': balance} })
                data_history_one = {
                    'user_id': str(x['_id']),
                    'username' : x['displayName'],
                    'amount': round(float(commission), 2),
                    'type' : 'Floor Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+str(percent)+' '+"""%"""+' commission from team trading $ '+str(x['team_volume_supper'])
                }
                db.historycommissions.insert(data_history_one)
        return True
    else:
        return True
def commission_master_ib():
    getTrading = db.users.find({'level': 5})
    if getTrading.count()  > 0:
        for x in getTrading:
            percent = 0.05
            if float(x['team_volume_supper']) > 0:
                commission = float(x['team_volume_supper'])*0.05
                commission = float(commission)/100
                balance = float(commission) + float(x['balance'])
                balance = round(balance, 2)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'balance': balance} })
                data_history_one = {
                    'user_id': str(x['_id']),
                    'username' : x['displayName'],
                    'amount': round(float(commission), 2),
                    'type' : 'Floor Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+str(percent)+' '+"""%"""+' commission from team trading $ '+str(x['team_volume_supper'])
                }
                db.historycommissions.insert(data_history_one)
        return True
    else:
        return True
def commission_diamond_ib():
    getTrading = db.users.find({'level': 6})
    if getTrading.count()  > 0:
        for x in getTrading:
            percent = 0.05
            if float(x['team_volume_supper']) > 0:
                commission = float(x['team_volume_supper'])*0.05
                commission = float(commission)/100
                balance = float(commission) + float(x['balance'])
                balance = round(balance, 2)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'balance': balance} })
                data_history_one = {
                    'user_id': str(x['_id']),
                    'username' : x['displayName'],
                    'amount': round(float(commission), 2),
                    'type' : 'Floor Commission',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Get '+str(percent)+' '+"""%"""+' commission from team trading $ '+str(x['team_volume_supper'])
                }
                db.historycommissions.insert(data_history_one)
        return True
    else:
        return True
@personal_ctrl.route('/api/caculate-teamvolume-20floor', methods=['GET', 'POST'])
def CaculateTeamvolume20Floor():
    print 'commission_supper_ib'
    commission_supper_ib()
    print 'commission_pro_ib'
    commission_pro_ib()
    print 'commission_master_ib'
    commission_master_ib()
    print 'commission_diamond_ib'
    commission_diamond_ib()
    return json.dumps({'status': '1'})




# 1 /api/update-check_volume

# 2: Cap nhat level
#     /api/referral
# 3: tinh hoa hong truc tiep
#     /api/caculate-referral

# 4: tinh + team volume
#     /api/caculate-teamvolume

# 5: tinh % team volume
#     /api/team-volume-commission

# 6 /api/reset_amount