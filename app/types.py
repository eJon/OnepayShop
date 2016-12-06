# -*- coding: utf-8 -*-

# 夺宝期状态、类型
state_0 = 0
state_1 = 1
state_2 = 2


def period_status():
    return (
        (state_0, u'进行中'),
        (state_1, u'揭晓中'),
        (state_2, u'已揭晓')
    )


# 商品状态
def product_status():
    return (
        (state_0, u'下架'),
        (state_1, u'上架')
    )






# 是否默认地址
def default_addr():
    return (
        (state_0, u'否'),
        (state_1, u'是')
    )



def order_pay_type():
    return (
        (u'优惠券', u'优惠券'),
        (u'余额', u'余额'),
        (u'微信', u'微信'),
        (u'银行卡', u'银行卡')
    )


def charge_pay_type():
    return (
        (u'微信', u'微信'),
        (u'银行卡', u'银行卡')
    )





# 中奖订单发货状态
def win_status():
    return (
        (0, u"未发货"),
        (1, u"已发货")
    )

# charge 状态
def charge_status():
    return (
        (0, u"待付款"),
        (1, u"已付款")
    )
