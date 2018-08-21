from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
from bson.objectid import ObjectId
import json
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from bson import json_util
__author__ = 'carlozamagni'

dashboard_ctrl = Blueprint('dashboard', __name__, static_folder='static', template_folder='templates')
def finduser_by_id(ids):
	user = db.User.find_one({'_id': ObjectId(ids)})
	return user
# @dashboard_ctrl.route('/update_password', methods=['GET', 'POST'])
# def dashboarupdate_password():
# 	List = db.users.find().skip(0).limit(220)
# 	for x in List:
# 		db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { 'password': 'password'} })
# 	return json.dumps({'afa':'asd'})

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

@dashboard_ctrl.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	if session.get(u'logged_in') is None:
		return redirect('/invest/login')
	else:
		uid = session.get('uid')
		user = db.User.find_one({'customer_id': uid})
		username = user['username']
		refferal_link = 'https://smartfva.co/invest/register/%s' % (username)
		received = float(user.m_wallet/1000000)
		roi = float(user.roi)
		profit_daily_pending = db.profits.find_one({'status': 0})
		# profit_daily = db.profits.find({'status': 1}).limit(5)
		profit_daily = db.profits.find({'status':1}).sort([("date_added", -1)]).limit(5)

		total_refferal = db.users.find({'p_node': uid, 'type': 1}).count()
		print uid
		refferal = db.users.find({'p_node': uid, 'type': 1})

		if roi > 0:
			percent = received/roi
		else:
			percent = 0		

		max_out = float(user.max_out)
		total_max_out = int(user.total_max_out)
		if max_out > 0:
			percent_max = total_max_out/max_out
		else:
			percent_max = 0
		data_ticker = db.tickers.find_one({})
		data ={
			'refferal_link' : refferal_link,
		    'user': user,
		    'menu' : 'dashboard',
		    'float' : float,
		    'percent' : round(percent*100, 2),
		    'percent_max' : round(percent_max*100, 2),
		    'total_refferal': total_refferal,
		    'refferal': refferal,
		    'profit_daily': profit_daily,
		    'profit_daily_pending': profit_daily_pending,
		    'btc_usd':data_ticker['btc_usd'],
	        'sva_btc':data_ticker['sva_btc'],
	        'sva_usd':data_ticker['sva_usd'],
	        'ltc_usd':data_ticker['ltc_usd'],
	        'sva_ltc':data_ticker['sva_ltc']
		}
		
		return render_template('account/dashboard.html', data=data)

@dashboard_ctrl.route('/getNewRefferal', methods=['GET', 'POST'])
def getNewRefferal():
	if session.get(u'logged_in') is None:
		return redirect('/invest/login')
	else:
		user_id = session.get('user_id')
		uid = session.get('uid')
		total_refferal = db.users.find({'p_node': uid, 'type': 1}).count()
		print total_refferal
		datarefferal = db.users.find({'p_node': uid, 'type': 1})
		if total_refferal > 0:
			html = ""
			for x in datarefferal:
				html = html + """<tr>
	                <td>"""+x['name']+"""</td>
	                <td>"""+x['username']+"""</td>
	                <td>
	                   <input type="radio" name="choose" value='"""+x['customer_id']+"""'>
	                </td>
	             </tr>"""
			return json.dumps({
				'status': 'success', 
				'refferal': html
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': 'No data'
			})

@dashboard_ctrl.route('/confrimAddTree', methods=['GET', 'POST'])
def confrimAddTree():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please login'
		})
	else:
		if request.method=='POST':
			positon = request.form['positon']
			p_binary = request.form['p_binary']
			if float(positon) == 1:
				p = 'left'
			else:
				p = 'right'
			customer_id = request.form['uid']
			customer = db.User.find_one({'customer_id': p_binary})

			refferal = db.User.find_one({'customer_id': customer_id})

			if customer is None or refferal is None:
				return json.dumps({
					'status': 'error', 
					'message': 'Position dose not exits'
				})
			else:
				if customer[p] == '' and refferal['p_binary'] == '':
					db.users.update({ "customer_id" : p_binary }, { '$set': { p: customer_id} })
					db.users.update({ "customer_id" : customer_id }, { '$set': { 'p_binary': p_binary, 'type': 0} })
					return json.dumps({
						'status': 'success', 
						'message': 'Success!'
					})
				else:
					return json.dumps({
						'status': 'error', 
						'message': 'Position exits'
					})
		else:
			return json.dumps({
				'status': 'error', 
				'message': 'Please login'
			})


		

def children_tree (json):
    customer = db.User.find_one({'customer_id': json['id']})
    user_p_left = db.User.find_one({"$and" :[{'p_binary': json['id']}, {'customer_id': customer.left}] })
    if user_p_left is not None:
        tree = {
            "id":user_p_left.customer_id
        }
        json.append(tree)
        children_tree(tree)
    user_p_right = db.User.find_one({"$and" :[{'p_binary': json['id']}, {'customer_id': customer.right}] })
    if user_p_right is not None:
        tree = {
            "id":user_p_right.customer_id
        }
        json.append(tree)
        children_tree(tree)
    return json 

def reduceTree (user):
	json = []
	tree = {
		"id":user.customer_id
	}
	json.append(tree)
	children_tree(tree)

def renderJson(uid) :
    user = db.User.find_one({'customer_id': uid})
    return reduceTree(user)


def LoopPNode(customer_id_list):
    List = db.User.find({"p_binary":{"$in":customer_id_list}})
    customer_id = []
    for x in List:
        customer_id.append(str(x['_id']))
    print customer_id
    if len(customer_id) > 0:
    	return LoopPNode(customer_id)

@dashboard_ctrl.route('/add-tree/<username>', methods=['GET', 'POST'])
def getdataTree(username):
	if session.get(u'logged_in') is None:
		return redirect('/invest/login')
	else:
		user_id = session.get('user_id')
		uid = session.get('uid')
		user = db.users.find_one({'username': username})
		if user is None:
			return redirect('/invest/login')
		customer_id = []
		customer_id.append(str(uid))
		page_sanitized = json_util.dumps(LoopPNode(customer_id))
		print page_sanitized
		return json.dumps({
			'status': 'error', 
			'message': 'Please enter amount exchange!' 
		})

@dashboard_ctrl.route('/transferusd', methods=['GET', 'POST'])
def transferUSD():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount exchange!' 
				})
			amount = float(request.form['amount'])
			amount = round(amount, 2)
			amount_s = round(amount, 2)
			if float(amount) < 15:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 15 USD' 
				})
			amount = float(amount) - (0.0005*float(amount))
			amount = round(amount, 2)
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})
			usd_balance = user['usd_balance']
			sva_balance = user['sva_balance']
			data_ticker = db.tickers.find_one({})
			sva_usd = data_ticker['sva_usd']
			new_usd_sva = float(amount)/float(sva_usd)
			new_usd_sva = round(new_usd_sva, 8)
			if float(usd_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_usd_balance = float(usd_balance) - float(amount_s)
			new_usd_balance = round(new_usd_balance, 2)
			new_sva_balance = float(sva_balance) + float(new_usd_sva)
			new_sva_balance = round(new_sva_balance, 8)
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "usd_balance": new_usd_balance, "sva_balance": new_sva_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_s),
				'type' : 'send',
				'wallet': 'USD',
				'date_added' : datetime.utcnow(),
				'detail': 'Transfer %s USD from USD Wallet to SVA Wallet' %(amount_s),
				'rate': '1 SVA = %s USD' %(sva_usd),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_s),
				'type' : 'receive',
				'wallet': 'SVA',
				'date_added' : datetime.utcnow(),
				'detail': 'Receive %s SVA from USD Wallet (%s USD)' %(new_usd_sva, amount_s),
				'rate': '1 SVA = %s USD' %(sva_usd),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_usd_balance': new_usd_balance,
				'new_sva_balance': new_sva_balance,
				'message': 'Transfer to SVA Wallet success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})

@dashboard_ctrl.route('/transferusdcms', methods=['GET', 'POST'])
def transferUSDCMS():
	return json.dumps({ 'status': 'error', 'message': 'Error' })
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount exchange!' 
				})
			amount = float(request.form['amount'])
			amount = round(amount, 2)
			amount_s = round(amount, 2)
			if float(amount) < 15:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 15 USD' 
				})
			amount = round(amount, 2)
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})
			usd_balance = user['sva_usd_cms']
			sva_balance = user['sva_balance']
			btc_balance = user['btc_balance']
			data_ticker = db.tickers.find_one({})
			sva_usd = data_ticker['sva_usd']
			btc_usd =  data_ticker['btc_usd']

			amount_usd_transfer = amount*0.2
			amount_btc_transfer = amount*0.8

			new_usd_sva = float(amount_usd_transfer)/float(sva_usd)
			new_usd_sva = round(new_usd_sva, 8)

			transfer_btc = float(amount_btc_transfer)/float(btc_usd)
			transfer_btc = round(transfer_btc,8)

			if float(usd_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_usd_balance = float(usd_balance) - float(amount_s)
			new_usd_balance = round(new_usd_balance, 2)
			new_sva_balance = float(sva_balance) + float(new_usd_sva)
			new_sva_balance = round(new_sva_balance, 8)
			new_btc_balance = float(btc_balance) + float(transfer_btc)
			new_btc_balance = round(new_btc_balance, 8)

			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "sva_usd_cms": new_usd_balance, "sva_balance": new_sva_balance, "btc_balance": new_btc_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_s),
				'type' : 'send',
				'wallet': 'USD CMS',
				'date_added' : datetime.utcnow(),
				'detail': 'Transfer %s USD from USD Commission Wallet to SVA Wallet' %(amount_s),
				'rate': '1 SVA = %s USD' %(sva_usd),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(new_usd_sva),
				'type' : 'receive',
				'wallet': 'SVA',
				'date_added' : datetime.utcnow(),
				'detail': 'Receive %s SVA from USD Commission Wallet (%s USD)' %(new_usd_sva, amount_usd_transfer),
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
				'amount': float(transfer_btc),
				'type' : 'receive',
				'wallet': 'BTC',
				'date_added' : datetime.utcnow(),
				'detail': 'Receive %s BTC from USD Commission Wallet (%s USD)' %(transfer_btc, amount_btc_transfer),
				'rate': '1 BTC = %s USD' %(btc_usd),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_historys)
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_usd_balance': new_usd_balance,
				'new_sva_balance': new_sva_balance,
				'message': 'Transfer to SVA Wallet success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})

@dashboard_ctrl.route('/transferusdsva', methods=['GET', 'POST'])
def transferSVAtoUSDSVA():
	# return json.dumps({ 'status': 'error', 'message': 'Error' })
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount convert!' 
				})
			amount = float(request.form['amount'])
			amount = round(amount, 2)
			if float(amount) < 5:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 5 SVA' 
				})
			amount = round(amount, 2)
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})
			usd_balance = user['sva_usdsva']
			sva_balance = user['sva_balance']

			data_ticker = db.tickers.find_one({})
			sva_usd = data_ticker['sva_usd']
			amount_usdsva = float(amount)*float(sva_usd)
			amount_usdsva= round(amount_usdsva,2)
			if float(sva_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_usd_balance = float(usd_balance) + float(amount_usdsva)
			new_usd_balance = round(new_usd_balance, 2)
			new_sva_balance = float(sva_balance) - float(amount)
			new_sva_balance = round(new_sva_balance, 8)

			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "sva_usdsva": new_usd_balance, "sva_balance": new_sva_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_usdsva),
				'type' : 'receive',
				'wallet': 'USDSVA',
				'date_added' : datetime.utcnow(),
				'detail': 'Receive %s from SVA Wallet (%s SVA)' %(amount_usdsva, amount),
				'rate': '1 SVA = %s USD' %(sva_usd),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_usd_balance': new_usd_balance,
				'new_sva_balance': new_sva_balance,
				'message': 'Transfer to USDSVA Wallet success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})