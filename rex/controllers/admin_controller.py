from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model, admin_model
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
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

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)
__author__ = 'carlozamagni'

admin_ctrl = Blueprint('admin', __name__, static_folder='static', template_folder='templates')
