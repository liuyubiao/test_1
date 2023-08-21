#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: Liuyb 
@license: Apache Licence  
@software: PyCharm 
@file: category_299.py 
@time: 2022-06-05 17:44 
@description: 针对126-海苔进行处理
"""
import re
import json
import requests
from collections import Counter

import base64
from PIL import Image
from io import BytesIO

import uuid

# 包装类型分类服务链接
package_type_url = 'http://127.0.0.1:5014/yourget_opn_classify'

# 使用模型组合出包装类型
url_material = 'http://127.0.0.1:5028/yourget_opn_classify'
url_shape = 'http://127.0.0.1:5029/yourget_opn_classify'

# 图像检索
image_search_url = 'http://127.0.0.1:5013/product_info_search'
# 中文匹配
zh_pattern = re.compile(u'[\u4e00-\u9fa5]')
# 提取数字规范
num_pattern = re.compile(r'\d+\.?\d*')

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
    brand_list, weight_list, product_name_list, taste_list, package_list, type_list,add_list,single_package_list, shape_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['口味'],product_dict['包装形式'],product_dict['类型'],product_dict['添加物'],product_dict['是否是独立包装'],product_dict['形状']
    # 去重
    brand_list, weight_list, product_name_list, taste_list, package_list, type_list,add_list,single_package_list, shape_list = remove_format(brand_list), remove_format(weight_list),remove_format(product_name_list),remove_format(taste_list),remove_format(package_list),remove_format(type_list),remove_format(add_list),remove_format(single_package_list),remove_format(shape_list)

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

    # 口味
    taste = taste_deal(taste_list)
    # 包装类型
    # package = package_deal(package_list, image_path_list)
    package = package_deal(image_path_list)
    # 类型
    # 形状
    type, shape = type_shape_deal(type_list, shape_list, product_name)
    # 添加物
    add = add_deal(add_list)
    # 是否独立包装
    single_package = '非独立包装'
    if weight_num != '不分':
        single_package = '独立包装'

    # 商品全称二次处理
    if product_name == '不分':
        # 使用口味+ 类型+ '海苔' 拼接出商品全称
        if shape != '不分':
            if shape == '卷':
                if taste != '不分':
                    product_name = '{}海苔卷'.format(taste)
                else:
                    if add != '不分':
                        infos = add.split('、')
                        if len(infos) > 1:
                            add_name = [item for item in infos if item.find('芝麻') < 0]
                            product_name = '{}海苔卷'.format(add_name[0])
                        elif len(infos) == 1:
                            product_name = '{}海苔卷'.format(infos[0])
                        else:
                            product_name = '海苔卷'
                    else:
                        product_name = '海苔卷'
            else:
                if shape == '片':
                    shape_name = ''
                else:
                    shape_name = shape

                if taste != '不分':
                    product_name = '{}{}海苔'.format(taste, shape_name)
                else:
                    if add != '不分':
                        infos = add.split('、')
                        if len(infos) > 1:
                            add_name = [item for item in infos if item.find('芝麻') < 0]
                            if len(add_name) > 0:
                                product_name = '{}{}海苔'.format(add_name[0],shape_name)
                            else:
                                product_name = '{}海苔'.format(shape_name)
                        elif len(infos) == 1:
                            product_name = '{}{}海苔'.format(infos[0],shape_name)
                        else:
                            product_name = '{}海苔'.format(shape_name)
                    else:
                        product_name = '{}海苔'.format(shape_name)
        else:
            if taste != '不分':
                product_name = '{}拌饭海苔'.format(taste)
            else:
                if add != '不分':
                    infos = add.split('、')
                    if len(infos) > 1:
                        add_name = [item for item in infos if item.find('芝麻') < 0]
                        product_name = '{}拌饭海苔'.format(add_name[0])
                    elif len(infos) == 1:
                        product_name = '{}拌饭海苔'.format(infos[0])
                    else:
                        product_name = '拌饭海苔'
                else:
                    product_name = '拌饭海苔'

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'],
                                                                    product_dict['商品编码'], brand1, brand2, weight_num,
                                                                    weight, product_name, taste, package, type, add, single_package, shape)
    return content

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
        infos = re.split('x|\*|X|×|\+', weight_num)
        single_weight, package_weight = infos[0], infos[1]
        single_weight_num = re.findall(num_pattern, single_weight)[0]
        signal_weight_unit = single_weight.replace(str(single_weight_num), '')

        package_weight_num = re.findall(num_pattern, package_weight)[0]

        if signal_weight_unit == 'kg' or signal_weight_unit == '千克':
            unit_name = '千克'
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('kg','千克')
            weight_num = '{}克*{}'.format(trans_weight_num, package_weight)
            if weight_num.find('+') >= 0:
                weight = '{}克'.format(str(round(trans_weight_num + float(package_weight_num),2)))
            else:
                weight = '{}克'.format(str(round(trans_weight_num * float(package_weight_num),2)))
        elif signal_weight_unit == 'g' or signal_weight_unit == '克':
            unit_name = '克'
            weight_num = weight_num.replace(signal_weight_unit, unit_name)
            if weight_num.find('+') >= 0:
                weight = '{}克'.format(round(float(single_weight_num) + float(package_weight_num),2))
            else:
                weight = '{}克'.format(round(float(single_weight_num) * float(package_weight_num),2))
    else:
        data_list = [item.lower() for item in data_list if item.find('/') < 0 or item.find('%') < 0]
        if len(data_list) > 0:
            weight = max(data_list, key=len)
            weight = weight.lower()

            if weight.find('kg') >= 0 or weight.find('千克') >= 0:
                weight_g = re.findall(num_pattern, weight)[0]
                weight = '{}克'.format(int(float(weight_g) * 1000))
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

    if len(rule_product_name_list) > 0:
        product_name = max(rule_product_name_list, key=len)
    else:
        if len(uie_product_name_list) > 0:
            product_name = max(uie_product_name_list, key=len)
            if len(product_name) < 4:
                product_name = '不分'
    return product_name

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

def package_deal_pre(package_list, image_path_list):
    '''
    包装类型分类
    :param package_list:
    :param image_path_list:
    :return:
    '''
    package_type = '铁罐（盒）（桶）'

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
        package_type = sort_result[0][0]
    return  package_type

def get_url_result_pre(imageList,url,category_id="126"):
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

def get_url_result(imageList,url,category_id="126"):
    package_list = []
    for imagePath in imageList:
        payload = {
            "data": imagePath
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

def package_deal(image_path_list):
    '''
    包装类型分类
    :param image_path_list:
    :return:
    '''
    package_type = '铁罐（盒）（桶）'

    # 获取材质
    material = get_url_result(image_path_list, url_material)
    # 获取形状
    shape = get_url_result(image_path_list, url_shape)
    package = material + shape

    if package != '':
        package_type = package
    return package_type

## 类型
def type_shape_deal(type_list, shape_list, product_name):
    '''
    类型和形状
    :param type_list:
    :param shape_list:
    :param product_name:
    :return:
    '''
    shape = '片'
    type = '纯即食海苔'

    rule_type_list, rule_shape_list = type_list[0], shape_list[0]

    if len(rule_shape_list) > 0:
        if '卷' in rule_shape_list:
            shape = '卷'
            type = '纯即食海苔'
        elif '非夹心' in rule_shape_list:
            shape = '非夹心'
            type = '多味即食海苔'
        elif '夹心' in rule_shape_list:
            shape = '夹心'
            type = '多味即食海苔'
    else:
        if product_name != '不分':
            if product_name.find('卷') >= 0:
                shape = '卷'
                type = '纯即食海苔'
            elif product_name.find('非夹心') >= 0:
                shape = '非夹心'
                type = '多味即食海苔'
            elif product_name.find('夹心') >= 0:
                shape = '夹心'
                type = '多味即食海苔'
            elif product_name.find('拌饭') >= 0:
                shape = '不分'
                type = '烹饪用烤/炒海苔'
    return type, shape

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
        add = '、'.join(rule_add_list)
    else:
        if len(uie_add_list) > 0:
            add = '、'.join(uie_add_list)
    return add


def deal_result_format(product_dict, result_list,image_path_list):
    '''
    将返回的结果进行格式化操作
    :param product_dict:
    :param result_list:
    :param image_path_list:
    :return:
    '''
    result_brand1_list = [[],[]]
    result_weight_num_list = [[],[]]
    result_product_name_list = [[],[]]

    result_taste_list = [[],[]]
    result_package_list = [[],[]]
    result_type_list = [[],[]]
    result_add_list = [[],[]]
    result_single_package_list = [[],[]]
    result_shape_list = [[],[]]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        taste_list, package_list, type_list,add_list,single_package_list, shape_list = infos['info1'], infos['info2'], infos['info3'], infos['info4'], infos['info5'], infos['info6']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_taste_list = taste_list
            result_package_list = package_list
            result_type_list = type_list
            result_add_list = add_list
            result_single_package_list = single_package_list
            result_shape_list = shape_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]), product_name.extend(product_name_list[index]), taste.extend(taste_list[index]), package.extend(package_list[index]), type.extend(type_list[index]), add.extend(add_list[index]), single_package.extend(single_package_list[index]), shape.extend(shape_list[index])) for index, (brand, weight, product_name, taste, package, type, add, single_package, shape) in
             enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list, result_taste_list, result_package_list, result_type_list, result_add_list,result_single_package_list, result_shape_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list
    product_dict['口味'] = result_taste_list
    product_dict['包装形式'] = result_package_list
    product_dict['类型'] = result_type_list
    product_dict['添加物'] = result_add_list
    product_dict['是否是独立包装'] = result_single_package_list
    product_dict['形状'] = result_shape_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    total_list = [[],[]]
    tmp1_list = [['原味'],['香蕉味']]

    total2_list = [[],[]]
    tmp2_list = [['伊利'],['君乐宝']]

    # 方法1
    # total_list[0].extend(tmp1_list[0])
    # total_list[1].extend(tmp1_list[1])
    # print(total_list)

    # 方法2
    # [(item1.extend(tmp1_list[index]),item2.extend(tmp2_list[index])) for index, (item1, item2) in enumerate(zip(total_list,total2_list))]
    # print(total_list)
    # print(total2_list)
