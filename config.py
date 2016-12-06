# -*- coding: utf-8 -*-
__author__ = 'wog'


class Config(object):

	SECRET_KEY = 'super-secret'
	UPLOAD_FOLDER= '/home/xu/oneshop/app/static/images/headimage/'
	SECURITY_TRACKABLE = True
	SECURITY_LOGIN_USER_TEMPLATE = "login.html"
	SECURITY_FORGOT_PASSWORD_TEMPLATE="forgot_password.html"
	SECURITY_RESET_PASSWORD_TEMPLATE="reset_password.html"
	SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
	SECURITY_PASSWORD_SALT = SECRET_KEY
	SECURITY_REGISTERABLE = True
	SECURITY_RECOVERABLE = True
	SECURITY_CHANGEABLE = True
	SECURITY_CONFIRMABLE = True
	SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
	SECURITY_REGISTER_USER_TEMPLATE = "register.html"
	SECURITY_REGISTER_URL = "/register"
	SECURITY_EMAIL_SENDER = "no-reply@aixunbang.com"

	MAIL_SERVER = 'smtp.ym.163.com'
	MAIL_PORT = '25'
	MAIL_USERNAME = "no-reply@aixunbang.com"
	MAIL_PASSWORD = "killqrf123!"

class DevConfig(Config):
	DATABASE = {
	    'name': 'example.db',
	    'engine': 'peewee.SqliteDatabase'
	}
	DEBUG=True

class ProConfig(Config):
	DATABASE = {
	    'name': 'axb_oneshop',
	     'engine': 'peewee.PostgresqlDatabase',
	     'user': 'axb_oneshop',
	     'password': 'killqrf1990'
	}
	ADMIN_URL = "/axb/axb/admin"
	BRANDING = "AXB"
	DEBUG = False
	FREE_BLOCK_NUM = 50
	INVITE_SCORE = 100
	PER_PAGE = 16
	SITEMAP_MAX_URL_COUNT = 2000
	MEMCACHE = ['127.0.0.1:11211']




