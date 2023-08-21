#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: Liuyb 
@license: Apache Licence  
@software: PyCharm 
@file: category_137.py
@time: 2022-06-05 17:44 
@description: 针对137-方便食品进行处理
"""
import re
import requests
import json
from collections import Counter

import uuid

# 包装类型分类服务链接
package_type_url = 'http://127.0.0.1:5015/yourget_opn_classify'
# 图像检索
image_search_url = 'http://127.0.0.1:5013/product_info_search'
# 中文匹配
zh_pattern = re.compile(u'[\u4e00-\u9fa5]')

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
    brand_list, weight_list, product_name_list, water_package_list,save_list,location_list,ingredient_list,series_list,sub_type_list,type_list,taste_list,hot_list,package_list,weight_detail_list,health_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['水包重量'],product_dict['储藏方式'],product_dict['地方风味'],product_dict['配料'],product_dict['系列'],product_dict['子类'],product_dict['类型'],product_dict['口味'],product_dict['加热方式'],product_dict['包装'],product_dict['重量细分'],product_dict['健康概念']
    # 去重
    brand_list, weight_list, product_name_list, water_package_list,save_list,location_list,ingredient_list,series_list,sub_type_list,type_list,taste_list,hot_list,package_list,weight_detail_list,health_list = remove_format(brand_list), remove_format(weight_list),remove_format(product_name_list),remove_format(water_package_list),remove_format(save_list),remove_format(location_list),remove_format(ingredient_list),remove_format(series_list),remove_format(sub_type_list),remove_format(type_list),remove_format(taste_list),remove_format(hot_list),remove_format(package_list),remove_format(weight_detail_list),remove_format(health_list)

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

    # 水包重量
    water_package = weight_deal(water_package_list)[0]
    # 系列
    series = series_deal(series_list)
    # 子类/类型
    type, sub_type = type_sub_deal(type_list, sub_type_list, product_name)
    # 口味
    taste = taste_deal(taste_list)
    # 加热方式
    hot = hot_deal(hot_list)
    # 包装形式
    package = package_deal(package_list, image_path_list)
    # 重量细分
    weight_detail = weight_detail_deal(weight_detail_list)
    # 健康概念
    health = health_deal(health_list)
    # 储藏方式
    save = save_deal(save_list)
    # 地方风味
    location = location_deal(location_list)
    # 配料
    ingredient = ingredient_deal(ingredient_list)

    # 商品全称二次处理
    if product_name == '不分':
        # 使用 口味+类型 拼接出商品全称
        type_name = type
        if type_name.find('其他') >= 0:
            type_name = type.replace('其他','')

        if taste != '不分':
            product_name = '{}{}'.format(taste, type_name)
        else:
            if brand1 != '不分':
                product_name = '{}{}'.format(brand1, type_name)
            else:
                product_name = type_name

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'],
                                                                    product_dict['商品编码'], brand1, brand2, weight_num,
                                                                    weight, product_name, water_package, series, sub_type, type,taste,hot,package,weight_detail,health,save, location, ingredient)
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

def type_sub_deal(type_list, sub_type_list, product_name):
    '''
    类型-子类型
    Args:
        type_list:
        sub_type_list:
        product_name:

    Returns:

    '''
    type = '螺狮粉'
    sub_type = '粉类'

    rule_type_list, rule_sub_type_list = type_list[0], sub_type_list[0]

    if len(rule_sub_type_list) > 0:
        type = rule_type_list[0]
        sub_type = rule_sub_type_list[0]

    if type == '不分' or sub_type == '不分':
        if product_name.find('饭') >= 0:
            type = '其他饭'
            sub_type = '饭类'
        elif product_name.find('粉') >= 0:
            type = '其他粉'
            sub_type = '粉类'
        elif product_name.find('锅') >= 0:
            type = '其他火锅'
            sub_type = '火锅'
        elif product_name.find('面') >= 0:
            type = '其他面食'
            sub_type = '面类'

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

def hot_deal(hot_list):
    '''
    加热方式
    :param hot_list:
    :return:
    '''
    rule_hot_list, uie_hot_list = hot_list[0], hot_list[1]
    hot = '自热'

    if len(rule_hot_list) > 0:
        hot = '、'.join(rule_hot_list)
    else:
        if len(uie_hot_list) > 0:
            hot = '、'.join(uie_hot_list)
    return hot

## 包装类型
def package_deal(package_list, image_path_list):
    '''
    包装类型
    :param package_list:
    :param image_path_list:
    :return:
    '''
    package = '塑料盒'
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
    return  package

def weight_detail_deal(weight_detail_list):
    '''
    重量细分
    :param weight_detail_list:
    :return:
    '''
    rule_weight_detail_list, uie_weight_detail_list = weight_detail_list[0], weight_detail_list[1]
    weight_detail = ''

    if len(rule_weight_detail_list) > 0:
        weight_detail = max(rule_weight_detail_list, key=len)
    else:
        if len(uie_weight_detail_list) > 0:
            weight_detail = max(uie_weight_detail_list, key=len)
    return weight_detail

def health_deal(health_list):
    '''
    健康概念
    :param health_list:
    :return:
    '''
    rule_health_list, uie_health_list = health_list[0], health_list[1]
    health = ''

    if len(rule_health_list) > 0:
        health = max(rule_health_list, key=len)
    else:
        if len(uie_health_list) > 0:
            health = max(uie_health_list, key=len)
    return health

def save_deal(save_list):
    '''
    储存条件
    :param save_list:
    :return:
    '''
    rule_save_list, uie_save_list = save_list[0], save_list[1]
    save = ''

    if len(rule_save_list) > 0:
        save = max(rule_save_list, key=len)
    else:
        if len(uie_save_list) > 0:
            save = max(uie_save_list, key=len)
            if save.find('阴凉') >= 0 or save.find('干燥') >= 0 or save.find('密闭') >= 0:
                save = ''
    # 最后判定一下
    if save.find('常温') < 0 and save.find('冷藏') < 0:
        save = ''

    return save

def location_deal(localation_list):
    '''
    地方风味
    :param localation_list:
    :return:
    '''
    rule_localation_list, uie_localation_list = localation_list[0], localation_list[1]
    location = ''

    if len(rule_localation_list) > 0:
        location = max(rule_localation_list, key=len)
    else:
        if len(uie_localation_list) > 0:
            location = max(uie_localation_list, key=len)
    return location

def ingredient_deal(ingredient_list):
    '''
    配料
    :param ingredient_list:
    :return:
    '''
    rule_ingredient_list, uie_ingredient_list = ingredient_list[0], ingredient_list[1]
    ingredient = ''

    if len(rule_ingredient_list) > 0:
        ingredient = max(rule_ingredient_list, key=len)
    else:
        if len(uie_ingredient_list) > 0:
            ingredient = max(uie_ingredient_list, key=len)
    return ingredient

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

    result_water_package_list = [[], []]
    result_save_list = [[], []]
    result_location_list = [[], []]
    result_ingredient_list = [[], []]
    result_series_list = [[], []]
    result_sub_type_list = [[], []]
    result_type_list = [[], []]
    result_taste_list = [[], []]
    result_hot_list = [[], []]
    result_package_list = [[], []]
    result_weight_detail_list = [[], []]
    result_health_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        water_package_list,series_list,sub_type_list,type_list,taste_list,hot_list,package_list,weight_detail_list,health_list,save_list,location_list,ingredient_list = infos['info1'], infos['info2'],infos['info3'], infos['info4'],infos['info5'], infos['info6'],infos['info7'], infos['info8'],infos['info9'], infos['info10'],infos['info11'], infos['info12']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_water_package_list = water_package_list
            result_series_list = series_list
            result_sub_type_list = sub_type_list
            result_type_list = type_list
            result_taste_list = taste_list
            result_hot_list = hot_list
            result_package_list = package_list
            result_weight_detail_list = weight_detail_list
            result_health_list = health_list
            result_save_list = save_list
            result_location_list = location_list
            result_ingredient_list = ingredient_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]),product_name.extend(product_name_list[index]),
              water_package.extend(water_package_list[index]), series.extend(series_list[index]), sub_type.extend(sub_type_list[index]), type.extend(type_list[index]),
              taste.extend(taste_list[index]), hot.extend(hot_list[index]), package.extend(package_list[index]), weight_detail.extend(weight_detail_list[index]),
              health.extend(health_list[index]), save.extend(save_list[index]), location.extend(location_list[index]), ingredient.extend(ingredient_list[index])
              ) for
             index, (brand, weight, product_name,
                     water_package, series, sub_type, type,
                     taste, hot, package, weight_detail,
                     health, save, location, ingredient) in
             enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list,
                           result_water_package_list,result_series_list, result_sub_type_list, result_type_list,
                           result_taste_list,result_hot_list,result_package_list,result_weight_detail_list,
                           result_health_list,result_save_list,result_location_list,result_ingredient_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['水包重量'] = result_water_package_list
    product_dict['系列'] = result_series_list
    product_dict['子类'] = result_sub_type_list
    product_dict['类型'] = result_type_list
    product_dict['口味'] = result_taste_list
    product_dict['加热方式'] = result_hot_list
    product_dict['包装'] = result_package_list
    product_dict['重量细分'] = result_weight_detail_list
    product_dict['健康概念'] = result_health_list
    product_dict['储藏方式'] = result_save_list
    product_dict['地方风味'] = result_location_list
    product_dict['配料'] = result_ingredient_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass
