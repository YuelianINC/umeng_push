# -*- coding: utf-8 -*-
import time
import hashlib
import json
import urllib2

import requests


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
    print post_body
    sign = md5('%s%s%s%s' % (method, url, post_body, app_master_secret))
    try:
        r = requests.post(url + '?sign=' + sign, data=post_body)
        print r.content
        # r = urllib2.urlopen(url + '?sign='+sign, data=post_body)
        # print r.read()
    except urllib2.HTTPError, e:
        print e.reason, e.read()
    except urllib2.URLError, e:
        print e.reason


if __name__ == '__main__':
    appkey = ''
    app_master_secret = ''
    device_token = ''

    push_unicast(appkey, app_master_secret, device_token)