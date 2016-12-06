# -*- coding: utf-8 -*-

import json
from datetime import datetime
from flask import request, g
from flask_restful import Api, Resource
from utils import make_response


class ApiIndexList(Resource):
    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):
        cid = int(request.args.get("cid", 0))
        page = int(request.args.get("page", 1))
        order = request.args.get("order", 'hot')
        print cid,page
        result = self.utils.get_category_list(cid=cid,limit=g.configure.list_item_number,page=page,order=order)
        return make_response(result, current_page=page)

