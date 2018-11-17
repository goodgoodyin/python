# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 08:18:01 2018

@author: hao
"""
 
# 抓取猫眼电影排行
import requests
import re
import json
from requests.exceptions import RequestException
import time

def get_one_page(url):
    try:        
        # 伪装ip
        headers={"user-agent":'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        response = requests.get(url,headers=headers)
        
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    
def parse_one_page(html):
    # 非贪婪匹配来提取i节点内的信息:  '<dd>.*?board-index.*?>(.*?)</i>',匹配从<dd>标签开始到</i>结束
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    print(items)
    for item in items:        
        yield{               
                'index': item[0],
                'image': item[1],
                'title': item[2].strip(),
                'actor': item[3].strip()[3:] if len(item[3]) > 3 else '',
                'time': item[4].strip()[5:] if len(item[4]) > 5 else '',
                'score' :item[5].strip() + item[6].strip()
             }
 
def write_to_file(content):
     print("c")
     with open('result.txt', 'a', encoding='utf-8') as f:
         f.write(json.dumps(content, ensure_ascii=False,) + '\n')
        

def main(offset):
    url = 'http://maoyan.com/board/4?offset='+str(offset)
    html = get_one_page(url) 
    for item in parse_one_page(html):
        print("a")
        print(item)
        write_to_file(item)
        
if __name__ == '__main__':
    for i in range(10):
        main(offset= i * 10)
        time.sleep(10)
       
