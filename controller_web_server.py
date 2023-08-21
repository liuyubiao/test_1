#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/29 14:14
# @Author  : liuyb
# @Site    : 
# @File    : process_controller.py
# @Software: PyCharm
# @Description: 流程控制(根据返回结果修改最终的输出)

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

from importlib import import_module
from contstant import RULE_MAPPING, CLASSIFY_MAPPING
from utils.datetime_utils import DateUtils
# 2022-07-05 加入ip监控
from utils.db_utils import DBUtils

from flask import Flask, request, render_template
from flask_cors import CORS

app = Flask(__name__)
PORT = 80

CORS(app,  resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = "process"

UPLOAD_PATH = 'static/upload/'
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

IP = '127.0.0.1'

LOCAL_PATH = '/root/data/project/product_recognize_main/static/upload/'
# 进行OCR的识别服务链接
ocr_url = 'http://127.0.0.1:5032/ocrReocg3'
# zx做的品类
other_url = 'http://127.0.0.1:5031/all_category_text_rule'

@app.route('/')
def index():
    # return render_template('index.html')
    return render_template('test.html')

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

def get_title_list(classify_code):
    '''
    获取标题列表
    :param classify_code:
    :return:
    '''
    title_list = ['品类编码', '品类名称', '商品编码']
    title_alias_name = ['brand1', 'brand2', 'capacityamount', 'capacitysum', 'commodityname']
    limit = 20
    title_other_name = ['info' + str(item+1) for item in range(limit)]
    title_alias_name.extend(title_other_name)

    current_classify_mapping = RULE_MAPPING[classify_code]
    classify_keys = current_classify_mapping.keys()
    title_extend_list = []
    title_real_alias_list = []

    for item in title_alias_name:
        if item in classify_keys:
            title_extend_list.append(current_classify_mapping[item])
            title_real_alias_list.append(item)

    title_list.extend(title_extend_list)
    return title_list, title_real_alias_list

@app.route('/process_image', methods=['GET', 'POST'])
def inference():
    result = {}
    start = time.time()

    if request.method == "POST":
        image_paths = []

        # 存储访问的数据
        try:
            visit_ip, visit_type = request.remote_addr, '0'
            visit_id = db.save_visit_record_info(visit_ip, visit_type)
        except Exception as e:
            print('记录访问ip时出现异常: {}'.format(str(e)))
            result['result'] = -1
            result['msg'] = '网络请求异常'

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')
            return dumps(result, ensure_ascii=False)

        classify_code = request.form.get('classify_code')
        product_name = request.form.get('product_name')
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

        for upload in request.files.getlist("file"):
            image_name = upload.filename.rsplit("/")[0]
            image_path = "/".join([upload_path, image_name])
            upload.save(image_path)

            image_paths.append(image_path)

        # 存储访问详情
        try:
            category_id, product_id, barcode, image_type, image_list = classify_code, tmp_path, '', '0', ','.join(
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

            # 存储访问结果
            visit_result = result['result']
            db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')

            return dumps(result, ensure_ascii=False)

        print('接收到图片量: {}'.format(len(image_paths)))

        product_dict = {}
        product_dict['品类编码'] = classify_code
        product_dict['品类名称'] = CLASSIFY_MAPPING[classify_code]
        product_dict['商品编码'] = tmp_path

        title_list, alias_title_list = get_title_list(classify_code)

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

            other_result = requests.post(url='%s' % (other_url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            other_json = json.loads(other_result.text)
            if other_json != None and other_json['result'] != 0:
                content = ''
            else:
                datas = other_json['data']
                # 针对datas数据进行整理
                content_list = [classify_code, CLASSIFY_MAPPING[classify_code], tmp_path]
                for item in alias_title_list:
                    content_list.append(datas[item])
                content = '\t'.join(content_list)
        else:
            content = '当前的商品不支持'

        content = content.replace('\n','')
        content_list = content.split('\t')

        data_info = {}
        data_info['contents'] = content_list
        data_info['titles'] = title_list
        data_info['images'] = image_paths
        data_info['product_name'] = tmp_path

        result['data'] = data_info
        result['result'] = 0
        result['msg'] = '识别成功'

        # 存储访问结果
        visit_result = result['result']
        db.save_visit_result_info(visit_id, visit_result, dumps(result, ensure_ascii=False))
    else:
        result['result'] = -2
        result['msg'] = '请使用POST提交'

    end = time.time()
    print('本次识别结束,耗时: {} s'.format(end - start))
    print('--------------------------------')

    return dumps(result, ensure_ascii=False)

if __name__ == '__main__':
    print('server startup, please open link {}'.format('http://{}'.format(IP, PORT)))
    du = DateUtils()
    db = DBUtils()

    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()
