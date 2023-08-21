#!/usr/bin/env python
# encoding: utf-8

"""
@Name: translate_utils.py
@Auth: liuyb
@Date: 2022/7/8-10:11
@Desc: 翻译工具类-调用有道接口进行的翻译
@Ver : 0.0.0
"""
import random
import requests
import json

class TranslateUtils(object):

    def __init__(self):
        self.url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
        self.key = {'type': "AUTO",'i': '',"doctype": "json","version": "2.1","keyfrom": "fanyi.web","ue": "UTF-8","action": "FY_BY_CLICKBUTTON","typoResult": "true"}
        # 简易伪装
        self.agent = [
           "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
           "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
           "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
           "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
           "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
           "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
           "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
           "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
           "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
           "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
           "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
           "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
           "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
           "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
           "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
        ]

    def get_translate_word(self, word):
        '''
        获取翻译的结果
        :param word:
        :return:
        '''
        result = ''

        item_key = self.key
        item_key['i'] = word

        # 随机选取一个agent, 并进行请求
        headers = {'User-Agent': random.choice(self.agent)}

        try:
            response = requests.post(self.url, headers=headers, data=item_key)

            if response.status_code == 200:
                # 然后相应的结果
                content = response.text
                translate_info = json.loads(content)
                result = translate_info['translateResult'][0][0]['tgt']
            else:
                raise Exception("有道词典调用失败")
        except Exception as e:
            print('翻译出现异常: {}'.format(str(e)))
        return result

if __name__ == '__main__':
    tru = TranslateUtils()

    word = '颓废之水淡香水'
    result = tru.get_translate_word(word)
    print(result)





