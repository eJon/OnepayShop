# -*- coding: utf-8 -*-
__author__ = 'xu'

from flask import Blueprint

qq_bp = Blueprint('qq_login',__name__)
weibo_bp = Blueprint('weibo_login',__name__)
wechat_bp = Blueprint('wechat_login',__name__)
import qq,weibo,wechat