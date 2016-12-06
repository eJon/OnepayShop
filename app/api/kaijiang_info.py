# -*- coding: utf-8 -*-
__author__ = 'wog'


import json

from datetime import datetime
from flask import request, g

from flask_restful import Api, Resource



class ApiKaijiang_info(Resource):
    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']

    def get(self):	
        sid= request.args.get("sid")
        Order_details=self.models.Order_detail.select().join(self.models.Period).where((self.models.Period.status==2)&(self.models.Period.product==sid)).order_by(self.models.Order_detail.created_datetime.desc())
        return [o.get_display_data() for o in Order_details]



        


