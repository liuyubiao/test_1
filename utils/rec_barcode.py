#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: Liuyb
@license: Apache Licence
@software: PyCharm
@file: rec_barcode.py
@time: 2022-05-31 16:12
@description: 识别条形码
"""
import cv2
import numpy as np
import pyzbar.pyzbar as pbar

class BarcodeUtils(object):

    def __init__(self):
        pass

    def cv_read(self, image_path):
        '''
        读取中文路径的图片
        :param image_path:
        :return:
        '''
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img

    def get_barcode(self, image_path):
        image = cv2.imread(image_path)
        barcodes = pbar.decode(image)
        barcodes = [item for item in barcodes if item.type != 'QRCODE']

        try:
            barcode_data = barcodes[0]
            barcode = barcode_data.data.decode('utf-8')
        except Exception as e:
            barcode = ''
        return barcode

if __name__ == '__main__':
    rec_obj = BarcodeUtils()
    image_path = '234.jpeg'
    result = rec_obj.get_barcode(image_path)
    print(result)
