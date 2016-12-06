# -*- coding: utf-8 -*-
from datetime import datetime
import time
from flask import render_template, redirect, request, url_for, g, abort
from flask_security import login_required, current_user, login_user
from models import Users,  Product, WinRecord, Address, Order_detail, Period,Category,Configure
from . import app, cache_proxy
from utils import request_form_to_dict,get_num,create_or_update_order_detail,update_user,get_kj_time,create_kj_count,\
                            update_period,create_period,get_join_records,get_single_join_record,get_newest_period,get_join_records,get_user_join_records\
                            ,get_user_zj_records,get_user_show_records,get_user_address_records
            
@app.before_request
def int_g():
    g.categorys=Category.get_categorys()
    g.configure=Configure().get(id=1)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
   return render_template('500.html'), 500


@app.route('/')
def my_home():
    categorys_list=[]
    categorys=Category.get_categorys()
    for category in categorys:
        periods=Period.get_index_periods(cid=category.id)
        categorys_list.append((category.name,periods))
    hot_products = Period.get_hot_products()
    return render_template('index.html', categorys_list=categorys_list, hot_products=hot_products)


@app.route('/list')
def product_all():
    page = int(request.args.get("page", 1))
    order = request.args.get("order")
    cid = request.args.get("cid")
    if cid:
        current_cate=Category.get(id=cid)
    else:
        current_cate=None
    periods=Period.get_list_periods(cid=cid,page=page,order=order)
    return render_template( 'new_list.html', periods=periods,order=order,cid=cid,current_cate=current_cate)


@app.route('/shop')
def period_detail():
    pid=request.args.get("pid")
    join_records = None
    count_now_time = None
    user_join_record = None
    zj_user_join_record = None
    newest_period = None
    period = Period.get_period(pid)
    newest_period = get_newest_period(period.product.id)
    join_records=get_join_records(period.kj_time)
    if period.status==1:
        join_records = get_join_records(period.end_time)
        count_now_time = time.time()
        newest_period = get_newest_period(period.product.id)
    if period.status == 2:
        zj_user_join_record = get_single_join_record(period.zj_user.id, pid)
    if current_user.get_id():
        user_join_record = get_single_join_record(current_user.id, pid)
    return render_template('shop.html', period=period, join_records=join_records,
                           count_now_time=count_now_time, newest_period=newest_period, user_join_record=user_join_record,
                           zj_user_join_record=zj_user_join_record)


@app.route('/order', methods=['POST'])
@login_required
def pay():
    if request.method == 'POST':
        data = request_form_to_dict()
        title = data.get("title")
        total_count = int(data.get("total_count"))
        number = int(data.get("number"))
        amount = int(data.get("amount"))
        pid = int(data.get("pid"))
    else:
        abort(404)
    return render_template('product_order.html',title=title,total_count=total_count,number=number,amount=amount,pid=pid)


@app.route('/pay', methods=['POST'])
@login_required
def pay_handler():
    if request.method =='POST':
        data = request_form_to_dict()
        pid = int(data.get("pid"))
        count = int(data.get("amount"))
        period=Period.get(id=pid)
        time_now=datetime.now()
        left=period.total_count-period.join_count
        if left >= count:
            num = get_num(pid, count)
            # 创建或更新夺宝订单明细记录
            create_or_update_order_detail(current_user.id, pid, {
                "count": count,
                "created_datetime": time_now,
                "num": num
            })
            # 更新用户余额
            update_user(current_user.id, current_user.balance - count)
            if left == count:
                kj_time = get_kj_time(time_now)
                update_period(pid, {
                     "join_count": period.join_count + count,
                     "status": 1,
                     "end_time": time_now,
                     "kj_count": create_kj_count(time_now),
                     "kj_time": kj_time,
                })
                create_period(period.product.id, period.total_count,  period.number+ 1)
            else:
                update_period(pid,{
                    "join_count": period.join_count + count,
                    })
            return redirect(url_for('period_detail',pid=pid))

@app.route('/announced')
def announced():
    count_now_time = time.time()
    periods = Period.get_announced_list()
    winrecords=WinRecord.get_winrecords()
    return render_template('announced.html', periods=periods, count_now_time=count_now_time,winrecords=winrecords)


@app.route('/user_home')
@login_required
def home():
    tab=request.args.get("tab")
    uid=current_user.id
    if tab=='join' or tab==None:
        records = get_user_join_records(current_user.get_id())
        return render_template('user/home.html', user=current_user, records=records)
    elif tab=='zj':
        records = get_user_zj_records(uid)
        return render_template('user/home.html', user=current_user, records=records)
    elif tab=='show':
        records = get_user_show_records(uid,with_not_pass=True)
        return render_template('user/home.html', user=current_user, records=records)
    elif tab=='address':
        records = get_user_address_records(uid)
        return render_template('user/home.html', user=current_user, records=records)












