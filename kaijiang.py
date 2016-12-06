# coding=utf-8
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import urllib2
import json
import time
from app  import models
def my_listener(event):
    if event.exception:
        print('The job crashed :', event.exception)
    else:
        print('The job worked')

def get_ssc():
    url = 'http://chart.cp.360.cn/zst/qkj/?lotId=255401'
    content = urllib2.urlopen(url)
    if content.getcode() == 200:
        ssc_json = json.loads(content.read().decode())
        content.close()
        if int(time.time()) > int(ssc_json['preEndTime']):
            return ssc_json['0']['WinNumber']
        else:
            time.sleep(10)
            return get_ssc()
    else:
        return 0

def caculate_kj_num(kaijiang_ssc):
    try:
        jxz_periods = models.Period.select().where(models.Period.status == 1)
        for period in jxz_periods:
            kj_num = (period.kj_count + kaijiang_ssc) % period.total_count + 100001
            query = models.Order_detail.select().where(models.Order_detail.period == period.id, models.Order_detail.num.contains(int(kj_num)))
            uid=query.get().owner.id
            join_count=int(query.get().count)
            models.Period.update(kj_num=kj_num, kj_ssc=kaijiang_ssc, status=2, zj_user=uid).where(models.Period.id == period.id).execute()
            models.WinRecord.create(period=period.id,zj_user=uid,kj_time=period.kj_time,kj_num=int(kj_num),join_count=join_count)


    except:
        pass

def my_job():
    kaijiang_ssc = int(get_ssc())
    print kaijiang_ssc
    caculate_kj_num(kaijiang_ssc)



def add_job():
    dtime = datetime.now().hour
    if 10 <= dtime < 22:
        sched.add_job(my_job, 'cron', minute='01,11,21,31,41,51', second='30', id='my_job')
    elif dtime < 2 or dtime >= 22:
        sched.add_job(my_job, 'cron', minute='01,11,21,31,41,51,06,16,26,36,46,56', second='30', id='my_job')
    else:
        sched.add_job(my_job, 'cron', hour='10', minute='1', second='30', id='my_job')


sched = BlockingScheduler()
sched.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

add_job()
sched.start()
