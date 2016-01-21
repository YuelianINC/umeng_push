# -*- coding: utf-8 -*-
import time
import hashlib
import json
import urllib.request, urllib.error, urllib.parse

import requests
import shortuuid
from umeng_push.services.message.connect import UMNotification
from .services.message.connect import UMMessage


def md5(s):
    m = hashlib.md5(s)
    return m.hexdigest()


def push_unicast(appkey, app_master_secret, device_token):
    timestamp = int(time.time() * 1000)
    method = 'POST'
    url = 'http://msg.umeng.com/api/send'
    params = {'appkey': appkey,
              'description': 'test',
              'policy': {'out_biz_no': 'CGS7U8QYwoUjetZFo3MvCT'},
              'timestamp': timestamp,
              'device_tokens': device_token,
              'type': 'unicast',
              'production_mode': 'false',
              'payload': {'aps': {
                  "alert": "xxx",
                  },
                          'display_type': 'notification'
                          }
              }
    post_body = json.dumps(params)
    print(post_body)
    sign = md5('%s%s%s%s' % (method, url, post_body, app_master_secret))
    try:
        r = requests.post(url + '?sign=' + sign, data=post_body)
        print(r.content)
        # r = urllib2.urlopen(url + '?sign='+sign, data=post_body)
        # print r.read()
    except urllib.error.HTTPError as e:
        print(e.reason, e.read())
    except urllib.error.URLError as e:
        print(e.reason)


def push_listcast(appkey, app_master_secret, push_infos):
    m = UMMessage(out_biz_no=shortuuid.uuid(),
                  description='有人投票',
                  production_mode=False,
                  app_key=appkey,
                  app_master_secret=app_master_secret,
                  )
    if type(push_infos) in (list, tuple):
        m.set_listcast([(info.umeng_device_token, info.umeng_device_type) for info in push_infos])
    notif = UMNotification(
        text='有人投票',
        ticker='test',
        title='有人投票',
        extra={'display_type': 'notification'},
    )
    notif.set_go_custom('follow')
    notif = UMNotification.load_data(str(notif))
    m.set_notification(notif)
    m.push()

if __name__ == '__main__':
    appkey = ''
    app_master_secret = '',
    device_token = ''

    # push_unicast(appkey, app_master_secret, device_token)
