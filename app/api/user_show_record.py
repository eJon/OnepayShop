# -*- coding: utf-8 -*-
__author__ = 'wog'
import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response

class ApiUserShow(Resource):

    def __init__(self, **kwargs):
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):
        uid = int(request.args.get("uid", 0))
        page = int(request.args.get("page", 1))
        if uid:
            result = self.utils.get_user_show_records(uid, page)
            return make_response(result, current_page=page)
