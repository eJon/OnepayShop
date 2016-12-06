# -*- coding: utf-8 -*-
import os
import json
import urllib2
from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_security import login_user
from flask_oauthlib.client import OAuth
from . import wechat_bp
from .. import app, utils
from weixin_compat import fixup_weixin_oauth
# get yours at http://connect.qq.com
we_pub_APP_ID = app.config.get("WX_APPID")
we_pub_APP_KEY = app.config.get("WX_SECRET")

oauth = OAuth(app)

wechat = oauth.remote_app(
    'wechat',
    consumer_key=we_pub_APP_ID,
    consumer_secret=we_pub_APP_KEY,
    base_url='https://api.weixin.qq.com',
    request_token_url=None,
    request_token_params={'scope': 'snsapi_userinfo'},
    access_token_url='https://api.weixin.qq.com/sns/oauth2/access_token',
    authorize_url='https://open.weixin.qq.com/connect/oauth2/authorize',
    content_type='application/json',
)
fixup_weixin_oauth(wechat)

def json_to_dict(x):
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x


def update_wechat_api_request_data(data={}):
    """Update some required parameters for OAuth2.0 API calls"""
    defaults = {
        'openid': session.get('wechat_openid'),
        'access_token': session.get('wechat_token'),
        # 'oauth_consumer_key': we_pub_APP_ID,
    }
    defaults.update(data)
    return defaults


@wechat_bp.route('/wechat/user_info')
def get_user_info():
    if 'wechat_openid' in session:
        data = update_wechat_api_request_data()
        # data["lang"] = 'zh_CN'
        # print data
        info_url = 'https://api.weixin.qq.com/sns/userinfo?access_token=' + data["access_token"] + '&openid=' + data["openid"] + '&lang=zh_CN'
        resp = urllib2.urlopen(info_url)
        user_info = json.loads(resp.read())
        # print user_info
        resp.close()
        user = utils.login_or_create_union_user(data["openid"], user_info, "wx_pub")
        # return jsonify(user.get_display_data())
        return redirect(url_for('my_home'))
    return redirect(url_for('login'))


@wechat_bp.route('/login/wechat')
def wechat_login():
    target = request.args.get("target")
    next = request.args.get("next")
    # print url_for('.authorized')
    if target:
        return wechat.authorize(callback=url_for('.authorized', target=target, _external=True))
    else:
        return wechat.authorize(callback=url_for('.authorized', next=next, _external=True))


@wechat_bp.route('/login_wechat/authorized')
def authorized():
    target = request.args.get("target")
    next = request.args.get("next")
    resp = wechat.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    # print resp
    resp_dict = json_to_dict(resp)
    if type(resp_dict) == dict:
        session["wechat_openid"] = resp_dict.get("openid")
        session["wechat_token"] = resp_dict.get("access_token")
    # print session.get("wechat_openid")
    # print target
    
    # data["lang"] = 'zh_CN'
    
    try:
        # 获取微信用户信息
        data = update_wechat_api_request_data()
        # print data
        info_url = 'https://api.weixin.qq.com/sns/userinfo?access_token=' + data["access_token"] + '&openid=' + data["openid"] + '&lang=zh_CN'
        resp = urllib2.urlopen(info_url)
        user_info = json.loads(resp.read())
        # print user_info
        resp.close()
        user = utils.login_or_create_union_user(data["openid"], user_info, "wx_pub")
        # utils.login_or_create_union_user(session.get("wechat_openid"), {}, "wx_pub")
        if target:
            return redirect(url_for('wx_menu_view',target=target))
        elif next:
            login_user(user)
            return redirect(next)
        else:
            login_user(user)
            return redirect(url_for('product_all'))
    except: 
        return redirect(url_for('product_all'))


@wechat.tokengetter
def get_wechat_oauth_token():
    return session.get('wechat_token')


def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v)) for k, v in dictionary.items())


def change_wechat_header(uri, headers, body):
    """On SAE platform, when headers' keys are unicode type, will raise
    ``HTTP Error 400: Bad request``, so need convert keys from unicode to str.
    Otherwise, ignored it."""
    # uncomment below line while deploy on SAE platform
    # headers = convert_keys_to_string(headers)
    return uri, headers, body

wechat.pre_request = change_wechat_header
