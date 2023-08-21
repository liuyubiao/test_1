#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: Liuyb
@license: Apache Licence
@software: PyCharm
@file: category_429.py
@time: 2022-06-05 17:44
@description: 针对429-卫生巾进行处理
"""
import re
import requests
import json

import uuid

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
    brand_list, weight_list, product_name_list, package_type_list, wings_num_list, net_list, wings_list, apply_time_list, thick_list, use_list, shape_list, length_list, effect_list, package_detail_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['组合（混合）装/独立装'], product_dict['护垫个数'], product_dict['网面'], product_dict['长条/护翼/裤型'], product_dict['适用时间及长度'], product_dict['薄厚程度'], product_dict['使用感觉'], product_dict['特殊形状/透气型'], product_dict['巾身长度'], product_dict['功效'], product_dict['组合装信息']
    # 去重
    brand_list, weight_list, product_name_list, package_type_list, wings_num_list, net_list, wings_list, apply_time_list, thick_list, use_list, shape_list, length_list, effect_list, package_detail_list = remove_format(brand_list), remove_format(weight_list), remove_format(product_name_list), remove_format(package_type_list), remove_format(wings_num_list), remove_format(net_list), remove_format(wings_list), remove_format(apply_time_list), remove_format(thick_list), remove_format(use_list), remove_format(shape_list), remove_format(length_list), remove_format(effect_list), remove_format(package_detail_list)

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

    # 组合（混合）装/独立装,护垫个数,网面,长条/护翼/裤型,适用时间及长度,薄厚程度,使用感觉,特殊形状/透气型,巾身长度,功效,组合装信息
    # 组合（混合）装/独立装
    # package_type = package_type_deal(package_type_list)
    # 护垫个数
    wings_num = wings_num_deal(wings_num_list)
    # 网面
    net = net_deal(net_list)
    # 长条/护翼/裤型
    wings = wings_deal(wings_list)
    # 适用时间及长度
    apply_time = apply_time_deal(apply_time_list)
    # 薄厚程度
    thick = thick_deal(thick_list)
    # 使用感觉
    use = '不分'
    # 特殊形状/透气型
    shape = shape_deal(shape_list)
    # 巾身长度
    length = length_deal(length_list)
    # 功效
    effect = effect_deal(effect_list)
    # 组合装信息
    package_detail = package_detail_deal(package_detail_list)

    # 针对组合装类型进行二次处理
    package_type = package_type2_deal(wings_num, apply_time)

    # 商品全称二次处理
    if product_name == '不分':
        product_name = '卫生巾'

        # 使用 品牌+适用时间+'卫生巾' 拼接出商品全称
        if brand1 != '不分':
            if apply_time != '不分':
                product_name = brand1 + apply_time + product_name
            else:
                product_name = brand1 + product_name
        else:
            if apply_time != '不分':
                product_name = apply_time + product_name

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'], product_dict['商品编码'], brand1, brand2, weight_num, weight, product_name, package_type, wings_num, net, wings, apply_time, thick, use, shape, length, effect, package_detail)
    return content

# 分别处理各个字段
## 品牌
def get_brand(data_list):
    '''
    将品牌拆解为品牌1和品牌2
    :param data_list:
    :return:
    '''
    brand1 = '不分'
    brand2 = '不分'

    if len(data_list) == 1:
        brand1 = data_list[0]
        brand2 = '不分'
    else:
        if 'ABC' in data_list:
            data_list.remove('ABC')

        if len(data_list) == 1:
            brand1 = data_list[0]
            brand2 = '不分'
        elif len(data_list) > 1:
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
        package_weight_num = re.findall(num_pattern, package_weight)[0]

        if weight_num.find('+') >= 0:
            weight = '{}片'.format(int(single_weight_num) + int(package_weight_num))
        else:
            weight = '{}片'.format(int(single_weight_num) * int(package_weight_num))
    else:
        if len(data_list) > 0:
            weight = max(data_list, key=len)

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
        if len(product_name) < 4:
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

def package_type_deal(package_type_list):
    '''
    组合（混合）装/独立装
    Args:
        package_type_list:

    Returns:

    '''
    package_type = '独立装'
    rule_package_type_list = package_type_list[0]

    if len(rule_package_type_list) > 0:
        package_type = '组合（混合）装'
    return package_type

def package_type2_deal(wings_num, apply_time):
    '''
    组合装类型更新版本
    Args:
        wings_num:
        apply_time:

    Returns:

    '''
    package_type = '独立装'

    if wings_num != '无护垫' or (apply_time.find('日用') >= 0 and apply_time.find('夜用') >= 0):
        package_type = '组合（混合）装'
    return package_type

def wings_num_deal(wings_num_list):
    '''
    护垫个数
    Args:
        wings_num_list:

    Returns:

    '''
    wings_num = '无护垫'

    rule_wings_num_list = wings_num_list[0]
    if len(rule_wings_num_list) > 0:
        wings_num = rule_wings_num_list[0]
    return wings_num

def net_deal(net_list):
    '''
    网面
    Args:
        net_list:

    Returns:

    '''
    net = '不分'
    rule_net_list = net_list[0]

    if len(rule_net_list) > 0:
        net = '，'.join(rule_net_list)
    return net

def wings_deal(wings_list):
    '''
    长条/护翼/裤型
    :param wings_list:
    :return:
    '''
    wings = '护翼'

    rule_wings_list = wings_list[0]
    if len(rule_wings_list) > 0:
        wings = rule_wings_list[0]
    return wings

def apply_time_deal(apply_time_list):
    '''
    适用时间及长度
    Args:
        apply_time_list:

    Returns:

    '''
    apply_result = '不分'

    apply_time = '不分'
    apply_length = '不分'

    rule_apply_time_list, rule_apply_length_list = apply_time_list[0], apply_time_list[1]
    if len(rule_apply_time_list) > 0:
        if '日用' in rule_apply_time_list and '夜用' in rule_apply_time_list:
            apply_time = '日用+夜用'
        else:
            apply_time = max(rule_apply_time_list, key=len)

    if len(rule_apply_length_list) > 0:
        apply_length = rule_apply_length_list[0]

    if apply_time != '不分':
        if apply_length != '不分':
            apply_result = '{}，{}'.format(apply_time, apply_length)
        else:
            apply_result = apply_time
    else:
        if apply_length != '不分':
            apply_result = apply_length
    return apply_result

def thick_deal(thick_list):
    '''
    薄厚程度
    Args:
        thick_list:

    Returns:

    '''
    thick = '不分'

    rule_thick_list = thick_list[0]

    if len(rule_thick_list) > 0:
        thick = rule_thick_list[0]
    return thick

def shape_deal(shape_list):
    '''
    特殊形状/透气型
    Args:
        shape_list:

    Returns:

    '''
    shape = '不分'

    rule_shape_list = shape_list[0]

    if len(rule_shape_list) > 0:
        shape = '，'.join(rule_shape_list)
    return shape

def length_deal(length_list):
    '''
    巾身长度
    Args:
        length_list:

    Returns:

    '''
    length = '未注明'

    rule_length_list = length_list[0]
    if len(rule_length_list) > 0:
        length = rule_length_list[0]
    return length

def effect_deal(effect_list):
    '''
    功效
    Args:
        effect_list:

    Returns:

    '''
    effect = '不分'

    rule_effect_list = effect_list[0]
    if len(rule_effect_list) > 0:
        effect = rule_effect_list[0]
    return effect

def package_detail_deal(package_detail_list):
    '''
    组合装信息
    Args:
        package_detail_list:

    Returns:

    '''
    package_detail = '不分'

    rule_package_detail_list = package_detail_list[0]
    if len(rule_package_detail_list) > 0:
        package_detail = rule_package_detail_list[0]
    return package_detail

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

    result_package_type_list = [[], []]
    result_wings_num_list = [[], []]
    result_net_list = [[], []]
    result_wings_list = [[], []]
    result_apply_time_list = [[], []]
    result_thick_list = [[], []]
    result_use_list = [[], []]
    result_shape_list = [[], []]
    result_length_list = [[], []]
    result_effect_list = [[], []]
    result_package_detail_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        package_type_list, wings_num_list, net_list, wings_list, apply_time_list, thick_list, use_list, shape_list, length_list, effect_list, package_detail_list = infos['info1'], infos['info2'], infos['info3'], infos['info4'], infos['info5'], infos['info6'], infos['info7'], infos['info8'], infos['info9'], infos['info10'], infos['info11']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_package_type_list = package_type_list
            result_wings_num_list = wings_num_list
            result_net_list = net_list
            result_wings_list = wings_list
            result_apply_time_list = apply_time_list
            result_thick_list = thick_list
            result_use_list = use_list
            result_shape_list = shape_list
            result_length_list = length_list
            result_effect_list = effect_list
            result_package_detail_list = package_detail_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]), product_name.extend(product_name_list[index]), package_type.extend(package_type_list[index]), wings_num.extend(wings_num_list[index]), net.extend(net_list[index]), wings.extend(wings_list[index]), apply_time.extend(apply_time_list[index]), thick.extend(thick_list[index]), use.extend(use_list[index]), shape.extend(shape_list[index]), length.extend(length_list[index]), effect.extend(effect_list[index]), package_detail.extend(package_detail_list[index])) for index, (brand, weight, product_name, package_type, wings_num, net, wings, apply_time, thick, use, shape, length, effect, package_detail) in enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list, result_package_type_list, result_wings_num_list, result_net_list, result_wings_list, result_apply_time_list, result_thick_list, result_use_list, result_shape_list, result_length_list, result_effect_list, result_package_detail_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['组合（混合）装/独立装'] = result_package_type_list
    product_dict['护垫个数'] = result_wings_num_list
    product_dict['网面'] = result_net_list
    product_dict['长条/护翼/裤型'] = result_wings_list
    product_dict['适用时间及长度'] = result_apply_time_list
    product_dict['薄厚程度'] = result_thick_list
    product_dict['使用感觉'] = result_use_list
    product_dict['特殊形状/透气型'] = result_shape_list
    product_dict['巾身长度'] = result_length_list
    product_dict['功效'] = result_effect_list
    product_dict['组合装信息'] = result_package_detail_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass