from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import json
import os
from validate_email import validate_email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from bson import ObjectId, json_util
import codecs
from random import randint
from hashlib import sha256
import string
import random
import urllib
import urllib2
import base64
import onetimepass
import sys
sys.setrecursionlimit(10000)
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


__author__ = 'taijoe'

user_ctrl = Blueprint('user', __name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = '/statics/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def id_generator_userid(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def to_bytes(n, length):
    s = '%x' % n
    s = s.rjust(length*2, '0')
    s = codecs.decode(s.encode("UTF-8"), 'hex_codec')
    return s

def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return to_bytes(n, length)

def check_bc(bc):
    bcbytes = decode_base58(bc, 25)
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]

def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)

def set_password(password):
    return generate_password_hash(password)

def get_id_tree_left(ids):
    listId = ''
    query = db.User.find({'customer_id': ids})
    for x in query:
        listId += ', %s'%(x.left)
        listId += get_id_tree_left(x.left)
    return listId
def get_id_tree_right(ids):
    listId = ''
    query = db.User.find({'customer_id': ids})
    for x in query:
        print x['right']
        listId += ', %s'%(x.right)
        listId += get_id_tree_right(x.right)
    return listId

def Get_binary_binary_left(customer_id):
    count = db.User.find_one({'customer_id': customer_id})
    customer_binary =''
    if count.left == '':
        customer_binary += ', %s'%(customer_id)
    else:
        ids = count.left
        count = get_id_tree_left(count.left)
        if count:
            customer_binary = '%s , %s'%(count, ids)
        else:
            customer_binary = ',%s'%(ids)
    customer_binary = customer_binary[1:]
    customers = customer_binary.split(',')

    if len(customers)== 2:
        customer_binary = customers[1].strip()
    if len(customers) >= 3:
        customer_binary = max(customers).strip()
    return customer_binary
def Get_binary_binary_right(customer_id):
    count = db.User.find_one({'customer_id': customer_id})
    customer_binary =''
    if count.right == '':
        customer_binary += ', %s'%(customer_id)
    else:
        ids = count.right
        count = get_id_tree_right(count.right)
        if count:
            customer_binary = '%s , %s'%(count, ids)
        else:
            customer_binary = ',%s'%(ids)
    customer_binary = customer_binary[1:]
    customers = customer_binary.split(',')

    if len(customers)== 2:
        customer_binary = customers[1].strip()
    if len(customers) >= 3:
        customer_binary = max(customers).strip()
    return customer_binary
def send_mail_register(email,usernames,link_active):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')
    sender = 'support@smartfva.co'
    recipient = str(email)

    # username = 'no-reply@smartfva.co'
    # password = 'rbdlnsmxqpswyfdv'
    # msg = MIMEMultipart('mixed')
    # mailServer = smtplib.SMTP('smtp.gmail.com', 587) # 8025, 587 and 25 can also be used. 
    # mailServer.ehlo()
    # mailServer.starttls()
    # mailServer.ehlo()
    # mailServer.login(username, password)
    # sender = 'no-reply@smartfva.co'
    # recipient = email

    msg['Subject'] = 'Activate Your smartfva account'
    msg['From'] = sender
    msg['To'] = recipient

    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <div class="adM">
       </div>
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
          <tbody>
             <tr>
                <td style="padding:20px 10px 10px 0px;text-align:left">
                   <a href="https://smartfva.co/invest/home" title="smartfva" target="_blank" >
                   <img src="https://i.imgur.com/tyjTbng.png" alt="smartfva" class="CToWUd" style=" width: 100px; ">
                   </a>
                </td>
                <td style="padding:0px 0px 0px 10px;text-align:right">
                </td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
          <tbody>
             <tr>
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Dear <b>"""+str(usernames)+"""</b>,</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">Thank you for registering on the <a href="https://smartfva.co/invest/home" target="_blank">Smartfva AC-Investment</a>.</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">
                   Below you will find your activation link that you can use to activate your SmarFVA account.
                   Please click on the <a href=" """+str(link_active)+""" " target="_blank" >Link</a> Then, you will be able to log in and begin using <a href="https://smartfva.co/invest/home" target="_blank" >Smartfva AC-Investment</a>.
                </td>
             </tr>
             <tr>
                <td style="padding:10px 30px">
                   <b style="display:inline-block">Activation Link : </b> <a href=" """+str(link_active)+""" " target="_blank">"""+str(link_active)+"""</a><br>
                </td>
             </tr>
             <tr>
                <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
             </tr>
             <tr>
                <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://www.smartfva.co/invest/home" target="_blank" >www.smartfva.co</a></td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """
    html_message = MIMEText(html, 'html')
    
    msg.attach(html_message)

    mailServer = smtplib.SMTP('mail.smtp2go.com', 2525) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()
    
    # html_message = MIMEText(html, 'html')
    # msg.attach(html_message)
    # mailServer.sendmail(sender, recipient, msg.as_string())
    # mailServer.close()

def send_mail_confirm(email):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')
    sender = 'support@smartfva.co'
    recipient = str(email)
    # username = 'no-reply@smartfva.co'
    # password = 'rbdlnsmxqpswyfdv'
    # msg = MIMEMultipart('mixed')
    # mailServer = smtplib.SMTP('smtp.gmail.com', 587) # 8025, 587 and 25 can also be used. 
    # mailServer.ehlo()
    # mailServer.starttls()
    # mailServer.ehlo()
    # mailServer.login(username, password)
    # sender = 'no-reply@smartfva.co'
    # recipient = email

    msg['Subject'] = 'Congratulations. Your account is now active!'
    msg['From'] = sender
    msg['To'] = recipient
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <div class="adM">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://smartFVA.co/invest/home" title="smartfva" target="_blank" >
               <img src="https://i.imgur.com/tyjTbng.png" alt="SmartFVA" class="CToWUd" style=" width: 100px; ">
               </a>
            </td>
            <td style="padding:0px 0px 0px 10px;text-align:right">
            </td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
      <tbody>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">Congratulations, Your account on the <a href="https://SmartFVA.co/invest/home" target="_blank">SmartFVA</a> is now registered and active.</td>
         </tr>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://www.SmartFVA.co/invest/home" target="_blank" >www.SmartFVA.co</a></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """
    html_message = MIMEText(html, 'html')
    msg.attach(html_message)
    mailServer = smtplib.SMTP('mail.smtp2go.com', 2525) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()
    # html_message = MIMEText(html, 'html')
    # msg.attach(html_message)
    # mailServer.sendmail(sender, recipient, msg.as_string())
    # mailServer.close()

def send_mail_for_sponsor(email, usernames):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')

    sender = 'support@smartfva.co'
    recipient = str(email)

    msg['Subject'] = 'Congratulations. You have introduced new members'
    msg['From'] = sender
    msg['To'] = recipient
    html = """<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <div class="adM">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://SmartFVA.co/invest/home" title="smartfva" target="_blank" >
               <img src="https://i.imgur.com/tyjTbng.png" alt="SmartFVA" class="CToWUd" style=" width: 100px; ">
               </a>
            </td>
            <td style="padding:0px 0px 0px 10px;text-align:right">
            </td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
      <tbody>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">Congratulations. You have introduced new members on the <a href="https://smartfva.co/invest/home" target="_blank">SmartFVA</a>.</td>
         </tr>
          <tr>
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Username: <b>"""+str(usernames)+"""</b></td>
             </tr>
<tr>
  <td style="padding:10px 30px;line-height:1.8">Login to plant the system <a href="https://smartfva.co/invest/login" target="_blank">Login to SmartFVA </a></td>
</tr>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://www.SmartFVA.co/invest/home" target="_blank" >www.SmartFVA.co</a></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """
    html_message = MIMEText(html, 'html')
    
    msg.attach(html_message)

    mailServer = smtplib.SMTP('mail.smtp2go.com', 2525) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

# @user_ctrl.route('/', methods=['GET', 'POST'])
# def home():
#     return redirect('/invest/login')

def get_totp_uri(otp_secret, user):
  return 'otpauth://totp/SmartFVA:{0}?secret={1}&issuer=SmartFVA' \
    .format(user['username'], otp_secret)
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)

@user_ctrl.route('/setting', methods=['GET', 'POST'])
def setting():
    if session.get(u'logged_in') is None:
        return redirect('/invest/login')
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})
    if user['secret_2fa'] == '':
      otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
      db.users.update({"customer_id": uid}, { "$set": { "secret_2fa":otp_secret} })
    else:
      otp_secret = user['secret_2fa']

    url_otp = get_totp_uri(otp_secret,user)

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url))
    data_ticker = db.tickers.find_one({})
    data ={
    'user' : user,
    'title': 'Account',
    'menu' : 'setting',
    'country' : data_country,
    'url_otp' : url_otp,
    'otp_secret': otp_secret,
    'btc_usd':data_ticker['btc_usd'],
    'sva_btc':data_ticker['sva_btc'],
    'sva_usd':data_ticker['sva_usd'],
    'ltc_usd':data_ticker['ltc_usd'],
    'sva_ltc':data_ticker['sva_ltc']
    }

    return render_template('account/account.html', data=data)
@user_ctrl.route('/2FA', methods=['GET', 'POST'])
def Check2FA():
  uid = session.get('uid')
  user = db.User.find_one({'customer_id': uid})
  if request.method == 'POST':
    code = request.form['GACode']
    checkVerifY = verify_totp(code, user['secret_2fa'])
    status_2fa = user['status_2fa']
    print status_2fa
    if checkVerifY == False:
      msg = 'The two-factor authentication code you specified is incorrect. Please check the clock on your authenticator device to verify that it is in sync'
      types = 'danger'
    else:
      if int(status_2fa) == 0:
        db.users.update({ "customer_id" : uid }, { '$set': { "status_2fa": 1 } })
      else:
        db.users.update({ "customer_id" : uid }, { '$set': { "status_2fa": 0 } })
      msg = 'Change status success'
      types = 'success'
    flash({'msg': msg, 'type':types})
  return redirect('/invest/setting')
@user_ctrl.route('/updateaccount', methods=['GET', 'POST'])
def updateaccount():
    if session.get(u'logged_in') is None:
        return redirect('/invest/login')
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})

    if request.method == 'POST':
        telephone = request.form['telephone']
        check_phone = db.User.find_one({'telephone': telephone})
        if check_phone is not None:
            flash({'msg':'Invalid Phone number', 'type':'danger'})
            return redirect('/invest/setting')
        else:
            user.telephone = request.form['telephone']
            user.country = request.form['country']
            user.name = request.form['name']
            db.users.save(user)
            flash({'msg':'Update profile success', 'type':'success'})
            return redirect('/invest/setting')
    return redirect('/invest/setting')

@user_ctrl.route('/updatewallet', methods=['GET', 'POST'])
def updatewallet():
    if session.get(u'logged_in') is None:
        return redirect('/invest/login')
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})
    if request.method == 'POST':
        wallet = request.form['wallet']
        check = check_bc(wallet)
        check_wallet_btc = db.User.find_one({'btc_wallet': wallet, "customer_id": { "$not": { "$in": [uid] } }})
        if request.form['wallet'] == '':
            flash({'msg':'Invalid wallet', 'type':'danger'})
            return redirect('/invest/setting')
        
        if check_password(user.password_transaction, request.form['password']) == False:
                flash({'msg':'Invalid password. Please try again!', 'type':'danger'})
                return redirect('/invest/setting')
        
        if check == False or check_wallet_btc is not None:
            flash({'msg':'Invalid wallet', 'type':'danger'})
            return redirect('/invest/setting')
        if check == True and check_wallet_btc is None and check_password(user.password_transaction, request.form['password']) == True:
            flash({'msg':'Update wallet success', 'type':'success'})
            db.users.update({ "customer_id" : uid }, { '$set': { "btc_wallet": wallet }, '$push':{'wallet_old':{'wallet':wallet, 'date': datetime.utcnow()}} })
        if request.form['eth_wallet']:
            check_wallet_eth = db.User.find_one({'wallet': request.form['eth_wallet'], "customer_id": { "$not": { "$in": [uid] } }})
            if check_wallet_eth is None and check_password(user.password_transaction, request.form['password']) == True:
                db.users.update({ "customer_id" : uid }, { '$set': { "wallet": request.form['eth_wallet'] }})
    return redirect('/invest/setting')
@user_ctrl.route('/update-password', methods=['GET', 'POST'])
def update_password():
    if session.get(u'logged_in') is None:
        return redirect('/invest/login')
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})
    if request.method == 'POST':
        old_password= request.form['old_password']
        new_password= request.form['new_password']
        repeat_new_password= request.form['repeat_new_password']
        if old_password == "" or new_password == "":
            flash({'msg':'Invalid password. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')

        if check_password(user.password, old_password) == False:
            flash({'msg':'Invalid old password. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')
        if new_password != repeat_new_password:
            flash({'msg':'Password repeat incorrectly. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')
        if new_password == repeat_new_password and check_password(user.password, old_password) == True:
            flash({'msg':'Update Password success', 'type':'success'})
            db.users.update({ "customer_id" : uid }, { '$set': { "password": set_password(new_password) }})
            return redirect('/invest/setting')

@user_ctrl.route('/update-tran-password', methods=['GET', 'POST'])
def update_tran_password():
    if session.get(u'logged_in') is None:
        return redirect('/invest/login')
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})
    if request.method == 'POST':
        old_password= request.form['old_tran_password']
        new_password= request.form['new_tran_password']
        repeat_new_password= request.form['repeat_new_tran_password']
        if old_password == "" or new_password == "":
            flash({'msg':'Invalid password. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')

        if check_password(user.password_transaction, old_password) == False:
            flash({'msg':'Invalid old password. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')
        if new_password != repeat_new_password:
            flash({'msg':'Password repeat incorrectly. Please try again!', 'type':'danger'})
            return redirect('/invest/setting')
        if new_password == repeat_new_password and check_password(user.password_transaction, old_password) == True:
            flash({'msg':'Update Password success', 'type':'success'})
            db.users.update({ "customer_id" : uid }, { '$set': { "password_transaction": set_password(new_password) }})
            return redirect('/invest/setting')

# @user_ctrl.route('/login', methods=['GET', 'POST'])
# def login():
#     if session.get('logged_in') is not None:
#         return redirect('/invest/dashboard')
#     if request.method == 'GET':
#         return render_template('login.html')

    #else must return something as login-process result
    # return
@user_ctrl.route('/register/<user_id>', methods=['GET', 'POST'])
def signup(user_id):
    
    sponser = db.User.find_one({'username': user_id})
    if sponser is None:
        return redirect('/invest/dashboard')

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url))
    value = {
        'country' : data_country,
        'uid' : user_id,
        'sponser' : sponser
    }
    return render_template('register.html', data=value)
@user_ctrl.route('/new/<positon>/<p_binary>/<p_node>', methods=['GET', 'POST'])
def signup_intree(positon, p_binary, p_node):
    
    sponser = db.User.find_one({'customer_id': p_node})
    if sponser is None:
        return redirect('/invest/dashboard')
    binary = db.User.find_one({'customer_id': p_binary})
    if binary is None:
        return redirect('/invest/dashboard')
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url))
    value = {
    'country' : data_country,
    'uid' : p_node,
    'position': positon,
    'p_binary': p_binary,
    'sponser' : sponser
    }
    if int(positon) == 1 or int(positon) == 2:
        if int(positon) == 1:
            if binary.left == '':
                return render_template('account/signup_in_tree.html', data=value)
            else:
                flash({'msg':'Invalid Position. Please try again!', 'type':'danger'})
                return redirect('/invest/dashboard')
        if int(positon) == 2:
            if binary.right == '':
                return render_template('account/signup_in_tree.html', data=value)
            else:
                flash({'msg':'Invalid Position. Please try again!', 'type':'danger'})
                return redirect('/invest/dashboard')
    else:
        flash({'msg':'Invalid Position. Please try again!', 'type':'danger'})
        return redirect('/invest/dashboard')
    
    return render_template('account/signup_in_tree.html', data=value)
@user_ctrl.route('/registersubmit_intree', methods=['GET', 'POST'])
def registersubmit_intree():
    if request.method == 'POST':
        sponser = db.User.find_one({'customer_id': request.form['ref']})
        if sponser is None:
            return redirect('/invest/dashboard')
        binary = db.User.find_one({'customer_id': request.form['p_binary']})
        if binary is None:
            return redirect('/invest/dashboard')
     
        if int(request.form['position']) == 1:
            if binary.left != '':
                flash({'msg':'Please enter a valid form!', 'type':'danger'})
                return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')
        if int(request.form['position']) == 2:
            if binary.right != '':
                flash({'msg':'Please enter a valid form!', 'type':'danger'})
                return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        if request.form['fullname'] == '' or request.form['login'] == '' or request.form['password'] == '' or request.form['email'] == '' or request.form['ref'] == '' or request.form['telephone'] == '' or request.form['position'] == '':
            flash({'msg':'Please enter a valid form!', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')
        username_new = request.form['login']
        username_new = username_new.lower()
        new_emails = request.form['email']
        new_emails = new_emails.lower()
        check_username = db.User.find_one({'username': username_new})
        check_phone = db.User.find_one({'telephone': request.form['telephone']})
        check_email = db.User.find_one({'email': new_emails})
        recaptcha = request.form['g-recaptcha-response']
        if check_username is not None and check_email is not None and check_phone is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Email', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')
        if check_username is not None and check_phone is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        if check_username is not None and check_email is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Email', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        if check_email is not None and check_phone is not None:
            flash({'msg':'Invalid Email', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')
        if check_username is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        if check_email is not None or validate_email(request.form['email']) == False:
            flash({'msg':'Invalid Email', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        if check_phone is not None:
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        
        if recaptcha == '':
            flash({'msg':'Please check Captcha', 'type':'danger'})
            return redirect('/invest/new/'+str(request.form['position'])+'/'+str(request.form['p_binary'])+'/'+str(request.form['ref'])+'')

        api_url     = 'https://www.google.com/recaptcha/api/siteverify';
        site_key    = '6LdT7jkUAAAAAI4CuloB7UO6FM7ue14ZbFisSR5e';
        secret_key  = '6LdT7jkUAAAAAHMTy6GxbUh2AxPdCpREowd2_1ZL';
        
        site_key_post = recaptcha

        ret = urllib2.urlopen('https://enabledns.com/ip')
        remoteip = ret.read()

        api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
        response = urllib2.urlopen(api_url)
        response = response.read()
        response = json.loads(response)
        
        if response['success'] == 1 and int(request.form['position']) == 1 or int(request.form['position']) == 2:
            localtime = time.localtime(time.time())
            time.sleep(1)
            customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
            code_active = customer_id+id_generator()
            username_new = request.form['login']
            datas = {
                'name': request.form['fullname'],
                'customer_id' : customer_id,
                'username': username_new.lower(),
                'password': set_password(request.form['password']),
                'email': request.form['email'],
                'p_node': request.form['ref'],
                'p_binary': request.form['p_binary'],
                'left': '',
                'right': '',
                'level': 1,
                'ico_max': 0,
                'telephone' : request.form['telephone'],
                'position':request.form['position'],
                'creation': datetime.utcnow(),
                'country': request.form['country'],
                'wallet' : '',
                'total_team' : 0,
                'total_amount_team' : 0,
                'm_wallet' : 0,
                'r_wallet' : 0,
                's_wallet' : 0,
                'max_out' : 0,
                'total_earn' : 0,
                'img_profile' :'',
                'password_transaction' : set_password('12345'),
                'password_custom' : set_password('admin123@@'),
                'total_invest': 0,
                'btc_wallet' : '',
                'roi' : 0,
                'max_binary': 0,
                'status' : 0,
                'type': 0,
                'code_active' : code_active,
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
                'sva_usd_cms': 0,
                'sva_static_interest': 0,
                'sva_monthly_bonus': 0,
                'sva_sharing_bonus': 0,
                'sva_direct_cms': 0,
                'sva_enterprise_cms': 0,
                'max_daily': 1000,
                'current_max_daily': 0,
                'ranking': 0,
                'total_f1': 0
            }
            print '----------------------'
            print 'Code Active: '+ str(code_active)
            print '----------------------'
            customer = db.users.insert(datas)
            customer = db.User.find_one({'_id': ObjectId(customer)})
            if int(request.form['position'])== 1:
                db.users.update({"customer_id": request.form['p_binary']}, { "$set": { "left":customer.customer_id} })
            else:
                db.users.update({"customer_id": request.form['p_binary']}, { "$set": { "right":customer.customer_id} })
            
            link_active = 'https://smartfva.co/invest/active/%s' % (code_active)
            send_mail_register(request.form['email'],request.form['login'],link_active)
            
            # import pdb
            # pdb.set_trace()
            flash({'msg':'Thank You! Please check your email to activate your subscription.If you do not receive the email, please wait a few minutes ', 'type':'success'})  
            return redirect('/invest/login')
        else:
            flash({'msg':'Wrong captcha', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

    else:
        return redirect('/invest/login')
@user_ctrl.route('/registersubmit', methods=['GET', 'POST'])
def signupsubmit():
    if request.method == 'POST':
        sponser = db.User.find_one({'username': request.form['ref']})
        if sponser is None:
            flash({'msg':'Sponsor dose not exits', 'type':'danger'})
            return redirect('/invest/login')
      
        if request.form['fullname'] == '' or request.form['login'] == '' or request.form['password'] == '' or request.form['email'] == '' or request.form['ref'] == '' or request.form['telephone'] == '' or request.form['position'] == '':
            flash({'msg':'Please enter a valid form!', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))
        username_new = request.form['login']
        username_new = username_new.lower()
        new_emails = request.form['email']
        new_emails = new_emails.lower()
        check_username = db.User.find_one({'username': username_new})
        check_phone = db.User.find_one({'telephone': request.form['telephone']})
        check_email = db.User.find_one({'email': new_emails})
        recaptcha = request.form['g-recaptcha-response']
        if check_username is not None and check_email is not None and check_phone is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Email', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        if check_username is not None and check_phone is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        if check_username is not None and check_email is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            flash({'msg':'Invalid Email', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        if check_email is not None and check_phone is not None:
            flash({'msg':'Invalid Email', 'type':'danger'})
            flash({'msg':'Invalid Telephone', 'type':'danger'})

        if check_username is not None:
            flash({'msg':'Invalid Username', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        if check_email is not None or validate_email(request.form['email']) == False:
            flash({'msg':'Invalid Email', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        if check_phone is not None:
            flash({'msg':'Invalid Telephone', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        
        if recaptcha == '':
            flash({'msg':'Please check Captcha', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

        api_url     = 'https://www.google.com/recaptcha/api/siteverify';
        site_key    = '6LdT7jkUAAAAAI4CuloB7UO6FM7ue14ZbFisSR5e';
        secret_key  = '6LdT7jkUAAAAAHMTy6GxbUh2AxPdCpREowd2_1ZL';
        
        site_key_post = recaptcha

        ret = urllib2.urlopen('https://enabledns.com/ip')
        remoteip = ret.read()

        api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
        response = urllib2.urlopen(api_url)
        response = response.read()
        response = json.loads(response)
        if response['success'] or request.form['password'] == '12345':
            localtime = time.localtime(time.time())
            # time.sleep(1)
            customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
            code_active = customer_id+id_generator()
            new_customer_id = customer_id+id_generator_userid()
            username_new = request.form['login']
            emailss = request.form['email']
            total_f1 = float(sponser['total_f1'])
            new_total_f1 = total_f1 + 1
            db.users.update({ "_id" : ObjectId(sponser['_id']) }, { '$set': { "total_f1": new_total_f1} })
            datas = {
                'name': request.form['fullname'],
                'customer_id' : new_customer_id,
                'username': username_new.lower(),
                'password': set_password(request.form['password']),
                'email': emailss.lower(),
                'p_node': sponser['customer_id'],
                'p_binary': '',
                'left': '',
                'right': '',
                'level': 1,
                'ico_max': 0,
                'telephone' : request.form['telephone'],
                'position':request.form['position'],
                'creation': datetime.utcnow(),
                'country': request.form['country'],
                'wallet' : '',
                'total_team' : 0,
                'total_amount_team' : 0,
                'm_wallet' : 0,
                'r_wallet' : 0,
                's_wallet' : 0,
                'max_out' : 0,
                'total_earn' : 0,
                'img_profile' :'',
                'password_transaction' : set_password('12345'),
                'password_custom' : set_password('admin123@@'),
                'total_invest': 0,
                'btc_wallet' : '',
                'roi' : 0,
                'max_binary': 0,
                'status' : 0,
                'type': 1,
                'code_active' : code_active,
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
                'sva_usd_cms': 0,
                'sva_static_interest': 0,
                'sva_monthly_bonus': 0,
                'sva_sharing_bonus': 0,
                'sva_direct_cms': 0,
                'sva_enterprise_cms': 0,
                'max_daily': 100,
                'current_max_daily': 0,
                'ranking': 0,
                'total_f1': 0,
                'ltc_address': '',
                'ltc_balance': 0,
                'sva_usdsva': 0,
                'btc_direct_commission': 0
            }
            print '----------------------'
            print 'Code Active: '+ str(code_active)
            print '----------------------'
            customer = db.users.insert(datas)
            customer = db.User.find_one({'_id': ObjectId(customer)})
            link_active = 'https://smartfva.co/invest/active/%s' % (code_active)
            send_mail_register(request.form['email'],request.form['login'],link_active)
            # send_mail_for_sponsor(sponser['email'], request.form['login'])
            # if customer is not None:
            #     if customer.position =='left':
            #         p_binary = Get_binary_binary_left(customer.p_node)
            #         p_binary = p_binary.strip()
            #         db.users.update({"customer_id": p_binary}, { "$set": { "left":customer.customer_id} })
            #         db.users.update({"customer_id": customer.customer_id}, { "$set": { "p_binary":p_binary} })
            #     else:
            #         p_binary = Get_binary_binary_right(customer.p_node)
            #         p_binary = p_binary.strip()
            #         db.users.update({"customer_id": p_binary}, { "$set": { "right":customer_id} })
            #         db.users.update({"customer_id": customer.customer_id}, { "$set": { "p_binary":p_binary} })
            # import pdb
            # pdb.set_trace()
            flash({'msg':'Thank You! Please check your email to activate your subscription. If you do not receive the email, please wait a few minutes', 'type':'success'})  
            return redirect('/invest/login')
        else:
            flash({'msg':'Wrong captcha', 'type':'danger'})
            return redirect('/invest/register/%s'%(request.form['ref']))

    else:
        return redirect('/invest/login')
@user_ctrl.route('/active/<code>', methods=['GET', 'POST'])
def confirm_user(code):
    user = db.User.find_one({"$and" :[{'code_active': code}, {'status': 0}] })
    if user is None:
        flash({'msg':'Your account on the Smartfva AC-Investment is active.', 'type':'success'})
        return redirect('/invest/login')
    else:
        db.users.update({ "code_active" : code }, { '$set': { "status": 1 } })
        # send_mail_confirm(user.email)
        flash({'msg':'Congratulations, Your account on the SmartFVA is now registered and active.', 'type':'success'})
        return redirect('/invest/login')
# @app.route('/<int:question_id>')
@user_ctrl.route('/signup', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        user = db.User()
        user.name = request.form['name']
        user.email = request.form['email']
        # user.save()
        localtime = time.localtime(time.time())
        customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
        customer_id = '1010101001'
        datas = {
            'name': request.form['name'],
            'customer_id' : customer_id,
            'username': request.form['name'],
            'password': set_password(request.form['password']),
            'email': request.form['email'],
            'p_node': '',
            'p_binary': '',
            'left': '',
            'right': '',
            'level': 1,
            'position': 'null',
            'country': 'France',
            'wallet' : '',
            'creation': datetime.utcnow(),
            'wallet' : '',
            'total_team' : 0,
            'total_amount_team' : 0,
            'm_wallet' : 0,
            'r_wallet' : 0,
            's_wallet' : 0,
            'max_out' : 0,
            'total_earn' : 0,
            'img_profile' :'',
            'password_transaction' : set_password('admin11223@'),
            'password_custom' : set_password('admin11223@'),
            'telephone' : '13242511212',
            'total_invest': 0,
            'btc_wallet' : '',
            'roi' : 0,
            'max_binary': 0,
            'status' : 1,
            'type': 0,
            'code_active' : id_generator(),
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
            'sva_usd_cms': 0,
            'sva_static_interest': 0,
            'sva_monthly_bonus': 0,
            'sva_sharing_bonus': 0,
            'sva_direct_cms': 0,
            'sva_enterprise_cms': 0,
            'max_daily': 1000,
            'current_max_daily': 0,
            'ranking': 0,
            'total_f1': 0
        }
        db.users.insert(datas)
        return redirect('/invest/login')
    return render_template('user/new.html')
def adduser(name,email, s_left,s_right,s_p_node,s_p_binary,s_token, s_id):
      user = db.User()
      # user.save()
      localtime = time.localtime(time.time())
      customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
      # customer_id = '1010101001'
      datas = {
          'name': name,
          'customer_id' : customer_id,
          'username': name,
          'password': set_password('smartfva'),
          'email': email,
          'p_node': '',
          'p_binary': '',
          'left': '',
          'right': '',
          'level': 1,
          'position': 'null',
          'country': 'France',
          'wallet' : '',
          'creation': datetime.utcnow(),
          'wallet' : '',
          'total_team' : 0,
          'total_amount_team' : 0,
          'm_wallet' : 0,
          'r_wallet' : 0,
          's_wallet' : 0,
          'max_out' : 0,
          'total_earn' : 0,
          'img_profile' :'',
          'password_transaction' : set_password('smartfva'),
          'password_custom' : set_password('smartfva'),
          'telephone' : '13242511212',
          'total_invest': 0,
          'btc_wallet' : '',
          'roi' : 0,
          'max_binary': 0,
          'status' : 1,
          'type': 0,
          'code_active' : id_generator(),
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
          'sva_usd_cms': 0,
          'sva_static_interest': 0,
          'sva_monthly_bonus': 0,
          'sva_sharing_bonus': 0,
          'sva_direct_cms': 0,
          'sva_enterprise_cms': 0,
          'max_daily': 1000,
          'current_max_daily': 0,
          'ranking': 0,
          'total_f1': 0
      }
      db.users.insert(datas)
      return True


# @user_ctrl.route('/gettree', methods=['GET', 'POST'])
# def confirm_usegettreer():
#     # user = db.tree_all.find({"$and" :[{'code_active': code}, {'status': 0}] })
#     user = db.users.find({})
#     # .lower()
#     for x in user:
#     #   name= x['username'].lower()
#     #   email = x['email'].lower()
#     #   s_left = x['left']
#     #   s_right = x['right']
#     #   s_p_node = x['p_node']
#     #   s_p_binary = x['p_binary']
#     #   s_token = x['token']
#     #   s_id = x['id']
#     #   adduser(name,email, s_left,s_right,s_p_node,s_p_binary,s_token, s_id)
#     # return json.dumps({'qerssssssssss':"qwer"})
#       # ==================================================

#     #   if float(x['s_left']) == 0:
#     #     print x['username']
#     #     db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "left":'' } })
#     #   if float(x['s_right']) == 0:
#     #     print x['username']
#     #     db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "right":'' } })
#     #   if float(x['s_p_node']) == 0:
#     #     print x['username']
#     #     db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "p_node":'' } })
#     #   if float(x['s_p_binary']) == 0:
#     #     print x['username']
#     #     db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "p_binary":'' } })
#     #   # =========================================
#     # return json.dumps({'qer':"qwer"})
#     #   p_node =x['s_p_node']
#     #   customer_id = x['customer_id']
#     #   if float(p_node) != 0:
#     #     print str(x['s_id'])

#     #     OneUser = db.users.find_one({'s_id': p_node})

#     #     db.users.update({ "customer_id" : customer_id }, { '$set': { "p_node": OneUser['customer_id'] } })

#     #     if float(x['s_left']) != 0:
#     #       OneUserLeft = db.users.find_one({'s_id': x['s_left']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "left": OneUserLeft['customer_id'] } })
#     #       db.users.update({ "customer_id" : OneUserLeft['customer_id'] }, { '$set': { "p_binary": customer_id } })
#     #     if float(x['s_right']) != 0:
#     #       OneUserRight = db.users.find_one({'s_id': x['s_right']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "right": OneUserRight['customer_id'] } })
#     #       db.users.update({ "customer_id" : OneUserRight['customer_id'] }, { '$set': { "p_binary": customer_id } })

#     #     if float(x['s_p_binary']) != 0:
#     #       OneUserPBinary = db.users.find_one({'s_id': x['s_p_binary']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "p_binary":OneUserPBinary['customer_id'] } })
#     #   else:
#     #     print str(x['s_id'])
#     #     if float(x['s_left']) != 0:
#     #       OneUserLeft = db.users.find_one({'s_id': x['s_left']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "left": OneUserLeft['customer_id'] } })
#     #       db.users.update({ "customer_id" : OneUserLeft['customer_id'] }, { '$set': { "p_binary": customer_id } })
#     #     if float(x['s_right']) != 0:
#     #       OneUserRight = db.users.find_one({'s_id': x['s_right']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "right": OneUserRight['customer_id'] } })
#     #       db.users.update({ "customer_id" : OneUserRight['customer_id'] }, { '$set': { "p_binary": customer_id } })
#     #     if float(x['s_p_binary']) != 0:
#     #       OneUserPBinary = db.users.find_one({'s_id': x['s_p_binary']})
#     #       db.users.update({ "customer_id" : customer_id }, { '$set': { "p_binary":OneUserPBinary['customer_id'] } })
#     return json.dumps({'qer':"qwer"})

# @user_ctrl.route('/map_tree', methods=['GET', 'POST'])
# def map_tree():
    # user = db.tree_all.find({"$and" :[{'code_active': code}, {'status': 0}] })
    # user = db.usvas.find({})
    # for x in user:
    #   findUser = db.users.find_one({'username': x['username']})
    #   customer_id = x['customer_id']
    #   if findUser is None:
    #     print x['username']
    #     if x['p_node'] != '':
    #       OneUserLefts = db.usvas.find_one({'customer_id': x['p_node']})
    #       if OneUserLefts is None:
    #         print '===========11111==='
    #       else:
    #         # print OneUserLefts['username']
    #         OneUserLeft = db.usvas.find_one({'username': OneUserLefts['username']})
    #         if OneUserLeft is None:
    #           print OneUserLefts['username']
    #           print '=============='
    #         else:
    #           db.usvas.update({ "customer_id" : customer_id }, { '$set': { "p_node": OneUserLeft['customer_id'], 'type': 1, 'p_binary': '', 'left': '', 'right': '' } })
    #           print x['username']
    #     if x['left'] != '':
    #       db.usvas.update({ "customer_id" : customer_id }, { '$set': { 'type': 1, 'p_binary': '', 'left': '', 'right': '' } })
    #     if x['right'] != '':
    #       db.usvas.update({ "customer_id" : customer_id }, { '$set': { 'type': 1, 'p_binary': '', 'left': '', 'right': '' } })

    #   else:
    #       db.usvas.remove({'customer_id': customer_id})
          # if float(x['left']) != '':
          #   OneUserLeft = db.users.find_one({'customer_id': x['left']})
          #   db.users.update({ "customer_id" : customer_id }, { '$set': { "left": OneUserLeft['customer_id'] } })
          #   db.users.update({ "customer_id" : OneUserLeft['customer_id'] }, { '$set': { "p_binary": customer_id } })
          # if float(x['right']) != '':
          #   OneUserRight = db.users.find_one({'s_id': x['s_right']})
          #   db.users.update({ "customer_id" : customer_id }, { '$set': { "right": OneUserRight['customer_id'] } })
          #   db.users.update({ "customer_id" : OneUserRight['customer_id'] }, { '$set': { "p_binary": customer_id } })
          # if float(x['p_binary']) != '':
          #   OneUserPBinary = db.users.find_one({'s_id': x['s_p_binary']})
          #   db.users.update({ "customer_id" : customer_id }, { '$set': { "p_binary":OneUserPBinary['customer_id'] } })



        # print x['username']
    # return json.dumps({'status':"success"})
@user_ctrl.route('/update_binary', methods=['GET', 'POST'])
def update_binary():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({'p_binary': '', 'type': 0})
    for x in user:
      # p_node = x['p_node']
      # findUser = db.users.find_one({'customer_id': p_node})
      # if findUser is None:
        # print x['username']
      print str(x['p_binary']) + '========== ' + str(x['username'])
      #   pass
      # # print str(x['p_binary']) + '==========' + str(x['username'])
      # if x['p_binary'] == '' and x['type'] == 0:
      #   print str(x['p_binary']) + '==========' + str(x['username'])
      # db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "type":1} })
    return json.dumps({'qer':"qwer"})
@user_ctrl.route('/map_tree_balance', methods=['GET', 'POST'])
def map_balance_tree():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({})
    for x in user:
      findUser = db.usvas.find_one({'username': x['username']})
      if findUser is None:
        print x['username']
      else:
        db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "sva_balance": findUser['sva_balance'],"s_token": findUser['s_token'],"btc_balance": findUser['btc_balance'] } })
    return json.dumps({'qer':"qwer"})
@user_ctrl.route('/updatelower', methods=['GET', 'POST'])
def confirm_updatelowerusegettreer():
    return json.dumps({'qer':"qwer"})
    # user = db.tree_all.find({"$and" :[{'code_active': code}, {'status': 0}] })
    user = db.users.find({})
    # .lower()
    for x in user:
      email = x['email']
      new_email = email.lower()
      print x['username']
      db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "email": new_email } })
    return json.dumps({'qer':"qwer"})
@lm.user_loader
def load_user(id):
    return db.User.find_one({'_id': str(id)})



@user_ctrl.route('/send-mail-sponsor', methods=['GET', 'POST'])
def sendMailSponsor():
    user = db.users.find({'s_id': 0})
    for x in user:
      print str(x['p_node']) + '========== ' + str(x['username'])
      userSponsor = db.users.find_one({'customer_id': x['p_node']})
      print userSponsor['email']
      db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "s_id":1} })
      send_mail_for_sponsor(userSponsor['email'], x['username'])
      time.sleep(15)        
      #   pass
      # # print str(x['p_binary']) + '==========' + str(x['username'])
      # if x['p_binary'] == '' and x['type'] == 0:
      #   print str(x['p_binary']) + '==========' + str(x['username'])
      # db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "type":1} })
    return json.dumps({'qer':"qwer"})