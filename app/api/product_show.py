# -*- coding: utf-8 -*-
__author__ = 'wog'
import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response


class ApiProductShow(Resource):
	def __init__(self, **kwargs):
		self.models = kwargs['models']
		self.utils = kwargs['utils']
	def get(self):
		proid = int(request.args.get("proid", 0))
		page = int(request.args.get("page", 1))
		if proid:
			result = self.utils.get_product_show_records(proid, page)
			return make_response(result, current_page=page)