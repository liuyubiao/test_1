#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: Liuyb 
@license: Apache Licence  
@software: PyCharm 
@file: category_131.py
@time: 2022-06-05 17:44 
@description: 针对131-中式酱进行处理
"""
import re
import requests
import json
from collections import Counter

import base64
from PIL import Image
from io import BytesIO

import uuid

# 包装类型分类服务链接
package_type_url = 'http://127.0.0.1:5015/yourget_opn_classify'
# 使用模型组合出包装类型
url_material = 'http://127.0.0.1:5028/yourget_opn_classify'
url_shape = 'http://127.0.0.1:5029/yourget_opn_classify'
# 图像检索
image_search_url = 'http://127.0.0.1:5013/product_info_search'
# 中文匹配
zh_pattern = re.compile(u'[\u4e00-\u9fa5]')
# 子类和类型关联关系
TYPE_DICT = {'豆酱':['郫县豆酱', '大豆酱', '豆瓣酱', '黄豆酱', '蚕豆酱', '黄酱'],'面酱':['甜面酱','面酱'],'辣椒酱':['指天椒辣酱', '朝天椒辣酱', '黄辣椒酱', '蒜蓉辣酱', '鲜椒酱', '甜辣酱', '油辣椒', '剁椒酱', '辣椒酱', '辣味酱', '辣酱'],'复合调味酱':['香菇牛肉酱', '其它复合酱', '牛肉酱', '香菇酱', '拌饭酱', '拌面酱', '海鲜酱', '香其酱', '沙茶酱', '柱侯酱', '蒜蓉酱', '烧烤酱', '烤肉酱', '涂抹酱', '炸酱', '肉酱'],'其它酱':['韭菜花酱','虾酱']}

def remove_contain_str(input_list):
    '''
    去除列表中被其他元素包含的元素
    :param input_list:
    :return:
    '''
    src_list = input_list
    # 为了保证各个属性输出时的准确性，现在会对属性结果进行排序处理
    input_list.sort(key=len, reverse=True)
    tmp_out, filter_list = [], []
    for s in input_list:
        mask_list = [s in o for o in tmp_out]
        if not any(mask_list):  # any函数全部为false才返回false
            tmp_out.append(s)
        else:
            # 记录是因为那个元素的存在导致被过滤
            filter_list.append(s)

    # 对out进行排序
    out = [item for item in src_list if item in tmp_out]
    return out, filter_list

def single_remove_format(result_data_list):
    '''
    对单list集合去重格式化
    :param result_data_list:
    :return:
    '''
    result_data_list = [item.strip() for item in result_data_list]
    # 先按照出现次数排序之后再进行去重
    result_data_list = sorted(result_data_list, key=lambda x: result_data_list.count(x), reverse=True)
    # 这种去重方式会打乱顺序
    # tmp_data_list = list(set(result_data_list))
    tmp_data_list = sorted(set(result_data_list), key=result_data_list.index)

    if tmp_data_list == None or len(tmp_data_list) == 0:
        tmp_data_list = []
    else:
        # 针对包含的内容再进行细分，包含情况也需要排除
        tmp_data_list, _ = remove_contain_str(tmp_data_list)
    return tmp_data_list

def remove_format(result_data_list):
    '''
    去重格式化
    :param result_data_list:
    :return:
    '''
    rule_list,uie_list = result_data_list[0], result_data_list[1]
    rule_list,uie_list = single_remove_format(rule_list), single_remove_format(uie_list)
    result = [rule_list, uie_list]
    return result

def fromat_attribute(product_dict, image_path_list):
    '''
    格式化商品属性
    :param product_dict:
    :param image_path_list:
    :return:
    '''
    brand_list, weight_list, product_name_list, series_list, sub_type_list,type_list,taste_list,package_list,trans_list,add_list,no_add_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['系列'],product_dict['子类'],product_dict['类型'],product_dict['口味'],product_dict['包装形式'],product_dict['是否非转基因'],product_dict['添加物'],product_dict['不添加']
    # 去重
    brand_list, weight_list, product_name_list, series_list, sub_type_list,type_list,taste_list,package_list,trans_list,add_list,no_add_list = remove_format(brand_list), remove_format(weight_list),remove_format(product_name_list),remove_format(series_list),remove_format(sub_type_list),remove_format(type_list),remove_format(taste_list),remove_format(package_list),remove_format(trans_list),remove_format(add_list),remove_format(no_add_list)

    # 品牌
    brand1, brand2 = brand_deal(brand_list)
    # 重容量
    weight_num, weight = weight_deal(weight_list)
    # 商品全称
    product_name = product_name_deal(product_name_list)

    # 通用必要的属性为空时，即启动图像检索功能
    if brand1 == '不分' or weight == '不分':
        # 启用图像检索功能
        content = search_image_info(product_dict, image_path_list)
        if content != None and content != '':
            return content

    # 系列
    series = series_deal(series_list)
    # 类型-子类型
    type, sub_type = type_sub_deal(type_list, sub_type_list)
    # 口味
    taste = taste_deal(taste_list)
    # 包装形式
    # package = package_deal(package_list, image_path_list)
    package = package_deal(image_path_list)
    # 是否非转基因
    trans = trans_deal(trans_list)
    # 添加物
    add = add_deal(add_list)
    # 不添加
    no_add = no_add_deal(no_add_list)

    # 2022-06-12添加：商品全称二次处理
    if product_name == '不分':
        # 使用 口味+类型 拼接出商品全称
        if taste != '不分':
            if type != '不分':
                type_name = type
                if type_name.find('复合酱') >= 0:
                    type_name = '酱'
                product_name = '{}{}'.format(taste, type_name)
            else:
                product_name = '{}{}酱'.format(brand1, taste)
        else:
            if type != '不分':
                type_name = type
                if type_name.find('复合酱') >= 0:
                    type_name = '酱'
                product_name = '{}{}'.format(brand1,type_name)
            else:
                product_name = '{}调味酱'.format(brand1)


    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'],
                                                                    product_dict['商品编码'], brand1, brand2, weight_num,
                                                                    weight, product_name, series,sub_type,type,taste,package,trans,add,no_add)
    return content

# 分别处理各个字段
## 品牌
def get_brand(data_list):
    '''
    将品牌拆解为品牌1和品牌2
    :param data_list:
    :return:
    '''
    if len(data_list) == 1:
        brand1 = data_list[0]
        brand2 = '不分'
    else:
        brand1 = data_list[0]
        brand2 = data_list[1]
    return brand1, brand2

def brand_deal(brand_list):
    '''
    品牌
    :param brand_list:
    :return:
    '''
    brand1 = '不分'
    brand2 = '不分'
    rule_brand_list,uie_brand_list = brand_list[0], brand_list[1]

    if len(rule_brand_list) > 0:
        brand1, brand2 = get_brand(rule_brand_list)
    else:
        if len(uie_brand_list) > 0:
            brand1, brand2 = get_brand(uie_brand_list)
    return brand1, brand2

## 重容量
def get_weight(data_list):
    '''
    将重容量拆解为 重容量和重容量x数量
    :param data_list:
    :return:
    '''
    weight = '不分'
    weight_num = '不分'

    tmp_weight_list = []
    for item_weight in data_list:
        if item_weight.find('x') >= 0 or item_weight.find('*') >= 0 or item_weight.find('×') >= 0 or item_weight.find('+') >= 0:
            tmp_weight_list.append(item_weight)
            break
    if len(tmp_weight_list) > 0:
        weight_num = max(tmp_weight_list, key=len)
        weight_num = weight_num.lower()
        infos = re.split('x|\*|X|×|\+', weight_num)
        single_weight, package_weight = infos[0], infos[1]
        single_weight_num = re.findall("\d+\.?\d*", single_weight)[0]
        signal_weight_unit = single_weight.replace(str(single_weight_num), '')

        package_weight_num = re.findall("\d+\.?\d*", package_weight)[0]

        if signal_weight_unit == 'ml' or signal_weight_unit == 'm' or signal_weight_unit == '毫升':
            unit_name = '毫升'
            weight_num = weight_num.replace(signal_weight_unit, unit_name)
            weight = '{}毫升'.format(int(float(single_weight_num) * float(package_weight_num)))
        elif signal_weight_unit == 'l' or signal_weight_unit == '升':
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('l','升')
            weight_num = '{}毫升*{}'.format(trans_weight_num,package_weight)
            weight = '{}毫升'.format(str(int(trans_weight_num * float(package_weight_num))))
        elif signal_weight_unit == 'kg' or signal_weight_unit == '千克':
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('kg','千克')
            weight_num = '{}克*{}'.format(trans_weight_num, package_weight)
            weight = '{}克'.format(str(int(trans_weight_num * float(package_weight_num))))
        elif signal_weight_unit == 'g' or signal_weight_unit == '克':
            unit_name = '克'
            weight_num = weight_num.replace(signal_weight_unit, unit_name)
            weight = '{}克'.format(int(float(single_weight_num) * float(package_weight_num)))
    else:
        data_list = [item.lower() for item in data_list if item.find('/') < 0 or item.find('%') < 0]
        if len(data_list) > 0:
            weight = max(data_list, key=len)
            weight = weight.lower()

            if weight.find('ml') >= 0 or weight.find('m') >= 0 or weight.find('毫升') >= 0:
                weight = weight.replace('ml', '毫升').replace('m', '毫升')
                weight = weight[0:weight.find('升') + 1]
            elif weight.find('l') >= 0 or weight.find('升') >= 0:
                weight_g = re.findall("\d+\.?\d*", weight)[0]
                weight = '{}{}'.format(int(float(weight_g) * 1000), '毫升')
            elif weight.find('kg') >= 0 or weight.find('千克') >= 0:
                weight_g = re.findall("\d+\.?\d*", weight)[0]
                weight = '{}{}'.format(int(float(weight_g) * 1000), '克')
            elif weight.find('g') >= 0 or weight.find('克') >= 0:
                weight = weight.replace('g', '克')
                weight = weight[0:weight.find('克') + 1]

    # 判断最终结果中是否含有中文
    zh_list = re.findall(zh_pattern, weight)
    if len(zh_list) == 0:
        weight = '不分'

    return weight_num, weight

def weight_deal(weight_list):
    '''
    重容量
    :param weight_list:
    :return:
    '''
    rule_weight_list, uie_weight_list = weight_list[0], weight_list[1]

    weight = '不分'
    weight_num = '不分'
    if len(rule_weight_list) > 0:
        weight_num, weight = get_weight(rule_weight_list)
    else:
        if len(uie_weight_list) > 0:
            weight_num, weight = get_weight(uie_weight_list)
    return weight_num, weight

## 商品全称
def product_name_deal(product_name_list):
    '''
    商品全称
    :param product_name_list:
    :return:
    '''
    rule_product_name_list, uie_product_name_list = product_name_list[0], product_name_list[1]
    product_name = '不分'

    if len(uie_product_name_list) > 0:
        product_name = max(uie_product_name_list, key=len)
        if len(product_name) < 4 or product_name.find('酱') < 0:
            product_name = '不分'
    return product_name

def search_image_info(product_dict, image_list):
    '''
    启用图像检索得到图像信息
    :param product_dict:
    :param image_list:
    :return:
    '''
    content = ''
    classify_code = product_dict['品类编码']
    for image_path in image_list:
        item_result = requests.post(url='%s' % (image_search_url), data={'image_path': '%s' % (image_path)},
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        info = json.loads(item_result.text)
        if info['result'] != 0 :
            continue
        datas = info['data']
        item_classify_code = datas[0]

        if classify_code == item_classify_code:
            datas[2] = str(uuid.uuid1())
            content = '{}\n'.format('\t'.join(datas))
            break
    return content

def series_deal(series_list):
    '''
    系列
    :param series_list:
    :return:
    '''
    rule_series_list, uie_series_list = series_list[0], series_list[1]
    series = '不分'

    if len(rule_series_list) > 0:
        series = max(rule_series_list, key=len)
    else:
        if len(uie_series_list) > 0:
            series = max(uie_series_list, key=len)
    return series

def type_sub_deal(type_list, sub_type_list):
    '''
    类型-子类型
    :param type_list:
    :param sub_type_list:
    :return:
    '''
    rule_type_list, rule_sub_type_list = type_list[0], sub_type_list[0]

    type = '不分'
    sub_type = '不分'

    if len(rule_type_list) > 0:
        type = rule_type_list[0]

        # 使用字典进行关联
        for key, val in TYPE_DICT.items():
            if type in val:
                sub_type = key
                break
    else:
        if len(rule_sub_type_list) > 0:
            sub_type = rule_sub_type_list[0]
    return type, sub_type

## 口味
def taste_deal(taste_list):
    '''
    口味
    :param taste_list:
    :return:
    '''
    rule_taste_list, uie_taste_list = taste_list[0], taste_list[1]

    taste = '不分'
    if len(rule_taste_list) > 0:
        taste = '、'.join(rule_taste_list)
    else:
        if len(uie_taste_list) > 0:
            taste = '、'.join(uie_taste_list)
    return taste

## 包装类型
def package_deal_pre(package_list, image_path_list):
    '''
    包装类型
    :param package_list:
    :param image_path_list:
    :return:
    '''
    package = '塑料瓶，桶'
    # 开始调用包装类型分类模型
    total_package_list = package_list[0]
    for image_path in image_path_list:
        result = requests.post(url='%s' % (package_type_url), data={'imagePath': '%s' % (image_path)},
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        item_result = json.loads(result.text)
        if item_result['result'] == 0:
            label = item_result['label']
            if label != '其他':
                total_package_list.append(label)
    # 统计包装类型最多的标签
    if len(total_package_list) > 0:
        number = Counter(total_package_list)
        sort_result = number.most_common()
        package = sort_result[0][0]
    return package

def get_url_result_pre(imageList,url,category_id="131"):
    package_list = []
    for imagePath in imageList:
        img = Image.open(imagePath)
        if img.mode != "RGB":
            img = img.convert("RGB")
            output_buffer = BytesIO()
            img.save(output_buffer, format="png")
            byte_data = output_buffer.getvalue()
            base64_data = base64.b64encode(byte_data).decode('utf-8')
        else:
            f = open(imagePath, 'rb')
            base64_data = base64.b64encode(f.read())
        payload = {
            "model_id": category_id,
            "data": base64_data,
            "imagePath": imagePath
        }
        try:
            merge = requests.post(url='%s' % (url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            json_dict = json.loads(merge.text)
            if json_dict["result"] == 0:
                label = json_dict["label"]

                if label != "其他" and "电商" not in label and label != "不分":
                    package_list.append(label)
        except:
            pass

    package_list = single_remove_format(package_list)
    if len(package_list) > 0:
        package = package_list[0]
    else:
        package = ''
    return package

def get_url_result(imageList,url,category_id="131"):
    package_list = []
    for imagePath in imageList:
        payload = {
            "data": imagePath
        }
        try:
            merge = requests.post(url='%s' % (url), data=payload,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
            json_dict = json.loads(merge.text)
            if json_dict["result"] == 0:
                label = json_dict["label"]

                if label != "其他" and "电商" not in label and label != "不分":
                    package_list.append(label)
        except:
            pass

    package_list = single_remove_format(package_list)
    if len(package_list) > 0:
        package = package_list[0]
    else:
        package = ''
    return package

def package_deal(image_path_list):
    '''
    包装类型分类
    :param image_path_list:
    :return:
    '''
    package_type = '塑料瓶，桶'

    # 获取材质
    material = get_url_result(image_path_list, url_material)
    # 获取形状
    shape = get_url_result(image_path_list, url_shape)
    package = material + shape

    if package != '':
        package_type = package
    return package_type

## 转基因
def trans_deal(trans_list):
    '''
    转基因
    :param trans_list:
    :return:
    '''
    rule_trans_list, uie_trans_list = trans_list[0], trans_list[1]

    trans = '不分'
    if len(rule_trans_list) > 0:
        trans = rule_trans_list[0]
    return  trans

## 添加物
def add_deal(add_list):
    '''
    添加物
    :param add_list:
    :return:
    '''
    rule_add_list, uie_add_list = add_list[0], add_list[1]

    add = '不分'
    if len(rule_add_list) > 0:
        add = rule_add_list[0]
    else:
        if len(uie_add_list) > 0:
            add = max(uie_add_list, key=len)
    return  add

## 不添加
def no_add_deal(no_add_list):
    '''
    不添加
    :param no_add_list:
    :return:
    '''
    rule_no_add_list, uie_no_add_list = no_add_list[0], no_add_list[1]

    no_add = '不分'
    if len(rule_no_add_list) > 0:
        no_add = rule_no_add_list[0]
    else:
        if len(uie_no_add_list) > 0:
            no_add = max(uie_no_add_list, key=len)
    return  no_add

def deal_result_format(product_dict, result_list, image_path_list):
    '''
    将返回的结果进行格式化操作
    :param product_dict:
    :param result_list:
    :param image_path_list:
    :return:
    '''
    result_brand1_list = [[], []]
    result_weight_num_list = [[], []]
    result_product_name_list = [[], []]

    result_series_list = [[], []]
    result_sub_type_list = [[], []]
    result_type_list = [[], []]
    result_taste_list = [[], []]
    result_package_list = [[], []]
    result_trans_list = [[], []]
    result_add_list = [[], []]
    result_no_add_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        series_list, sub_type_list,type_list,taste_list,package_list,trans_list,add_list,no_add_list = infos['info1'], infos['info2'],infos['info3'], infos['info4'],infos['info5'], infos['info6'],infos['info7'],infos['info8']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_series_list = series_list
            result_sub_type_list = sub_type_list
            result_type_list = type_list
            result_taste_list = taste_list
            result_package_list = package_list
            result_trans_list = trans_list
            result_add_list = add_list
            result_no_add_list = no_add_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]),
              product_name.extend(product_name_list[index]), series.extend(series_list[index]),
              sub_type.extend(sub_type_list[index]), type.extend(type_list[index]), taste.extend(taste_list[index]),
              package.extend(package_list[index]), trans.extend(trans_list[index]), add.extend(add_list[index]), no_add.extend(no_add_list[index])) for
             index, (brand, weight, product_name, series, sub_type, type, taste, package, trans, add, no_add) in
             enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list, result_series_list,
                           result_sub_type_list, result_type_list, result_taste_list, result_package_list,
                           result_trans_list, result_add_list, result_no_add_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['系列'] = result_series_list
    product_dict['子类'] = result_sub_type_list
    product_dict['类型'] = result_type_list
    product_dict['口味'] = result_taste_list
    product_dict['包装形式'] = result_package_list
    product_dict['是否非转基因'] = result_trans_list
    product_dict['添加物'] = result_add_list
    product_dict['不添加'] = result_no_add_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass
