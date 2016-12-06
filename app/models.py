# -*- coding: utf-8 -*-
__author__ = 'wog'
from datetime import datetime, timedelta, date, time
from random import randint
import types
import time
import urllib2
import json
import os
from flask import g, url_for
from flask_peewee.admin import Admin, ModelAdmin, AdminModelConverter, AdminPanel
from flask_security import UserMixin, RoleMixin, PeeweeUserDatastore, Security, current_user
from peewee import TextField, BooleanField, DateTimeField, DateField, \
    IntegerField, ForeignKeyField, CharField, fn, FloatField, CompositeKey, DoubleField
from playhouse.signals import Signal
from . import app, auth, db, cache_proxy
from forms import LoginForms, RegisterForm, ForgotForm, ChangeForm, ResetForm


before_save = Signal()
after_save = Signal()


class SignalModel(db.Model):
    def save(self, *args, **kwargs):
        created = not bool(self.get_id())
        before_save.send(self, created=created)
        super(SignalModel, self).save(*args, **kwargs)
        after_save.send(self, created=created)



class Users(db.Model, UserMixin):
    name = CharField(unique=True, verbose_name=u"用户名")
    email = TextField(unique=True, verbose_name=u"邮箱")
    avatar = CharField(null=True, default="http://img.aixunbang.com/default.jpg", verbose_name=u"头像")
    password = TextField(verbose_name=u"密码")
    active = BooleanField(default=True, verbose_name=u"状态")
    confirmed_at = DateTimeField(null=True, verbose_name=u"认证时间")
    register_at = DateTimeField(default=datetime.now, verbose_name=u"注册时间")
    balance = IntegerField(default=0, verbose_name=u"夺宝币")
    address_count = IntegerField(default=0, verbose_name=u"地址数量")
    default_address_id = IntegerField(default=0, verbose_name=u"默认地址id")
    open_id = CharField(null=True, default=None)
    # flask-secrity 登录ip追踪
    last_login_at = CharField(null=True, verbose_name=u"上次登入")
    current_login_at = CharField(null=True, verbose_name=u"当前登入")
    login_count = IntegerField(default=0, verbose_name=u"登入次数")
    last_login_ip = CharField(null=True, verbose_name=u"上次登入IP")
    current_login_ip = CharField(null=True, verbose_name=u"当前登入IP")
    union_login_type = CharField(null=True, default=None, choices=types.union_login_type())

    def __unicode__(self):
        return self.email
    def __repr__(self):
        return self.name



class Role(db.Model, RoleMixin):
    description = TextField(null=True)
    name = CharField(null=False, default='admin')

    def __unicode__(self):
        return self.name


class UserRoles(db.Model):
    customer = ForeignKeyField(Users, related_name="roles")
    role = ForeignKeyField(Role, related_name="users")
    name = property(lambda self: self.role.name)

    def __unicode__(self):
        return self.name



# 商品类目<==>数据库category表
class Category(db.Model):
    name = CharField(unique=True)
    number=IntegerField(unique=True)
    parent = ForeignKeyField('self', null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_categorys():
        query=Category.select().order_by(Category.number).desc()
        return query

class CategoryAdmin(ModelAdmin):
    def get_admin_name(self):
        return u"类目"



# 商品表<==>数据库product表
class Product(db.Model):
    category = ForeignKeyField(Category, null=False, verbose_name=u"类目")
    title = CharField(verbose_name=u"商品")
    thumbnail = CharField(verbose_name=u"缩略图")
    content = TextField(verbose_name=u"详情")
    hits = IntegerField(default=0, verbose_name=u"热度")
    status = IntegerField(null=False, default=1, choices=types.product_status(), verbose_name=u"状态")
    created_datetime = DateTimeField(default=datetime.now, verbose_name=u"创建时间")
    buy_price = IntegerField(null=False, verbose_name=u"进价")
    sell_price = IntegerField(null=False, verbose_name=u"售价")
    to_index = BooleanField(default=False, verbose_name=u"是否上首页")
    
    def __unicode__(self):
        return self.title

class ProductAdmin(ModelAdmin):
    columns = ['title', 'category', 'buy_price', 'sell_price', 'status', 'hits']

    def get_template_overrides(self):
        return {'add': 'admin_templates/product_create.html',
                'edit': 'admin_templates/product_edit.html'
                }

    def get_admin_name(self):
        return u"商品"

    def save_model(self, instance, form, adding):
        super(ProductAdmin, self).save_model(instance, form, adding)
        if adding:
            from utils import create_period
            create_period(instance.id, instance.sell_price)


# 夺宝期<==>数据库period表
class Period(db.Model):
    product = ForeignKeyField(Product, null=False, verbose_name=u"商品")
    zj_user = ForeignKeyField(Users, null=True, verbose_name=u"中奖用户")
    number = IntegerField(default=100001, verbose_name=u"期号")
    total_count = IntegerField(default=0, verbose_name=u"总需人次")
    join_count = IntegerField(default=0, verbose_name=u"参与人次")
    kj_time = DateTimeField(null=True, verbose_name=u"开奖时间")
    kj_num = IntegerField(default=0, verbose_name=u"开奖号码")
    kj_ssc = DoubleField(default=0, verbose_name=u"时时彩号码")
    kj_count = DoubleField(default=0, verbose_name=u"时间总和")
    all_num = TextField(verbose_name=u"所有号码")
    end_time = DateTimeField(null=True, verbose_name=u"夺宝结束时间")
    status = IntegerField(default=0, verbose_name=u"状态", choices=types.period_status())

    def __unicode__(self):
        return "%s %s%s" % (self.product.title, self.number, u"期")


    @staticmethod
    def get_period(pid):
        period = Period.get(id=pid)
        return period
    

    @staticmethod
    def get_hot_products():
        query=Period.select().join(Product).where(Period.status==0).order_by(Product.hits.desc())
        return query

    @staticmethod
    def get_index_periods(cid):
        query=Period.select().join(Product).where(Product.category==cid,Period.status==0).limit(8)
        return query

    @staticmethod
    def get_list_periods(cid,order='hot',page=1):
        if cid:
            query=Period.select().join(Product).where(Product.category==cid,Period.status==0)
        else:
            query=Period.select().join(Product).where(Period.status==0)
        if order=='hot':
            query=query.order_by(Product.hits.desc())
        elif order == 'left':
            query = query.order_by((Period.total_count - Period.join_count))
        elif order == 'new':
            query = query.order_by(Product.created_datetime.desc())
        elif order == 'price_up':
            query = query.order_by(Period.total_count)
        elif order == 'price_down':
            query = query.order_by(Period.total_count.desc())
        return query.paginate(page,9)

    @staticmethod
    def get_announced_list():
        query=Period.select().where(Period.status==1).order_by(Period.end_time.desc())
        return query

class PeriodAdmin(ModelAdmin):
    columns = ['product', 'number', 'total_count', 'join_count', 'kj_time', 'end_time', 'kj_num', 'kj_ssc',
               'kj_count', 'status', 'zj_user']

    def get_admin_name(self):
        return u"夺宝期"

    def get_display_name(self):
        return self.get_admin_name()
        # def save_model(self,instance,form,adding):
        # pass

# 订单明细表
class Order_detail(db.Model):
    owner = ForeignKeyField(Users, null=False, verbose_name=u"所属用户")
    period = ForeignKeyField(Period, null=False, verbose_name=u"夺宝期")
    created_datetime = DateTimeField(default=datetime.now, verbose_name=u"创建时间")
    count = IntegerField(default=0, verbose_name=u"购买人次")
    num = TextField(null=False, verbose_name=u"分配号码")

    def __unicode__(self):
        return self.period.product.title
    def get_display_data(self):
        return {
            "created_datetime": self.created_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "count": self.count,
            "num": self.num,
            "owner": self.owner,
            "period": self.period
        }

class Order_detailAdmin(ModelAdmin):
    columns = ['created_datetime', 'period', 'owner', 'count', 'num']

    def get_admin_name(self):
        return u"订单明细"

    def get_display_name(self):
        return self.get_admin_name()

    def save_model(self, instance, form, adding):
        pass



# 收获地址表
class Address(db.Model):
    owner = ForeignKeyField(Users, null=False, verbose_name=u"所属用户")
    tel = CharField(null=False, verbose_name=u"联系电话")
    province = CharField(null=False, verbose_name=u"省份")
    city = CharField(null=False, verbose_name=u"市")
    dist = CharField(null=True, verbose_name=u"区/县")
    detail = CharField(null=False, verbose_name=u"街道地址")
    name = CharField(null=False, verbose_name=u"收件人姓名")
    created_datetime = DateTimeField(default=datetime.now)


    @staticmethod
    def create_address(owner, tel, province, city, dist, detail, name):
        # 创建地址
        address = Address.create(
            owner=owner,
            tel=tel,
            province=province,
            city=city,
            dist=dist,
            detail=detail,
            name=name
        )
        if address:
            try:
                user = Users.get(id=owner)
                user.address_count = user.address_count + 1
                user.save()
            except:
                return None
        return ''

    @staticmethod
    def edit_address(addr_id, owner, tel, province, city, dist, detail, name):
        try:
            address = Address.get(id=addr_id)
            address.owner = owner
            address.tel = tel
            address.province = province
            address.city = city
            address.dist = dist
            address.detail = detail
            address.name = name
            address.save()
            return True
        except:
            return None

    @staticmethod
    def get_address_list(uid, need_model=False):
        records =Aaddress.select().where(Address.owner == uid)
        return records if need_model else [record.get_display_data() for record in records]

    @staticmethod
    def set_default_address(addr_id, uid):
        try:
            user = Users.get(id=uid)
            user.default_address_id = addr_id
            user.save()
            return True
        except:
            return False

    @staticmethod
    def delete_address(addr_id, uid):
        try:
            address = Address.get(id=addr_id)
            user = Users.get(id=uid)
            address.delete_instance()
            user.address_count = user.address_count - 1
            if user.default_address_id == addr_id:
                user.default_address_id = 0
            user.save()
            return True
        except:
            return False


class AddressAdmin(ModelAdmin):
    columns = ['owner', 'name', 'tel', 'province', 'city', 'dist']

    def get_admin_name(self):
        return u"地址"

    def get_display_name(self):
        return self.get_admin_name()



# 中奖记录
class WinRecord(db.Model):
    period = ForeignKeyField(Period, null=False, verbose_name=u"夺宝期")
    zj_user = ForeignKeyField(Users, null=False, verbose_name=u"中奖用户")
    join_count=IntegerField(null=False,verbose_name=u'购买人次')
    kj_time = DateTimeField(null=False, verbose_name=u"开奖时间")
    kj_num = IntegerField(default=0, verbose_name=u"开奖号码")
    name = CharField(null=True, verbose_name=u"收货人")
    tel = CharField(null=True, verbose_name=u"电话")
    address = CharField(null=True, verbose_name=u"地址")
    express = CharField(null=True, verbose_name=u"快递公司")
    express_order = CharField(null=True, verbose_name=u"快递单号")
    status = IntegerField(default=0, choices=types.win_status(), verbose_name=u"状态")

    @staticmethod
    def get_winrecords():
        query=WinRecord.select()
        return query



class WinRecordAdmin(ModelAdmin):
    columns = ["period", "zj_user", "kj_time", "kj_num", "status"]

    def get_admin_name(self):
        return u"中奖记录"

    def get_display_name(self):
        return self.get_admin_name()

    def get_template_overrides(self):
        return {'edit': 'admin_templates/win_record_edit.html'
        }


class UsersAdmin(ModelAdmin):
    columns = ['name', 'email', 'balance', 'active', 'register_at']

    def get_admin_name(self):
        return u"用户"

    def get_display_name(self):
        return self.get_admin_name()
        # def save_model(self,instance,form,adding):
        # pass


# 晒单表
class Show(db.Model):
    owner = ForeignKeyField(Users, null=False)
    product = ForeignKeyField(Product, null=False)
    pid = IntegerField(null=False, default=0)
    content = TextField()
    thumbnail = CharField()
    title = CharField()
    created_datetime = DateTimeField(default=datetime.now)
    passed = BooleanField(default=False)

    def get_display_data(self):
        period = Period.get(id=self.pid)
        return {
            "id": self.id,
            "period": period.get_display_data(str_time=True),
            "owner": self.owner.get_display_data(),
            "product": self.product.get_display_data(),
            "created_datetime": self.created_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "content": self.content,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "passed": self.passed
        }

    @staticmethod
    def pass_show(show_id):
        # 通过晒单
        show = Show.get(id=show_id)
        if not show.passed:
            show.passed = True
            # todo 加分
            show.save()
        return show

    @staticmethod
    def create_show(owner, product, content, thumbnail, title, pid=0):
        # 创建晒单
        show = Show.create(
            owner=owner,
            product=product,
            pid=pid,
            content=content,
            thumbnail=thumbnail,
            title=title
        )
        return show

    @staticmethod
    def get_show(show_id, need_model=False):
        # 获取晒单
        try:
            show = Show.get(id=int(show_id))
            return show if need_model else show.get_display_data()
        except:
            return None

    @staticmethod
    def get_list(page=1, with_not_pass=False):
        # 获取晒单列表 默认不返回没通过的
        if with_not_pass:
            query = Show.select()
        else:
            query = Show.select().where(Show.passed == True)
        query = query.order_by(
            Show.created_datetime.desc()
        ).paginate(page=page, paginate_by=g.configure.list_item_number)
        return [q.get_display_data() for q in query]


class ShowAdmin(ModelAdmin):
    columns = ['product', 'owner', 'pid', 'content', 'created_datetime', 'thumbnail', 'title']

    def get_admin_name(self):
        return u"晒单"

    def get_display_name(self):
        return self.get_admin_name()



class Configure(db.Model):
    home_item_number = IntegerField(default=8, verbose_name=u"首页每个类目下的商品数量")
    list_item_number = IntegerField(default=20, verbose_name=u"列表页项目数量")
    price_unit = IntegerField(default=100, verbose_name=u"价格单位", help_text=u"1表示0.01元,100表示1元,1000表示10元.....")
    tel = CharField(default="18512521547", verbose_name=u"客服电话")
    qq = CharField(default="298424338", verbose_name=u"客服qq")
    email = CharField(default="bd@aixunbang.com", verbose_name=u"联系邮箱")
    give_db = BooleanField(default=True, verbose_name=u"是否赠送夺宝币种")

   
class ConfigureAdmin(ModelAdmin):
    columns = ['base_number', 'period_num',  'home_item_number', 'list_item_number']

    def get_admin_name(self):
        return u"配置"

    def get_display_name(self):
        return self.get_admin_name()


user_datastore = PeeweeUserDatastore(db, Users, Role, UserRoles)
security = Security(app, user_datastore,
                    login_form=LoginForms,
                    register_form=RegisterForm,
                    confirm_register_form=RegisterForm,
                    forgot_password_form=ForgotForm,
                    reset_password_form=ResetForm,
                    change_password_form=ChangeForm

                    )

admin = Admin(app, auth)
admin.register(Role, ModelAdmin)
admin.register(UserRoles, ModelAdmin)
admin.register(Category, CategoryAdmin)
admin.register(Product, ProductAdmin)
admin.register(Order_detail, Order_detailAdmin)
admin.register(Period, PeriodAdmin)
admin.register(Configure, ConfigureAdmin)
admin.register(Users, UsersAdmin)
admin.register(Show, ShowAdmin)
admin.register(Address, AddressAdmin)
admin.register(WinRecord, WinRecordAdmin)
admin.register(WinRecord, WinRecordAdmin)
auth.register_admin(admin)
admin.setup()
