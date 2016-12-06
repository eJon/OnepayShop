# -*- coding: utf-8 -*-

import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response


class ApiHistoryList(Resource):
    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):
        page = int(request.args.get("page", 1))
        proid = int(request.args.get("proid",0))
        result = self.utils.get_history_periods(proid=proid,page=page,limit=g.configure.list_item_number)
        return make_response(result, current_page=page)

