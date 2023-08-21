#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2022/7/12 10:16
# @Author  : liuyb
# @File    : db_settings.py
# @Describe: mysql数据库连接配置

import pymysql
# from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB
from pymysql.converters import escape_string


class Config(object):
    SALT = b"ictr-liuyb"
    SECRET_KEY = 'ictr-kwpo-product'

    MAX_CONTENT_LENGTH = 1024 * 1024 * 7

    POOL = PooledDB(
        creator=pymysql,  # 使用链接数据库的模块
        maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
        mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
        maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
        maxshared=3,
        # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
        blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
        maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
        setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
        ping=0,
        # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
        host='127.0.0.1',
        port=3306,
        user='root',
        password='1qaz@WSX',
        database='product',
        charset='utf8'
    )

class DBUtils(object):

    def __init__(self):
        self.config = Config()

    def connect(self):
        conn = Config.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self, cursor, conn):
        cursor.close()
        conn.close()

    def get_all_data(self, sql):
        '''
        执行多条查询sql
        :param sql:
        :return:
        '''
        conn, cursor = self.connect()

        result = None
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except Exception as ex:
            print(str(ex))
        self.connect_close(cursor, conn)
        return result

    def get_single_data(self, sql):
        '''
        执行单条查询sql
        :param sql:
        :return:
        '''
        conn, cursor = self.connect()
        result = None

        try:
            cursor.execute(sql)
            result = cursor.fetchone()
        except Exception as ex:
            print(str(ex))
        self.connect_close(cursor, conn)
        return result

    def exec_save(self, sql):
        '''
        执行存储sql
        :param sql:
        :return:
        '''
        conn, cursor = self.connect()
        insert_id = None

        try:
            cursor.execute(sql)
            insert_id = cursor.lastrowid
            conn.commit()
        except Exception as ex:
            print(str(ex))
        self.connect_close(cursor, conn)
        return insert_id

    def save_visit_record_info(self, visit_ip, visit_type):
        '''
        向访问记录表中存储数据
        :param visit_ip:
        :param visit_type:
        :return:
        '''
        sql = "INSERT INTO `product`.`visit_record_info` ( `visit_ip`, `visit_type` ) VALUES ( '{}', '{}' );".format(
            visit_ip, visit_type)
        insert_id = self.exec_save(sql)
        return insert_id

    def save_visit_detail_info(self, visit_id, category_id, product_id, barcode, image_type, image_list):
        '''
        向访问详情表中存储数据
        :param visit_id:
        :param category_id:
        :param product_id:
        :param barcode:
        :param image_type:
        :param image_list:
        :return:
        '''
        sql = "INSERT INTO `product`.`visit_detail_info` ( `visit_id`, `category_id`, `product_id`, `barcode`, `image_type`, `image_list`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(
            visit_id, category_id, product_id, barcode, image_type, image_list)
        insert_id = self.exec_save(sql)
        return insert_id

    def save_image_detail_info(self, detail_id, image_path, image_name):
        '''
        向图片详情表中存储数据
        :param detail_id:
        :param image_path:
        :param image_name:
        :return:
        '''
        sql = "INSERT INTO `product`.`image_detail_info` (`detail_id`, `image_path`, `image_name`) VALUES ('{}', '{}', '{}');".format(
            detail_id, image_path, image_name)
        insert_id = self.exec_save(sql)
        return insert_id

    def save_visit_result_info(self, visit_id, visit_result, visit_result_data):
        '''
        向结果表中存储数据
        :param visit_id:
        :param visit_result:
        :param visit_result_data:
        :return:
        '''
        visit_result_data = escape_string(visit_result_data)
        sql = "INSERT INTO `product`.`visit_result_info` (`visit_id`, `visit_result`, `visit_result_data`) VALUES ('{}', '{}', '{}');".format(
            visit_id, visit_result, visit_result_data)
        insert_id = self.exec_save(sql)
        return insert_id

    def get_data_info(self, visit_id):
        '''
        查询访问记录是否存在
        :param visit_id:
        :return:
        '''
        sql = "SELECT COUNT(*) is_exist FROM `product`.`visit_record_info` WHERE `visit_id` = '{}';".format(
            visit_id)
        result = self.get_single_data(sql)
        return result['is_exist']

    def save_review_result(self, visit_id, category_id, product_id, barcode, brand1, brand2, capacitysum,
                           capacityamount, commodityname, info1, info2, info3, info4, info5, info6, info7, info8,
                           info9, info10, info11, info12, info13, info14, info15, info16, info17, info18, info19,
                           info20, is_update):
        '''
        存储审核结果
        :param visit_id:
        :param category_id:
        :param product_id:
        :param barcode:
        :param brand1:
        :param brand2:
        :param capacitysum:
        :param capacityamount:
        :param commodityname:
        :param info1:
        :param info2:
        :param info3:
        :param info4:
        :param info5:
        :param info6:
        :param info7:
        :param info8:
        :param info9:
        :param info10:
        :param info11:
        :param info12:
        :param info13:
        :param info14:
        :param info15:
        :param info16:
        :param info17:
        :param info18:
        :param info19:
        :param info20:
        :param is_update:
        :return:
        '''
        sql = "INSERT INTO `product`.`review_result_info`(`visit_id`, `category_id`, `product_id`, `barcode`, `brand1`, `brand2`, `capacitysum`, `capacityamount`, `commodityname`, `info1`, `info2`, `info3`, `info4`, `info5`, `info6`, `info7`, `info8`, `info9`, `info10`, `info11`, `info12`, `info13`, `info14`, `info15`, `info16`, `info17`, `info18`, `info19`, `info20`, `is_update`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
            visit_id, category_id, product_id, barcode, brand1, brand2, capacitysum, capacityamount, commodityname,
            info1, info2, info3, info4, info5, info6, info7, info8, info9, info10, info11, info12, info13, info14,
            info15, info16, info17, info18, info19, info20, is_update)
        review_id = self.exec_save(sql)
        return review_id

if __name__ == '__main__':
    import json
    db = DBUtils()

    # 向访问记录表中插入数据
    # visit_ip, visit_type = '10.20.4.124', '0'
    # visit_id = db.save_visit_record_info(visit_ip, visit_type)
    # print(visit_id)

    # 向访问详情表中插入数据
    # visit_id, category_id, product_id, barcode, image_type, image_list = '1', '126', '100345', '1111100000032', '0', '123.jpg,234.jpg,345.jpg'
    # detail_id = db.save_visit_detail_info(visit_id, category_id, product_id, barcode, image_type, image_list)
    # print(detail_id)

    # 向图片详情表中插入数据
    # detail_id, image_path, image_name = '2', '/data/123/', '123.jpg'
    # image_id = db.save_image_detail_info(detail_id, image_path, image_name)
    # print(image_id)

    # 向访问结果表中插入数据
    # visit_id, visit_result, visit_result_data = '2', '1', {"123":"123","445":"456"}
    # result_id = db.save_visit_result_info(visit_id, visit_result, json.dumps(visit_result_data,ensure_ascii=False))
    # print(result_id)

    # 查询访问记录是否存在
    # visit_id = 100
    # result = db.get_data_info(visit_id)
    # print(result)

    # 存储审核信息记录
    visit_id, category_id, product_id, barcode, brand1, brand2, capacitysum, capacityamount, commodityname, info1, info2, info3, info4, info5, info6, info7, info8, info9, info10, info11, info12, info13, info14, info15, info16, info17, info18, info19, info20, is_update = '1', '2','3', '4', '5', '6', '7', '8', '9', '10','1', '2','3', '4', '5', '6', '7', '8', '9', '10','1', '2','3', '4', '5', '6', '7', '8', '9', '10'
    result = db.save_review_result(visit_id, category_id, product_id, barcode, brand1, brand2, capacitysum, capacityamount, commodityname, info1, info2, info3, info4, info5, info6, info7, info8, info9, info10, info11, info12, info13, info14, info15, info16, info17, info18, info19, info20, is_update)
    print(result)

