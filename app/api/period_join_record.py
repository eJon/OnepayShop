# -*- coding: utf-8 -*-
__author__ = 'wog'

import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response


class ApiPeriodJoinRecord(Resource):
    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):
        pid = int(request.args.get("pid", 0))
        page = int(request.args.get("page", 1))
        if pid:
        	result = self.utils.get_period_join_records(pid, page)
        	return make_response(result, current_page=page)
        


        


