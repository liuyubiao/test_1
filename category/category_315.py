#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: Liuyb
@license: Apache Licence
@software: PyCharm
@file: category_159.py
@time: 2022-06-05 17:44
@description: 针对315-洗发水洗发膏进行处理
"""
import re
import requests
import json

import uuid

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
    brand_list, weight_list, product_name_list, anti_dandruff_list,merge_list,add_list,effect_list,apply_hair_list,apply_person_list,odor_list,oil_list = product_dict['品牌1'], product_dict['重容量x数量'], product_dict['商品全称'], product_dict['去头屑/非去头屑'],product_dict['几合一'],product_dict['含有物'],product_dict['功效'],product_dict['适用发质'],product_dict['适用人群'],product_dict['香型'],product_dict['有无硅油']
    # 去重
    brand_list, weight_list, product_name_list, anti_dandruff_list, merge_list, add_list, effect_list, apply_hair_list, apply_person_list, odor_list, oil_list = remove_format(brand_list), remove_format(weight_list),remove_format(product_name_list),remove_format(anti_dandruff_list),remove_format(merge_list),remove_format(add_list),remove_format(effect_list),remove_format(apply_hair_list),remove_format(apply_person_list),remove_format(odor_list),remove_format(oil_list)

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

    # 去头屑/非去头屑
    anti_dandruff = anti_dandruff_deal(anti_dandruff_list)
    # 几合一
    merge = merge_deal(merge_list)
    # 含有物
    add = add_deal(add_list)
    # 功效
    effect = effect_deal(effect_list)
    # 适用发质
    apply_hair = apply_hair_deal(apply_hair_list)
    # 适用人群
    apply_person = apply_person_deal(apply_person_list)
    # 香型
    odor = odor_deal(odor_list)
    # 有无硅油
    oil = oil_deal(oil_list)

    # 商品全称二次处理
    if product_name == '不分':
        # 使用 含有物+功效+是否去屑+洗发水 拼接出商品全称
        if anti_dandruff == '去头屑':
            anti_dandruff_name = '去屑'
        else:
            anti_dandruff_name = '不分'
        tmo_product_name = [add,effect,anti_dandruff_name,'洗发水']
        tmo_product_name = [item for item in tmo_product_name if item != '不分']
        product_name = ''.join(tmo_product_name)

    content = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_dict['品类编码'], product_dict['品类名称'],
                                                                    product_dict['商品编码'], brand1, brand2, weight_num,
                                                                    weight, product_name, anti_dandruff, merge, add, effect, apply_hair, apply_person, odor, oil)
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
            weight_num = '{}毫升x{}'.format(trans_weight_num,package_weight)
            weight = '{}毫升'.format(str(int(trans_weight_num * float(package_weight_num))))
        elif signal_weight_unit == 'kg' or signal_weight_unit == '千克':
            trans_weight_num = int(float(single_weight_num) * 1000)
            # weight_num = weight_num.replace('kg','千克')
            weight_num = '{}克x{}'.format(trans_weight_num, package_weight)
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

def anti_dandruff_deal(anti_dandruff_list):
    '''
    去头屑/非去头屑
    :param anti_dandruff_list:
    :return:
    '''
    anti_dandruff = '非去头屑'

    rule_anti_dandruff_list = anti_dandruff_list[0]
    if len(rule_anti_dandruff_list) > 0:
        anti_dandruff = '去头屑'
    return anti_dandruff

def merge_deal(merge_list):
    '''
    几合一
    :param merge_list:
    :return:
    '''
    merge = '非二合一'
    rule_merge_list = merge_list[0]
    if len(rule_merge_list) > 0:
        merge = max(rule_merge_list, key=len)
    return merge

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

def effect_deal(effect_list):
    '''
    功效
    :param effect_list:
    :return:
    '''
    effect = '不分'
    rule_effect_list, uie_effect_list = effect_list[0], effect_list[1]
    if len(rule_effect_list) > 0:
        effect = '、'.join(rule_effect_list)
    else:
        if len(uie_effect_list) > 0:
            effect = '、'.join(uie_effect_list)
    return effect

def apply_hair_deal(apply_hair_list):
    '''
    适用发质
    :param apply_hair_list:
    :return:
    '''
    apply_hair = '不分'
    rule_apply_hair_list, uie_apply_hair_list = apply_hair_list[0], apply_hair_list[1]
    if len(rule_apply_hair_list) > 0:
        apply_hair = max(rule_apply_hair_list, key=len)
    else:
        if len(uie_apply_hair_list) > 0:
            apply_hair = max(uie_apply_hair_list, key=len)
    return apply_hair

def apply_person_deal(apply_person_list):
    '''
    适用人群
    :param apply_person_list:
    :return:
    '''
    apply_person = '不分'
    rule_apply_person_list, uie_apply_person_list = apply_person_list[0], apply_person_list[1]
    if len(rule_apply_person_list) > 0:
        apply_person = max(rule_apply_person_list, key=len)
    else:
        if len(uie_apply_person_list) > 0:
            apply_person = max(uie_apply_person_list, key=len)
    return apply_person

def odor_deal(odor_list):
    '''
    香型
    :param odor_list:
    :return:
    '''
    rule_odor_list, uie_odor_list = odor_list[0], odor_list[1]

    odor = '不分'
    if len(rule_odor_list) > 0:
        odor = max(rule_odor_list, key=len)
    else:
        if len(uie_odor_list) > 0:
            odor = max(uie_odor_list, key=len)
    return odor

def oil_deal(oil_list):
    '''
    有无硅油
    :param oil_list:
    :return:
    '''
    oil = '不分'

    rule_oil_list = oil_list[0]

    if len(rule_oil_list) > 0:
        oil = '无硅油'
    return oil

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

    result_anti_dandruff_list = [[], []]
    result_merge_list = [[], []]
    result_add_list = [[], []]
    result_effect_list = [[], []]
    result_apply_hair_list = [[], []]
    result_apply_person_list = [[], []]
    result_odor_list = [[], []]
    result_oil_list = [[], []]

    for rule_index, rule_result in enumerate(result_list):
        # 将规则的结果汇总到uie结果中
        infos = rule_result['infos']
        anti_dandruff_list,merge_list,add_list,effect_list,apply_hair_list,apply_person_list,odor_list,oil_list = infos['info1'], infos['info2'],infos['info3'], infos['info4'],infos['info5'], infos['info6'],infos['info7'], infos['info8']
        brand_list, weight_list, product_name_list = infos['brand'], infos['weight'], infos['product']

        if rule_index == 0:
            result_brand1_list = brand_list
            result_weight_num_list = weight_list
            result_product_name_list = product_name_list

            result_anti_dandruff_list = anti_dandruff_list
            result_merge_list = merge_list
            result_add_list = add_list
            result_effect_list = effect_list
            result_apply_hair_list = apply_hair_list
            result_apply_person_list = apply_person_list
            result_odor_list = odor_list
            result_oil_list = oil_list
        else:
            [(brand.extend(brand_list[index]), weight.extend(weight_list[index]), product_name.extend(product_name_list[index]),
              anti_dandruff.extend(anti_dandruff_list[index]), merge.extend(merge_list[index]), add.extend(add_list[index]), effect.extend(effect_list[index]),
              apply_hair.extend(apply_hair_list[index]), apply_person.extend(apply_person_list[index]), odor.extend(odor_list[index]), oil.extend(oil_list[index])
              ) for
             index, (brand, weight, product_name,
                     anti_dandruff, merge, add, effect,
                     apply_hair, apply_person, odor, oil) in
             enumerate(zip(result_brand1_list, result_weight_num_list, result_product_name_list,
                           result_anti_dandruff_list, result_merge_list, result_add_list, result_effect_list,
                           result_apply_hair_list, result_apply_person_list, result_odor_list, result_oil_list))]

    product_dict['品牌1'] = result_brand1_list
    product_dict['重容量x数量'] = result_weight_num_list
    product_dict['商品全称'] = result_product_name_list

    product_dict['去头屑/非去头屑'] = result_anti_dandruff_list
    product_dict['几合一'] = result_merge_list
    product_dict['含有物'] = result_add_list
    product_dict['功效'] = result_effect_list
    product_dict['适用发质'] = result_apply_hair_list
    product_dict['适用人群'] = result_apply_person_list
    product_dict['香型'] = result_odor_list
    product_dict['有无硅油'] = result_oil_list

    # 将结果进行整体的整合处理
    content = fromat_attribute(product_dict, image_path_list)
    return content

if __name__ == "__main__":
    pass