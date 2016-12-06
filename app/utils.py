# -*- coding: utf-8 -*-
__author__ = 'wog'
import random
import time
from math import ceil
import json
import requests
import urllib2
from datetime import datetime, date, timedelta
from flask import jsonify, g, abort, request, url_for
from flask_security import current_user, login_user
from models import Users, Role, UserRoles, Category, Product, Period, Order_detail, Address, Show,UserRoles, Configure, WinRecord
from . import auth, app


# """
# 功能函数，包括数据库查询 算法等
# """
# 获取请求数据
def request_form_to_dict():
    data = {}
    for key in request.form.keys():
        tmp = key if not key.endswith("[]") else key[:-2]
        if len(request.form.getlist(key)) > 1:
            data[tmp] = request.form.getlist(key)
        else:
            data[tmp] = request.form.getlist(key)[0]
    return data

#获取商品的最新一期夺宝
def get_newest_period(proid):
    period = Period.select().where(Period.product == proid, Period.status == 0).get()
    return period

# 获取截止时间点前最后50参与记录
def get_join_records(end_time, limit=50):
    records = Order_detail.select().where(Order_detail.created_datetime <= end_time). \
        order_by(Order_detail.created_datetime.desc()).limit(limit)
    return [record.get_display_data() for record in records]


def get_single_join_record(uid, pid):
    try:
        record = Order_detail.select().where(Order_detail.owner == uid, Order_detail.period == pid).get()
        return record.get_display_data()
    except:
        return False

# 增加或更新订单明星记录
def create_or_update_order_detail(uid, pid, data):
    try:
        record = Order_detail.select().where(Order_detail.owner == uid, Order_detail.period == pid).get()
        record.num = record.num + ' ' + data["num"]
        record.count = record.count + data["count"]
        record.save()
    except:
        Order_detail.create(owner=uid, period=pid, count=data["count"], num=data["num"],
                            created_datetime=data["created_datetime"])

# 更新夺宝期记录
def update_period(pid, data):
    period = Period.get(id=int(pid))
    if data.get("status"):
        period.join_count = data["join_count"]
        period.status=data["status"]
        period.end_time=data["end_time"]
        period.kj_count=data["kj_count"]
        period.kj_time=data["kj_time"]
    else:
        period.join_count = data["join_count"]
    period.save()

# 更新用户余额记录
def update_user(uid, new_balance):
    Users.update(balance=new_balance).where(Users.id == uid).execute()


# 计算开奖时间
def get_kj_time(time_now):
    if 10 <= time_now.hour < 22:
        kj_time = int(int(datetime_to_timestamp(time_now)) / 600 + 1) * 600 + 90
    elif time_now.hour >= 22 or time_now.hour < 2:
        kj_time = int(int(datetime_to_timestamp(time_now)) / 300 + 1) * 300 + 90
    else:
        kj_time = no_ssc_kj_time()
    kj_date_time = datetime.fromtimestamp(kj_time)
    return kj_date_time

# 初始化夺宝期号码
def create_all_num(length):
    text = ''
    for x in xrange(1, length + 1):
        text += str(x + 100001)
        if x < length:
            text += ' '
    return text


#  分配号码
def get_num(pid, price):

    period = Period.get(id=pid)
    all_seq = str(period.all_num).split(' ')
    random_seq = random.sample(all_seq, price)
    random_text = ' '.join(random_seq)
    left_seq = set(all_seq) - set(random_seq)
    left_text = ' '.join(left_seq)
    period.all_num=left_text
    period.save()
    return random_text

# datetime 转时间戳
def datetime_to_timestamp(date_time):
    time_array = time.strptime(date_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_array))


# 开奖时间求和
def create_kj_count(end_time):
    kj_count = 0
    order_details = Order_detail.select(Order_detail.created_datetime).where( Order_detail.created_datetime <= end_time).\
    order_by(Order_detail.created_datetime.desc()).limit(50)
    for o in order_details:
        kj_count += int(datetime_to_timestamp(o.created_datetime))
    return kj_count


# 福彩不开奖时 夺宝开奖时间
def no_ssc_kj_time():
    time_str = datetime.now().strftime('%Y-%m-%d') + " 10:01:30"
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_array))

# 初始化新的夺宝期
def create_period(pro_id, tcount, number=None):
    if number:
        Period.create(
            product=pro_id,
            number=number,
            total_count=tcount,
            all_num=create_all_num(tcount),
        )
    else:
        Period.create(
            product=pro_id,
            total_count=tcount,
            all_num=create_all_num(tcount),
        )


# 获取用户夺宝记录
def get_user_join_records(uid, page=1, limit=20):
    records = Order_detail.select().where(Order_detail.owner == uid). \
        order_by(Order_detail.created_datetime.desc()).paginate(page=page, paginate_by=limit)
    return [record.get_display_data() for record in records]


# 获取用户中奖记录
def get_user_zj_records(uid, page=1, limit=20):
    records = WinRecord.select().where(WinRecord.zj_user == uid). \
        order_by(WinRecord.kj_time.desc()).paginate(page=page, paginate_by=limit)
    return records


# 获取用户地址
def get_user_address_records(uid):
    records = Address.select().where(Address.owner == uid)
    return [record.get_display_data() for record in records]

# 创建数据表
def create_tables():
    auth.User.create_table(fail_silently=True)
    Users.create_table(fail_silently=True)
    Role.create_table(fail_silently=True)
    Category.create_table(fail_silently=True)
    Product.create_table(fail_silently=True)
    Period.create_table(fail_silently=True)
    Order_detail.create_table(fail_silently=True)
    Address.create_table(fail_silently=True)
    Show.create_table(fail_silently=True)
    UserRoles.create_table(fail_silently=True)
    Configure.create_table(fail_silently=True)
    WinRecord.create_table(fail_silently=True)



# 初始化后台管理用户
def init_admin_user():
    if auth.User.select().count() == 0:
        admin = auth.User(username='xu', email='zhuofanxu@live.com', admin=True, active=True)
        admin.set_password('123456')
        admin.save()
    if Configure.select().count() == 0:
        Configure.create()


