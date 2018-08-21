from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
from bson.objectid import ObjectId
import json
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
import string
import random
from bson import json_util
__author__ = 'carlozamagni'

appkey_ctrl = Blueprint('appkey', __name__, static_folder='static', template_folder='templates')
def finduser_by_id(ids):
	user = db.User.find_one({'_id': ObjectId(ids)})
	return user
# @appkey_ctrl.route('/update_password', methods=['GET', 'POST'])
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

@appkey_ctrl.route('/key', methods=['GET', 'POST'])
def key():
	if session.get(u'logged_in') is None:
		return redirect('/invest/login')
	else:
		uid = session.get('uid')
		user = db.User.find_one({'customer_id': uid})
		username = user['username']
		refferal_link = 'https://smartfva.co/invest/register/%s' % (username)
		max_out = float(user.max_out)
		total_max_out = int(user.total_max_out)
		if max_out > 0:
			percent_max = total_max_out/max_out
		else:
			percent_max = 0
		data_ticker = db.tickers.find_one({})
		dataKey = db.apps.find({'uid': uid})
		data ={
			'refferal_link' : refferal_link,
		    'user': user,
		    'menu' : 'key',
		    'float' : float,
		    'int': int,
		    'dataKey': dataKey,
		    'btc_usd':data_ticker['btc_usd'],
	        'sva_btc':data_ticker['sva_btc'],
	        'sva_usd':data_ticker['sva_usd'],
	        'ltc_usd':data_ticker['ltc_usd'],
	        'sva_ltc':data_ticker['sva_ltc']
		}
		return render_template('account/key.html', data=data)

def id_generator(size=25, chars=string.ascii_uppercase + string.digits):
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

@appkey_ctrl.route('/buyKey', methods=['GET', 'POST'])
def keybuy():
	if session.get(u'logged_in') is None:
		return redirect('/invest/login')
	else:
		if request.method == 'POST':
			quantity = request.form['key_quantity']
			quantity = float(quantity)
			checkIsnumber = is_number(quantity)
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})
			sva_balance = float(user['sva_balance'])
			total_invest = float(user['total_invest'])
			if float(total_invest) < 500:
				flash({'msg':'Error!', 'type':'danger'})
				return redirect('/invest/key')
			if quantity == 0 or quantity == '' or checkIsnumber == False:
				flash({'msg':'Please enter valid quantity (quantity > 1)', 'type':'danger'})
				return redirect('/invest/key')
			quantity = round(quantity,0)
			sva_price = float(quantity)*12
			data_ticker = db.tickers.find_one({})
			sva_usd = data_ticker['sva_usd']
			convert_usd_sva = float(sva_price)/float(sva_usd)
			if float(convert_usd_sva) > float(sva_balance):
				flash({'msg':'Your SVA balance is not enough.', 'type':'danger'})
				return redirect('/invest/key')
			new_sva_balance = float(sva_balance) - float(convert_usd_sva)
			new_sva_balance = round(new_sva_balance, 8)
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"sva_balance": new_sva_balance } })
			for x in xrange(0,int(quantity)):
				data_deposit = {
					'uid' : uid,
					'user_id': user_id,
					'username' : user['username'],
					'status' : 1,
					'date_added' : datetime.utcnow(),
					'key' : id_generator()+str(x)
				}
				db.apps.insert(data_deposit)
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(convert_usd_sva),
				'type' : 'send',
				'wallet': 'SVA',
				'date_added' : datetime.utcnow(),
				'detail': 'Paid for buy %s key '%(quantity),
				'rate': '',
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			flash({'msg':'Buy key success', 'type':'success'})
			return redirect('/invest/key')
		return render_template('account/key.html', data=data)
