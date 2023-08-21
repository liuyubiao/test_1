#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2022/9/13 17:36
# @Author  : liuyb
# @File    : gs1_utils.py
# @Describe: gs1调用工具类

import requests
import json


class GS1Utils(object):

    def __init__(self):
        self.outside_url = 'https://127.0.0.1/barcode'
        self.outside_appcode = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.headers = {'Authorization': 'APPCODE ' + self.outside_appcode, 'Content-Type': 'application/x-www-form-urlencoded'}

    def get_outside_gs1_data(self, barcode):
        '''
        从gs1接口中获取品牌和商品全称
        Args:
            barcode:

        Returns:

        '''
        brand, goods_name = '不分', '不分'
        params = {'code': barcode}
        result = requests.get(self.outside_url, params=params, headers=self.headers)

        try:
            infos = json.loads(result.text)

            showapi_res_code = infos['showapi_res_code']
            if showapi_res_code != 0:
                raise Exception('请求接口出现异常')

            showapi_res_body = infos['showapi_res_body']

            brand, goods_name = showapi_res_body['trademark'], showapi_res_body['goodsName']
        except Exception as e:
            print('调用外部数据出现异常: {}'.format(str(e)))
        return brand, goods_name

if __name__ == '__main__':
    gs1_utils = GS1Utils()

    barcode = '6971828770021'
    brand, goods_name = gs1_utils.get_outside_gs1_data(barcode)
    print('品牌为: {}, 商品全称为: {}'.format(brand, goods_name))