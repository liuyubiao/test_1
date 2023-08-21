#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/29 14:14
# @Author  : liuyb
# @Site    : 
# @File    : process_controller.py
# @Software: PyCharm
# @Description: 流程控制(根据返回结果修改最终的输出) -- OCR批量处理时

from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

import os
import numpy as np
import cv2
from PIL import Image
import time
import uuid
from json import dumps
import requests
import json
import base64
import shutil

# from concurrent.futures import ThreadPoolExecutor
# executor = ThreadPoolExecutor()

from importlib import import_module
from contstant import RULE_MAPPING, CLASSIFY_MAPPING
from utils.datetime_utils import DateUtils
# 2022-07-05 加入ip监控
from utils.db_utils import DBUtils
# 2022-09-13 加入GS1数据
from utils.gs1_utils import GS1Utils

from flask import Flask, request
from flask_cors import CORS
#from tornado.wsgi import WSGIContainer
#from tornado.httpserver import HTTPServer
#from tornado.ioloop import IOLoop

app = Flask(__name__)
PORT = 5030

CORS(app,  resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = "api"

UPLOAD_PATH = 'static/upload/'
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

IP = '127.0.0.1'

LOCAL_PATH = '/root/data/project/product_recognize_main/static/upload/'
# 进行OCR的识别服务链接
ocr_url = 'http://127.0.0.1:5032/ocrReocg3'
# zx做的品类
other_url = 'http://127.0.0.1:5031/all_category_text_rule'

def cv_imread(file_path):
    '''
    兼容读取中文路径的图片
    :param file_path:
    :return
    '''
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

def trans_image_channels(file_path):
    '''
    将文件转换成三通道数据
    :param file_path:
    :return:
    '''
    img = Image.open(file_path)

    img_mode = img.mode
    if img_mode != 'RGB':
        img = img.convert('RGB')
        img.save(file_path)
    return file_path

def trans_run(params):
    '''
    将请求进行转发
    :param params:
    :return:
    '''
    trans_url = 'http://127.0.0.1/process_image'
    for i in range(8):
        requests.post(url='%s' % (trans_url), data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    # requests.post(url='%s' % (trans_url), data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

@app.route('/process_image', methods=['GET', 'POST'])
def inference():
    result = {}
    start = time.time()

    if request.method == "POST":
        # 2023-02-04添加：为了实现并行验证效果：将请求异步转发出去
        # executor.submit(lambda p:trans_run(*p), [request.form])

        image_paths = []

        # 2022-07-05 增加访问记录
        # 存储访问的数据
        try:
            visit_ip, visit_type = request.remote_addr, '1'
            visit_id = db.save_visit_record_info(visit_ip, visit_type)
        except Exception as e:
            print('记录访问ip时出现异常: {}'.format(str(e)))
            result['result'] = -1
            result['msg'] = '网络请求异常'

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        # 存储上传的图片
        item_start = time.time()
        print('获取的参数为: {}'.format(request.values))
        classify_code = request.form.get('cat')
        product_name = request.form.get('adid')
        product_name = product_name.strip()
        barcode = request.form.get('barCode')
        base64strs = json.loads(request.form.get('base64strs'))
        image_list = json.loads(request.form.get('imageList'))
        item_end = time.time()
        print('获取参数耗时:{}s'.format(item_end-item_start))
        
        item_start = time.time()
        if classify_code == None or classify_code == '':
            print('识别出现异常: 未上传商品品类')
            result['result'] = -1
            result['msg'] = '未上传商品品类'

            # 存储访问结果
            visit_result = result['result']
            db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        # 设置最终存储位置
        if product_name == None or product_name == '':
            tmp_path = str(uuid.uuid1())
        else:
            tmp_path = product_name
        upload_path = os.path.join(UPLOAD_PATH, tmp_path + '/')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        if len(image_list) > 0:
            image_type = '0'
        else:
            image_type = '1'

        if image_type == '0':
            for upload in image_list:
                image_name = os.path.split(upload)[-1]
                image_path = "/".join([upload_path, image_name])

                if upload.find('http') >= 0:
                    r = requests.get(upload)
                    with open(image_path, "wb") as code:
                        code.write(r.content)
                else:
                    shutil.copy(upload, image_path)
                # 因为模型仅处理三通道的数据,所以上传文件如果不为三通道,需要将其转化
                image_path = trans_image_channels(image_path)
                image_paths.append(image_path)
        else:
            # 使用base64存储到本地
            for base64str in base64strs:
                imagedata = base64.b64decode(base64str)

                image_name = '{}.jpg'.format(str(uuid.uuid1()))
                image_path = "/".join([upload_path, image_name])
                with open(image_path, "wb") as code:
                    code.write(imagedata)
                # 因为模型仅处理三通道的数据,所以上传文件如果不为三通道,需要将其转化
                image_path = trans_image_channels(image_path)
                image_paths.append(image_path)
        item_end = time.time()
        print('存储文件耗时: {}s'.format(item_end-item_start))
         
        # 存储访问详情
        try:
            category_id, product_id, barcode, image_type, image_list = classify_code, tmp_path, barcode, image_type, ','.join(
                image_paths)
            detail_id = db.save_visit_detail_info(visit_id, category_id, product_id, barcode, image_type,
                                                  image_list)
        except Exception as e:
            print('记录访问详情时出现异常: {}'.format(str(e)))
            result['result'] = -1
            result['msg'] = '传入参数有误'

            # 存储访问结果
            visit_result = result['result']
            db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        # 存储图片详情
        for image_path in image_paths:
            image_name = os.path.split(image_path)[-1]
            # 存储图片详情
            db.save_image_detail_info(detail_id, upload_path, image_name)

        if len(image_paths) == 0:
            print('识别出现异常: 上传图片失败')
            result['result'] = -1
            result['msg'] = '上传图片失败'

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')

            # 存储访问结果
            visit_result = result['result']
            db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))

            return dumps(result, ensure_ascii=False)

        print('接收到图片量: {}'.format(len(image_paths)))

        product_dict = {}
        product_dict['品类编码'] = classify_code
        product_dict['品类名称'] = CLASSIFY_MAPPING[classify_code]
        product_dict['商品编码'] = tmp_path

        # 整体信息汇总
        image_list = [item.replace(UPLOAD_PATH, LOCAL_PATH) for item in image_paths]

        if classify_code in ['101','102','103','104','106','112','114','117','121','125','126','127',
                               '128','129','130','131','133','134','139','148','149','159','160','161','162','189','191','194','196',
                               '217','138','218','223','230','232','235','295','299','315', '316', '323', '325', '326', '327', '328','342',
                               '429','492','507','510','821','827']:
            # 2022-07-06 进行了品类更新: 去除了137品类, 新增了217品类
            base64strs = []

            payload = {
                "cat": classify_code,
                "adid": product_name,
                "base64strs": json.dumps(base64strs),
                "imageList": json.dumps(image_list),
                "barCode": barcode,
                "writeTime": du.get_current_time()
            }

            response = requests.post(url='%s' % (other_url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            result = json.loads(response.text)

            # 存储访问结果
            visit_result = result['result']
            db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))

            if visit_result == 0:
                result['data']['recordID'] = visit_id
                # print(result)

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')

            return dumps(result, ensure_ascii=False)
        else:
            # 需要修改
            detail_list = []
            data = {}
            msg = '当前的商品不支持'
            result_code = -1

        result['data'] = data
        result['detail'] = detail_list
        result['result'] = result_code
        result['msg'] = msg

        # 存储访问结果
        visit_result = result['result']
        db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))
    else:
        result['data'] = []
        result['detail'] = {}
        result['result'] = -2
        result['msg'] = '请使用POST提交'

    end = time.time()
    print('本次识别结束,耗时: {} s'.format(end - start))
    print('--------------------------------')

    return dumps(result, ensure_ascii=False)

@app.route('/review_product_info', methods=['GET', 'POST'])
def receive_review_data():
    '''
    2022-07-06新增接口: 获取审核数据接口
    :return:
    '''
    result = {}
    start = time.time()

    if request.method == "POST":
        # 存储上传的图片
        visit_id = request.form.get('recordID')
        category_id = request.form.get('categoryID')
        product_id = request.form.get('adid')
        barcode = request.form.get('barCode')
        is_update = request.form.get('isUpdate')
        brand1 = request.form.get('brand1')
        brand2 = request.form.get('brand2')
        capacitysum = request.form.get('capacitysum')
        capacityamount = request.form.get('capacityamount')
        commodityname = request.form.get('commodityname')
        info1 = request.form.get('info1')
        info2 = request.form.get('info2')
        info3 = request.form.get('info3')
        info4 = request.form.get('info4')
        info5 = request.form.get('info5')
        info6 = request.form.get('info6')
        info7 = request.form.get('info7')
        info8 = request.form.get('info8')
        info9 = request.form.get('info9')
        info10 = request.form.get('info10')
        info11 = request.form.get('info11')
        info12 = request.form.get('info12')
        info13 = request.form.get('info13')
        info14 = request.form.get('info14')
        info15 = request.form.get('info15')
        info16 = request.form.get('info16')
        info17 = request.form.get('info17')
        info18 = request.form.get('info18')
        info19 = request.form.get('info19')
        info20 = request.form.get('info20')

        # 查询传入的信息是否存在
        visit_info = db.get_data_info(visit_id)

        if visit_info <= 0:
            print('识别出现异常: 未识别到记录信息')
            result['result'] = -1
            result['msg'] = '识别出现异常: 未识别到记录信息'

            end = time.time()
            print('数据接收失败,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        # 存储审核详情
        try:
            review_id = db.save_review_result(visit_id, category_id, product_id, barcode, brand1, brand2, capacitysum, capacityamount, commodityname, info1, info2, info3, info4, info5, info6, info7, info8, info9, info10, info11, info12, info13, info14, info15, info16, info17, info18, info19, info20, is_update)
            if review_id == None or review_id <= 0:
                raise Exception('接收失败, 存储审核信息出现异常')
        except Exception as e:
            print('记录审核详情时出现异常: {}'.format(str(e)))
            result['result'] = -1
            result['msg'] = '接收异常, 处理出现异常'

            end = time.time()
            print('本次接收结束,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        result['result'] = 1
        result['msg'] = '接收成功'
    else:
        result['result'] = 0
        result['msg'] = '接收失败,请使用POST提交'

    end = time.time()
    print('本次接收结束,耗时: {} s'.format(end - start))
    print('--------------------------------')

    return dumps(result, ensure_ascii=False)

if __name__ == '__main__':
    print('server startup, please open link {}'.format('http://{}:{}/process_image'.format(IP, PORT)))
    du = DateUtils()
    db = DBUtils()
    gs1 = GS1Utils()

    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()

    #http_server = HTTPServer(WSGIContainer(app))
    #http_server.listen(PORT)
    #IOLoop.instance().start()
