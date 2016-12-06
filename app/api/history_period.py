# -*- coding: utf-8 -*-
__author__ = 'wog'

import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response


class ApiPeriodHistory(Resource):

    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):
        proid = int(request.args.get("proid", 0))
        number = int(request.args.get("number", 0))
        if proid and number:
            result = self.utils.get_history_period(proid, number)
            if result.get("zj_user"):
                result["display_id"] = result["zj_user"]["id"] + 100000
            return make_response(result)
