# -*- coding: utf-8 -*-
import os
import logging
import memcache
from flask import Flask, Blueprint, url_for
from flask_mail import Mail
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_debugtoolbar import DebugToolbarExtension
from flask_restful import Api, Resource
from config import DevConfig
from api import *


app = Flask(__name__)
# logging.basicConfig(filename='example.log',level=logging.WARNING)


#memcache
from cache import CacheProxy
mc = memcache.Client(['127.0.0.1:11211'],debug=1)
cache_proxy = CacheProxy(mc)
app.extensions = getattr(app, 'extensions', {})
app.extensions['cache_proxy'] = cache_proxy
app.config.from_object(DevConfig)


# db
db = Database(app)
auth = Auth(app, db)
# toolbar = DebugToolbarExtension(app)



mail = Mail(app) 


import models

import utils
utils.create_tables()
utils.init_admin_user()


import views
app.jinja_env.globals['static'] = (
            lambda filename: url_for('static', filename = filename)
    )

# Blueprint for social login
# from social_login import qq_bp, weibo_bp, wechat_bp
# app.register_blueprint(qq_bp)
# app.register_blueprint(weibo_bp)
# app.register_blueprint(wechat_bp)

# configure for api (bluepint for api)
api_bp = Blueprint('api', __name__, url_prefix="/api")
api = Api(api_bp, default_mediatype='application/json')
api.add_resource(ApiPeriodJoinRecord, '/v1.0/period_join_record', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiProductShow, '/v1.0/product_show', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiUserWin, '/v1.0/user_win', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiUserJoinRecord, '/v1.0/user_join', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiUserShow, '/v1.0/user_show', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiUserCharge, '/v1.0/user_cz', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiPeriodHistory, '/v1.0/period_history', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiAddress, '/v1.0/address', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiHistoryList, '/v1.0/history_list', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiAnnounc, '/v1.0/announc_list', resource_class_kwargs={"models": models, "utils": utils})
api.add_resource(ApiIndexList, '/v1.0/index_list', resource_class_kwargs={"models": models, "utils": utils})
app.register_blueprint(api_bp)
