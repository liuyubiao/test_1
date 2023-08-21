#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: Liuyb 
@license: Apache Licence  
@software: PyCharm 
@file: datetime_utils.py 
@time: 2022-07-02 20:33 
@description: 时间类
"""
import datetime

class DateUtils(object):

    def __init__(self):
        self.pattern = '%Y-%m-%d %H:%M:%S'

    def get_current_time(self):
        '''
        获取当前的格式化时间
        '''
        current_time = datetime.datetime.now()
        current_time = current_time.strftime(self.pattern)
        return current_time

if __name__ == "__main__":
    du = DateUtils()
    result = du.get_current_time()
    print(result)