import json
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from . import weibo_bp
from .. import app,utils

oauth = OAuth(app)
weibo = oauth.remote_app(
    'weibo',
    consumer_key='',
    consumer_secret='',
    request_token_params={'scope': 'email,statuses_to_me_read'},
    base_url='https://api.weibo.com/2/',
    authorize_url='https://api.weibo.com/oauth2/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.weibo.com/oauth2/access_token',
    # since weibo's response is a shit, we need to force parse the content
    content_type='application/json',
)


def json_to_dict(x):
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x

@weibo_bp.route('/login/weibo')
def weibo_login():
    return weibo.authorize(callback=url_for('.authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

# @app.route('/logout')
# def logout():
#     session.pop('oauth_token', None)
#     return redirect(url_for('index'))


@weibo_bp.route('/login_weibo/authorized')
def authorized():
    try:
        resp = weibo.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
    except:
        return redirect(url_for('home'))
    session['oauth_token'] = (resp['access_token'], '')
    session['uid'] = (resp['uid'], '')
    resp = weibo.get('/users/show.json', {'access_token': session['oauth_token'][0],'uid':session['uid'][0]})
    user_info = json_to_dict(resp.data)
    if type(user_info) == dict:
        user = utils.login_or_create_union_user(user_info.get("id"), user_info, "weibo")
    return redirect(url_for('home'))


@weibo.tokengetter
def get_weibo_oauth_token():
    return session.get('oauth_token')


def change_weibo_header(uri, headers, body):
    """Since weibo is a rubbish server, it does not follow the standard,
    we need to change the authorization header for it."""
    auth = headers.get('Authorization')
    if auth:
        auth = auth.replace('Bearer', 'OAuth2')
        headers['Authorization'] = auth
    return uri, headers, body

weibo.pre_request = change_weibo_header