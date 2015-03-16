#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last modified: Wang Tai (i@wangtai.me)

__revision__ = '0.1'

__all__ = [
    'UMMessage',
    'UMNotification',
]

from django.conf import settings

try:
    APP_KEY = getattr(settings, 'UMENG_APP_KEY', None)
    APP_MASTER_SECRET = getattr(settings, 'UMENG_APP_MASTER_SECRET', None)
except:
    APP_KEY = ''
    APP_MASTER_SECRET = ''


import time

import hashlib
import json
import requests
import logging


from enum import Enum


class MsgType(Enum):
    unicast = 'unicast'
    list_cast = 'listcast'
    file_cast = 'filecast'
    broadcast = 'broadcast'
    group_cast = 'groupcast'
    customized_cast = 'customizedcast'


class DisplayType(Enum):
    message = 'message'  # 简单消息
    notification = 'notification'  # 复杂通知


class AfterOpenType(Enum):
    go_app = 'go_app'
    go_url = 'go_url'
    go_activity = 'go_activity'
    go_custom = 'go_custom'


class MsgReturnData(object):

    def __init__(self,
                 ret,
                 thirdparty_id,
                 msg_id=None,
                 error_code=None):
        self.ret = ret
        self.thirdparty_id = thirdparty_id
        self.msg_id = msg_id
        self.error_code = error_code

    def __str__(self):
        return "{} {} {} {}".format(self.ret, self.thirdparty_id, self.msg_id, self.error_code)


class UMNotification(object):

    def __init__(self,
                 ticker,  # 通知栏提示文字
                 title,  # 通知标题
                 text,  # 通知文字描述
                 builder_id=0,  # 开发者必须在SDK里面实现自定义通知栏样式。
                 icon=None,
                 large_icon=None,
                 img=None,
                 sound=None,
                 play_vibrate=False,
                 play_lights=False,
                 play_sound=False,
                 extra=None  # 用户自定义key-value。只对"通知"
                 ):
        """
        :param ticker,  # 通知栏提示文字
        :param title,  # 通知标题
        :param text,  # 通知文字描述
        :param builder_id=0, #  开发者必须在SDK里面实现自定义通知栏样式。
        :param extra=None # 用户自定义key-value。只对"通知"
        """
        self.ticker = ticker
        self.title = title
        self.text = text
        self.icon = icon
        self.large_icon = large_icon
        self.img = img
        self.sound = sound
        self.builder_id = builder_id
        self.play_vibrate = play_vibrate
        self.play_lights = play_lights
        self.play_sound = play_sound
        self.extra = extra

        self.after_open = AfterOpenType.go_app

    @staticmethod
    def load_data(data):
        data = json.loads(data)
        extra = data.get('extra', None)

        notif = UMNotification(ticker=data['ticker'],  # 通知栏提示文字
                               title=data['title'],  # 通知标题
                               text=data['text'],  # 通知文字描述
                               builder_id=data.get('builder_id', 0),  # 开发者必须在SDK里面实现自定义通知栏样式。
                               icon=data.get('icon', None),
                               large_icon=data.get('large_icon', None),
                               img=data.get('img', None),
                               sound=data.get('sound', None),
                               play_vibrate=data.get('play_vibrate', False),
                               play_lights=data.get('play_lights', False),
                               play_sound=data.get('play_sound', False),
                               extra=extra  # 用户自定义key-value。只对"通知"
                               )

        after_open = data['after_open']
        if after_open == 'AfterOpenType.go_app':
            notif.set_go_app()
        elif after_open == 'AfterOpenType.go_activity':
            notif.set_go_activity(data['activity'])
        elif after_open == 'AfterOpenType.go_custom':
            notif.set_go_custom(data['custom'])
        elif after_open == 'AfterOpenType.go_url':
            notif.set_go_url(data['url'])

        return notif

    def set_go_app(self):
        self.after_open = AfterOpenType.go_app

    def set_go_url(self, url):
        self.after_open = AfterOpenType.go_url
        self.url = url

    def set_go_activity(self, activity):
        self.after_open = AfterOpenType.go_activity
        self.activity = activity

    def set_go_custom(self, custom):
        """
        :param custom json or str
        """
        self.after_open = AfterOpenType.go_custom
        try:
            self.custom = json.loads(custom)
        except:
            self.custom = custom

    def __str__(self):
        attrs = vars(self)
        data = {}
        for key, value in attrs.items():
            if value == AfterOpenType.go_app:
                value = 'AfterOpenType.go_app'
            elif value == AfterOpenType.go_activity:
                value = 'AfterOpenType.go_activity'
            elif value == AfterOpenType.go_custom:
                value = 'AfterOpenType.go_custom'
            elif value == AfterOpenType.go_url:
                value = 'AfterOpenType.go_url'
            data.update({key: value})
        return json.dumps(data)


class UMMessage(object):

    def __init__(self,
                 out_biz_no,  # 开发者对消息的唯一标识，服务器会根据这个标识避免重复发送。
                 description,  # 发送消息描述，建议填写。
                 production_mode=False,
                 thirdparty_id=None,  # 开发者自定义消息标识ID
                 app_key=APP_KEY,
                 app_master_secret=APP_MASTER_SECRET,
                 ):
        """
        :param out_biz_no,  # 开发者对消息的唯一标识，服务器会根据这个标识避免重复发送。
        :param description,  # 发送消息描述，建议填写。
        :param thirdparty_id=None,  # 开发者自定义消息标识ID
        """
        if app_key is None or app_master_secret is None:
            raise ValueError('APP_KEY or APP_MASTER_SECRET is None')

        self.thirdparty_id = thirdparty_id
        self.out_biz_no = out_biz_no
        self.app_key = app_key
        self.app_master_secret = app_master_secret
        self.device_tokens = []
        self.type = None
        self.display_type = None
        self.custom = None
        self.description = description
        self.production_mode = production_mode
        self.url = 'http://msg.umeng.com/api/send'
        self.params = None

    @property
    def params(self):
        if self.__params is None:
            self.__build_params()
        return self.__params

    @params.setter
    def params(self, params):
        self.__params = params

    def set_unicast(self, device_token):
        self.type = MsgType.unicast
        self.device_tokens = device_token
        return self

    def set_listcast(self, device_tokens):
        self.type = MsgType.list_cast
        self.device_tokens = device_tokens
        return self

    def set_broadcast(self):
        self.type = MsgType.broadcast
        return self

    def set_message(self, message_body):
        self.display_type = DisplayType.message
        self.custom = message_body
        return self

    def set_notification(self, notification):
        self.display_type = DisplayType.notification
        self.notification = notification
        self.custom = notification.custom
        return self

    def set_policy(self,
                   start_time=None,
                   expire_time=None,
                   max_send_num=None):
        self.start_time = start_time
        self.expire_time = expire_time
        self.max_send_num = max_send_num
        return self

    def __md5(self, s):
        m = hashlib.md5(s)
        return m.hexdigest()

    def __build_params(self):  # noqa
        if self.type is None:
            raise ValueError('message type is None, call set_unicast/set_listcast/set_broadcast/set_message first')

        if self.display_type is None:
            raise ValueError('display type is None, call set_notification/set_message first')

        timestamp = int(time.time() * 1000)
        params = {'appkey': self.app_key,
                  'timestamp': timestamp,
                  'type': self.type.value,
                  'device_tokens': ','.join(self.device_tokens),
                  'payload': {'body': {},
                              'display_type': self.display_type.value
                              },
                  'policy': {
                      'out_biz_no': self.out_biz_no
                      },
                  'production_mode': 'true' if self.production_mode else 'false',
                  }

        # display_type
        if self.display_type == DisplayType.message:
            if self.custom is None:
                raise ValueError('custom parameter is None')
            params['payload']['body'].update({'custom': self.custom})

        elif self.display_type == DisplayType.notification:
            # check required parameters
            # fill info params
            for item in ('ticker', 'title', 'text'):
                params['payload']['body'].update({item: getattr(self.notification, item)})

            for item in ('icon', 'img', 'sound', 'builder_id'):
                value = getattr(self.notification, item)
                if value is not None:
                    params['payload']['body'].update({item: value})

            # large_icon
            for item, real_name in (('large_icon', 'largeIcon'), ):
                value = getattr(self.notification, item)
                if value is not None:
                    params['payload']['body'].update({real_name: value})

            # play_vibrate, play_lights, play_vibrate
            for item in ('play_vibrate', 'play_lights', 'play_sound'):
                value = getattr(self.notification, item)
                if value is not None:
                    params['payload']['body'].update({item: 'true' if value else 'false'})

            # after_open
            params['payload']['body'].update({'after_open': self.notification.after_open.value})
            if self.notification.after_open == AfterOpenType.go_app:
                pass
            elif self.notification.after_open == AfterOpenType.go_url:
                params['payload']['body'].update({'url': self.notification.url})
            elif self.notification.after_open == AfterOpenType.go_activity:
                params['payload']['body'].update({'activity': self.notification.activity})
            elif self.notification.after_open == AfterOpenType.go_custom:
                params['payload']['body'].update({'custom': self.custom})
            else:
                raise ValueError('after_open type Not Supported')

            # extra
            extra_value = getattr(self.notification, 'extra')
            if extra_value is not None:
                params['payload'].update({'extra': extra_value})

        else:
            raise ValueError('display type not supported')

        # policy
        for item in ('start_time', 'expire_time', 'max_send_num'):
            value = getattr(self, item, None)
            if value is not None:
                params['policy'].update({item: value})

        # description
        if self.description is not None:
            params.update({'description': self.description})

        if self.thirdparty_id is not None:
            params.update({'thirdparty_id': self.thirdparty_id})

        self.params = params
        return params

    def __build_sign(self, params):
        post_body = json.dumps(params)
        logging.debug(post_body)

        sign = self.__md5('{}{}{}{}'.format('POST', self.url, post_body, self.app_master_secret))
        return sign

    def __process_rt_data(self, ret_text):
        # process return data
        data = json.loads(ret_text)
        logging.debug(data)
        print data
        if data.get('ret') == 'SUCCESS':
            msg_data = MsgReturnData(ret=data.get('ret'),
                                     thirdparty_id=data.get('data').get('thirdparty_id'),
                                     msg_id=data.get('data').get('msg_id'))
        else:
            msg_data = MsgReturnData(ret=data.get('ret'),
                                     thirdparty_id=data.get('data').get('thirdparty_id'),
                                     error_code=data.get('data').get('error_code'))

        print msg_data
        return msg_data

    def push(self, ):

        params = self.__build_params()

        sign = self.__build_sign(params)

        r = requests.post(self.url + '?sign='+sign, data=json.dumps(params))
        from yl_umeng_api.services.message.error_codes import HTTPStatusCode

        status_code = HTTPStatusCode(r.status_code)
        if status_code == HTTPStatusCode.OK:
            # return success
            rt_data = self.__process_rt_data(r.text)
            return rt_data
        elif status_code == HTTPStatusCode.INTERNAL_SERVER_ERROR:
            # return failure
            rt_data = self.__process_rt_data(r.text)

            from yl_umeng_api.services.message.error_codes import UMPushError, APIServerErrorCode

            raise UMPushError(APIServerErrorCode(int(rt_data.error_code)), params)
        else:
            from yl_umeng_api.services.message.error_codes import UMHTTPError

            raise UMHTTPError(status_code)


if __name__ == "__main__":
    UMENG_APP_KEY = '527203e256240b705d06fafa'
    UMENG_APP_MASTER_SECRET = '8ghx471whykgxigizjzpawhczdk9bokv'
    import shortuuid
    m = UMMessage(out_biz_no=shortuuid.uuid(),
                  description='test',
                  app_key=UMENG_APP_KEY,
                  app_master_secret=UMENG_APP_MASTER_SECRET
                  )
    # m.set_unicast(['AqeMKU0exV4f80YUac3JEVccuuELHuFdjH5EO-m6rU3z'])  # Wang Tai's mobile
    notif = UMNotification(
        ticker='test',
        title='test',
        text='test',
        extra={'m': 'k', 'm2': 'k2'}
    )
    notif.set_go_custom('follow')
    print str(notif)
    notif = UMNotification.load_data(str(notif))
    m.set_notification(notif)
    print str(notif)
    print m.params
    m.push()
