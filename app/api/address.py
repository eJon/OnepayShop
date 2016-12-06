# -*- coding: utf-8 -*-
__author__ = 'wog'
import json
from datetime import datetime
from flask import request, g, redirect, url_for, flash
from flask_restful import Api, Resource
from flask_security import current_user, login_required
from utils import make_response


class ApiAddress(Resource):

	def __init__(self, **kwargs):
		self.models = kwargs['models']
		self.utils = kwargs['utils']

	@login_required
	def post(self):
		data = self.utils.request_form_to_dict()
		edit = request.args.get('edit',0)
		print edit
		if edit:
			# 编辑地址
			try:
				addr_id = int(request.args.get('addr_id',0))
				if not addr_id:
					flash(u"修改地址失败了,请重试", 'address')
					return redirect(url_for('user_home_address',uid=current_user.get_id()))
			except:
				flash(u"修改地址失败了,请重试", 'address')
				return redirect(url_for('user_home_address',uid=current_user.get_id()))
			result = self.models.Ship_address.edit_address(
				addr_id=addr_id,
				owner=current_user.get_id(),
				tel=data["tel"],
				province=data["province"],
	            city=data["city"],
	            dist=data["dist"],
	            detail=data["detail"],
	            name=data["name"]
			)
			if result:
				return redirect(url_for('user_home_address',uid=current_user.get_id()))
			else:
				flash(u"修改地址失败了,请重试", 'address')
				return redirect(url_for('user_home_address',uid=current_user.get_id()))
		else:
			result = self.models.Ship_address.create_address(
				owner=current_user.get_id(),
				tel=data["tel"],
				province=data["province"],
			    city=data["city"],
			    dist=data["dist"],
			    detail=data["detail"],
			    name=data["name"]
			)
			if result:
				return redirect(url_for('user_home_address',uid=current_user.get_id()))
			else:
				flash(u"添加地址失败了,请检重新添加", 'address')
				return redirect(url_for('user_home_address',uid=current_user.get_id()))

	@login_required
	def delete(self):
		data = self.utils.request_form_to_dict()
		try:
			addr_id = int(data["addr_id"])
			uid = int(data["uid"])
		except:
			return make_response(message=u"faile")
		status = self.models.Ship_address.delete_address(addr_id=addr_id, uid=uid)
		if status:
			return make_response()
		else:
			return make_response(message=u"faile")

	@login_required
	def put(self):
		data = self.utils.request_form_to_dict()
		# 设置默认
		try:
			addr_id = int(data["addr_id"])
			uid = int(data["uid"])
		except:
			return make_response(message=u"faile")
		status = self.models.Ship_address.set_default_address(addr_id=addr_id, uid=uid)
		if status:
			return make_response()
		else:
			return make_response(message=u"faile")