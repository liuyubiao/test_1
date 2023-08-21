#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: Liuyb
@license: Apache Licence
@software: PyCharm
@file: category_507.py
@time: 2022-06-05 17:44
@description: 针对507-香辛料进行处理
"""
import re
import requests
import json
from collections import Counter

import base64
from PIL import Image
from io import BytesIO

import uuid

# 包装类型分类服务链接(目前默认先使用128的)
package_type_url = 'http://127.0.0.1:5016/yourget_opn_classify'
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
    brand_list, weight_list, product_name_list, ingredient_1_list, ingredient_2_list, type_list, taste_list, state_list, package_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['配料1'], product_dict['配料2'], product_dict['类型'], product_dict['口味'], product_dict['状态'], product_dict['包装类型']
    # 去重
    brand_list, weight_list, product_name_list, ingredient_1_list, ingredient_2_list, type_list, taste_list, state_list, package_list = remove_format(brand_list), remove_format(weight_list), remove_format(product_name_list), remove_format(ingredient_1_list), remove_format(ingredient_2_list), remove_format(type_list), remove_format(taste_list), remove_format(state_list), remove_format(package_list)

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

    # 配料（盐/糖/味精等调味料）,配料(除配料1以外的配料),类型,口味,状态,包装类型
    # 配料1
    ingredient_1 = ingredient_1_deal(ingredient_1_list)
    # 配料2
    ingredient_2 = ingredient_2_deal(ingredient_2_list)
    # 类型
    type = type_deal(type_list, product_name, ingredient_1, ingredient_2)
    # 口味
    taste = taste_deal(taste_list)
    # 状态
    state = state_deal(state_list)
    # 包装类型
    # package = package_deal(package_list, image_path_list)
    package = package_deal(image_path_list)

    # 商品全称二次处理
    if product_name == '不分':
        # 使用 口味+'粉' 拼接出商品全称
        taste_name = taste

        if taste_name != '不分':
            if taste_name.find('辣椒') >= 0:
                product_name = '辣椒面'
            else:
                infos = taste_name.split('、')
                taste_name = max(infos,key=len)
                product_name = taste_name

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'], product_dict['商品编码'], brand1, brand2, weight_num, weight, product_name, ingredient_1, ingredient_2, type, taste, state, package)
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

    data_list = [item.lower() for item in data_list if item.find('/') < 0 and item.find('%') < 0]

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
        single_weight_num = re.findall(num_pattern, single_weight)[0]
        signal_weight_unit = single_weight.replace(str(single_weight_num), '')

        package_weight_num = re.findall(num_pattern, package_weight)[0]

        if signal_weight_unit == 'ml' or signal_weight_unit == 'm' or signal_weight_unit == '毫升':
            unit_name = '毫升'
            weight_num = weight_num.replace(signal_weight_unit, unit_name)
            weight = '{}毫升'.format(round(float(single_weight_num) * float(package_weight_num),1))
        elif signal_weight_unit == 'l' or signal_weight_unit == '升':
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('l','升')
            weight_num = '{}毫升*{}'.format(trans_weight_num,package_weight)
            weight = '{}毫升'.format(str(round(trans_weight_num * float(package_weight_num),1)))
        elif signal_weight_unit == 'kg' or signal_weight_unit == '千克':
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('kg','千克')
            weight_num = '{}克*{}'.format(trans_weight_num, package_weight)
            weight = '{}克'.format(str(round(trans_weight_num * float(package_weight_num),1)))
        elif signal_weight_unit == 'g' or signal_weight_unit == '克':
            unit_name = '克'
            weight_num = weight_num.replace(signal_weight_unit, unit_name)
            weight = '{}克'.format(round(float(single_weight_num) * float(package_weight_num),1))
    else:
        if len(data_list) > 0:
            weight = max(data_list, key=len)
            weight = weight.lower()

            if weight.find('ml') >= 0 or weight.find('m') >= 0 or weight.find('毫升') >= 0:
                weight = weight.replace('ml', '毫升').replace('m', '毫升')
                weight = weight[0:weight.find('升') + 1]
            elif weight.find('l') >= 0 or weight.find('升') >= 0:
                weight_g = re.findall(num_pattern, weight)[0]
                weight = '{}{}'.format(int(float(weight_g) * 1000), '毫升')
            elif weight.find('kg') >= 0 or weight.find('千克') >= 0:
                weight_g = re.findall(num_pattern, weight)[0]
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

    if len(rule_product_name_list) > 0:
        product_name = max(rule_product_name_list, key=len)
    else:
        if len(uie_product_name_list) > 0:
            product_name = max(uie_product_name_list, key=len)
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

def ingredient_1_deal(ingredient_1_list):
    '''
    配料1
    Args:
        ingredient_1_list:

    Returns:

    '''
    ingredient_1 = '否'
    rule_ingredient_1_list, uie_ingredient_1_list = ingredient_1_list[0], ingredient_1_list[1]

    if len(rule_ingredient_1_list) > 0:
        ingredient_1 = '，'.join(rule_ingredient_1_list)
    else:
        if len(uie_ingredient_1_list) > 0:
            ingredient_1 = '，'.join(uie_ingredient_1_list)
    return ingredient_1

def ingredient_2_deal(ingredient_2_list):
    '''
    配料2
    Args:
        ingredient_2_list:

    Returns:

    '''
    ingredient_2 = '不分'
    rule_ingredient_2_list, uie_ingredient_2_list = ingredient_2_list[0], ingredient_2_list[1]

    if len(rule_ingredient_2_list) > 0:
        ingredient_2 = '，'.join(rule_ingredient_2_list)
    else:
        if len(uie_ingredient_2_list) > 0:
            ingredient_2 = '，'.join(uie_ingredient_2_list)
    return ingredient_2

def type_deal(type_list, product_name, ingredient_1, ingredient_2):
    '''
    类型
    Args:
        type_list:
        product_name:
        ingredient_1:
        ingredient_2:

    Returns:

    '''
    type = '单一香料'
    rule_sub_type_list = type_list[0]

    if product_name == '不分':
        if len(rule_sub_type_list) == 0:
            if ingredient_1 == '否':
                if ingredient_2 == '不分':
                    type = '单一香料'
                else:
                    infos = ingredient_2.split('，')
                    flag = False
                    for item in infos:
                        if product_name.find(item) >= 0:
                            flag = True
                            break
                    if len(infos) == 1 or flag:
                        type = '单一香料'
                    else:
                        type = '混合香料'
            else:
                type = '菜谱式调料'
        else:
            type = rule_sub_type_list[0]
    else:
        if product_name.find('五香') >= 0 or product_name.find('椒盐') >= 0 or product_name.find('卤') >= 0:
            type = '混合香辛料'
        elif product_name.find('蒸肉粉') >= 0 or product_name.find('烧烤') >= 0 or product_name.find('烤') >= 0:
            type = '菜谱式调料'
    return type

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

def state_deal(state_list):
    '''
    状态
    :param state_list:
    :return:
    '''
    state = '粉状'

    rule_length_list = state_list[0]
    if len(rule_length_list) > 0:
        state = rule_length_list[0]
    return state

## 包装类型
def package_deal_pre(package_list, image_path_list):
    '''
    包装类型
    :param package_list:
    :param image_path_list:
    :return:
    '''
    package = '塑料袋'
    # # 开始调用包装类型分类模型
    # total_package_list = package_list[0]
    # for image_path in image_path_list:
    #     result = requests.post(url='%s' % (package_type_url), data={'imagePath': '%s' % (image_path)},
    #                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
    #     item_result = json.loads(result.text)
    #     if item_result['result'] == 0:
    #         label = item_result['label']
    #         if label != '其他':
    #             total_package_list.append(label)
    # # 统计包装类型最多的标签
    # if len(total_package_list) > 0:
    #     number = Counter(total_package_list)
    #     sort_result = number.most_common()
    #     package = sort_result[0][0]
    return package

def get_url_result_pre(imageList,url,category_id="507"):
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

def get_url_result(imageList,url,category_id="507"):
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

def package_deal(image_path_list):
    '''
    包装类型分类
    :param image_path_list:
    :return:
    '''
    package_type = '塑料袋'

    # 获取材质
    material = get_url_result(image_path_list, url_material)
    # 获取形状
    shape = get_url_result(image_path_list, url_shape)
    package = material + shape

    if package != '':
        package_type = package
    return package_type

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

    result_ingredient_1_list = [[], []]
    result_ingredient_2_list = [[], []]
    result_type_list = [[], []]
    result_taste_list = [[], []]
    result_state_list = [[], []]
    result_package_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        ingredient_1_list, ingredient_2_list, type_list, taste_list, state_list, package_list = infos['info1'], infos['info2'], infos['info3'], infos['info4'], infos['info5'], infos['info6']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_ingredient_1_list = ingredient_1_list
            result_ingredient_2_list = ingredient_2_list
            result_type_list = type_list
            result_taste_list = taste_list
            result_state_list = state_list
            result_package_list = package_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]), product_name.extend(product_name_list[index]), ingredient_1.extend(ingredient_1_list[index]), ingredient_2.extend(ingredient_2_list[index]), type.extend(type_list[index]), taste.extend(taste_list[index]), state.extend(state_list[index]), package.extend(package_list[index])) for index, (brand, weight, product_name, ingredient_1, ingredient_2, type, taste, state, package) in enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list, result_ingredient_1_list, result_ingredient_2_list, result_type_list, result_taste_list, result_state_list, result_package_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['配料1'] = result_ingredient_1_list
    product_dict['配料2'] = result_ingredient_2_list
    product_dict['类型'] = result_type_list
    product_dict['口味'] = result_taste_list
    product_dict['状态'] = result_state_list
    product_dict['包装类型'] = result_package_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass