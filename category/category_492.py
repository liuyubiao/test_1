#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: Liuyb
@license: Apache Licence
@software: PyCharm
@file: category_492.py
@time: 2022-06-05 17:44
@description: 针对3342-杀虫驱蚊剂进行处理
"""
import re
import requests
import json
from collections import Counter

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
    brand_list, weight_list, product_name_list, type_list, add_package_list, length_list, package_num_list, bag_use_list, wrap_use_list, is_thick_list, package_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['产品类型'], product_dict['有无补充装'], product_dict['长度'], product_dict['单多包装'], product_dict['保鲜袋提取方法'], product_dict['保鲜膜提取方法'], product_dict['是否加厚'], product_dict['包装']
    # 去重
    brand_list, weight_list, product_name_list, type_list, add_package_list, length_list, package_num_list, bag_use_list, wrap_use_list, is_thick_list, package_list = remove_format(brand_list), remove_format(weight_list), remove_format(product_name_list), remove_format(type_list), remove_format(add_package_list), remove_format(length_list), remove_format(package_num_list), remove_format(bag_use_list), remove_format(wrap_use_list), remove_format(is_thick_list), remove_format(package_list)

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

    # 产品类型, 有无补充装, 长度, 单多包装, 保鲜袋提取方法, 保鲜膜提取方法, 是否加厚, 包装
    # 产品类型
    type = type_deal(type_list)
    # 有无补充装
    add_package = add_package_deal(add_package_list)
    # 长度
    length = length_deal(length_list, type)
    # 单多包装
    package_num = package_num_deal(package_num_list)
    # 保鲜袋提取方法, 保鲜膜提取方法
    if type == '保鲜袋':
        # 保鲜袋提取方法
        bag_use = bag_use_deal(bag_use_list)
        # 保鲜膜提取方法
        wrap_use = '不分（不属于上述选项的）'
    else:
        bag_use = '不分（不属于上述选项的）'
        # 保鲜膜提取方法
        wrap_use = wrap_use_deal(wrap_use_list)
    # 是否加厚
    is_thick = is_thick_deal(is_thick_list)
    # 包装类型
    package = package_deal(image_path_list)

    # 商品全称二次处理
    if product_name == '不分':
        # 使用 提取方法+类型 拼接出商品全称
        type_name = type
        if type == '保鲜袋':
            if bag_use != '不分（不属于上述选项的）':
                item_bag_use = ''
                if bag_use.find('点断式') >= 0:
                    item_bag_use = '点断式'
                elif bag_use.find('抽取式') >= 0:
                    item_bag_use = '抽取式'
                product_name = item_bag_use + type_name
            else:
                product_name = type_name
        else:
            if wrap_use != '不分（不属于上述选项的）':
                item_wrap_use = ''
                if wrap_use.find('点断式') >= 0:
                    item_wrap_use = '点断式'
                elif wrap_use.find('切割式') >= 0:
                    item_wrap_use = '切割式'
                product_name = item_wrap_use + type_name
            else:
                product_name = type_name

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'], product_dict['商品编码'], brand1, brand2, weight_num, weight, product_name, type, add_package, length, package_num, bag_use, wrap_use, is_thick, package)
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
        if item_weight.find('x') >= 0 or item_weight.find('*') >= 0 or item_weight.find('×') >= 0 or item_weight.find(
                '+') >= 0:
            tmp_weight_list.append(item_weight)
            break
    if len(tmp_weight_list) > 0:
        weight_num = max(tmp_weight_list, key=len)

        # 在实际测试过程中, 实际会抽出多个数据来，目前处理（先分割+，再分别计算各个段中的数值）
        item_list = re.split('\+', weight_num)
        if len(item_list) > 0:
            total = 0
            unit_name = ''
            for item_index, item in enumerate(item_list):
                if item.find('x') >= 0 or item.find('*') >= 0 or item.find('X') >= 0 or item.find('×') >= 0:
                    infos = re.split('x|\*|X|×', item)
                    # 获取单位
                    single_weight = infos[0]
                    single_weight_num = re.findall(num_pattern, single_weight)[0]
                    signal_weight_unit = single_weight.replace(str(single_weight_num), '')

                    item_total = 0
                    for item_info in infos:
                        if item_info == single_weight:
                            item_total = int(single_weight_num)
                            continue
                        try:
                            item_num = re.findall(num_pattern, item_info)[0]
                            if item_num == '':
                                continue
                            item_total *= int(item_num)
                        except Exception as e:
                            pass
                    total += item_total
                    if item_index == 0:
                        unit_name = signal_weight_unit
                else:
                    single_weight_num = re.findall(num_pattern, item)[0]
                    signal_weight_unit = item.replace(str(single_weight_num), '')
                    if item_index == 0:
                        unit_name = signal_weight_unit
                    total += int(single_weight_num)
            weight = '{}{}'.format(total, unit_name)
        else:
            infos = re.split('x|\*|X|×', weight_num)
            # 获取单位
            single_weight = infos[0]
            single_weight_num = re.findall(num_pattern, single_weight)[0]
            signal_weight_unit = single_weight.replace(str(single_weight_num), '')

            total = 0
            for item in infos:
                if item == single_weight:
                    total = int(single_weight_num)
                    continue
                try:
                    item_num = re.findall(num_pattern, item)[0]
                    if item_num == '':
                        continue
                    total *= int(item_num)
                except Exception as e:
                    pass

            if signal_weight_unit == '个' or signal_weight_unit == '卷' or signal_weight_unit == '只':
                weight = '{}{}'.format(total, signal_weight_unit)
    else:
        data_list = [item.lower() for item in data_list if item.find('/') < 0 or item.find('%') < 0]
        if len(data_list) > 0:
            weight = max(data_list, key=len)

    # 判断最终结果中是否含有中文
    zh_list = re.findall(zh_pattern, weight)
    if len(zh_list) == 0:
        weight = '1卷'
    return weight_num, weight

def weight_deal(weight_list):
    '''
    重容量
    :param weight_list:
    :return:
    '''
    rule_weight_list, uie_weight_list = weight_list[0], weight_list[1]

    weight = '1卷'
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

def type_deal(type_list):
    '''
    类型
    :param type_list:
    :return:
    '''
    type = '保鲜袋'

    rule_sub_type_list = type_list[0]
    if len(rule_sub_type_list) > 0:
        type = rule_sub_type_list[0]
    return type

def add_package_deal(add_package_list):
    '''
    有无补充装
    :param add_package_list:
    :return:
    '''
    rule_add_package_list = add_package_list[0]

    add_package = '不分'
    if len(rule_add_package_list) > 0:
        add_package = '有补充装'
    return add_package

def length_deal(length_list, type):
    '''
    长度(暂时不区分保鲜膜和保鲜袋)
    :param length_list:
    :param type:
    :return:
    '''
    length = '不分'
    rule_length_list = length_list[0]
    try:
        length = max(rule_length_list,key=len)
    except Exception as e:
        pass

    return length

def package_num_deal(package_num_list):
    '''
    单多包装
    :param package_num_list:
    :return:
    '''
    package_num = '单包'

    rule_package_num_list= package_num_list[0]
    if len(rule_package_num_list) > 0:
        package_num = '多包'
    return package_num

def bag_use_deal(bag_use_list):
    '''
    保鲜袋提取方法
    :param bag_use_list:
    :return:
    '''
    bag_use = '不分（不属于上述选项的）'
    rule_bag_use_list = bag_use_list[0]

    if len(rule_bag_use_list) > 0:
        bag_use = rule_bag_use_list[0]
        for item in rule_bag_use_list:
            if item.find('抽取式') >= 0:
                bag_use = item
                break
        if bag_use.find('，') < 0:
            bag_use = bag_use + '，普通'
    return bag_use

def wrap_use_deal(wrap_use_list):
    '''
    保鲜膜提取方法
    :param wrap_use_list:
    :return:
    '''
    wrap_use = '不分（不属于上述选项的）'
    rule_wrap_use_list = wrap_use_list[0]

    if len(rule_wrap_use_list) > 0:
        wrap_use = max(rule_wrap_use_list,key=len)

        if wrap_use.find('，') < 0:
            wrap_use = wrap_use + '，普通'
    return wrap_use

def is_thick_deal(is_thick_list):
    '''
    是否加厚
    Args:
        is_thick_list:

    Returns:

    '''
    is_thick = '不分'

    rule_is_thick_list = is_thick_list[0]
    if len(rule_is_thick_list) > 0:
        is_thick = '加厚'
    return is_thick

## 包装类型
def package_deal_pre(package_list, image_path_list):
    '''
    包装类型
    :param package_list:
    :param image_path_list:
    :return:
    '''
    package = '卷筒'
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

def get_url_result(imageList,url,category_id="492"):
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
    package_type = '卷筒'

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

    result_type_list = [[], []]
    result_add_package_list = [[], []]
    result_length_list = [[], []]
    result_package_num_list = [[], []]
    result_bag_use_list = [[], []]
    result_wrap_use_list = [[], []]
    result_is_thick_list = [[], []]
    result_package_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        type_list, add_package_list, length_list, package_num_list, bag_use_list, wrap_use_list, is_thick_list, package_list = infos['info1'], infos['info2'], infos['info3'], infos['info4'], infos['info5'], infos['info6'], infos['info7'], infos['info8']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_type_list = type_list
            result_add_package_list = add_package_list
            result_length_list = length_list
            result_package_num_list = package_num_list
            result_bag_use_list = bag_use_list
            result_wrap_use_list = wrap_use_list
            result_is_thick_list = is_thick_list
            result_package_list = package_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]), product_name.extend(product_name_list[index]), type.extend(type_list[index]), add_package.extend(add_package_list[index]), length.extend(length_list[index]), package_num.extend(package_num_list[index]), bag_use.extend(bag_use_list[index]), wrap_use.extend(wrap_use_list[index]), is_thick.extend(is_thick_list[index]), package.extend(package_list[index])) for index, (brand, weight, product_name, type, add_package, length, package_num, bag_use, wrap_use, is_thick, package) in enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list, result_type_list, result_add_package_list, result_length_list, result_package_num_list, result_bag_use_list, result_wrap_use_list, result_is_thick_list, result_package_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['产品类型'] = result_type_list
    product_dict['有无补充装'] = result_add_package_list
    product_dict['长度'] = result_length_list
    product_dict['单多包装'] = result_package_num_list
    product_dict['保鲜袋提取方法'] = result_bag_use_list
    product_dict['保鲜膜提取方法'] = result_wrap_use_list
    product_dict['是否加厚'] = result_is_thick_list
    product_dict['包装'] = result_package_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass