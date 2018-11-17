# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 07:49:21 2018

@author: hao
"""

import re
import requests

def downlaodPic(html, keyword):
    # pic_url = re.findall('"data-objurl":"(.*?)",', html, re.S)
    pic_url = re.findall('"objURL":"(.*?)",',html,re.S)
    i = 0   
    
    print("找出关键词：" + keyword + '的图片，现在开始下载图片……' )
    for each in pic_url:
        print("正在下载第"+ str(i+1) +"张图片，图片地址："+ str(each))
        try:
            pic = requests.get(each, timeout = 10)
        except requests.exceptions.ConnectionError:
            print("错误：当前页面无法加载")
            continue
        string = 'pictures\\'+ keyword + '_' + str(i) + '.jpg'
        fp = open(string,'wb')
        fp.write(pic.content)
        fp.close()
        i += 1
        
if __name__ == '__main__':
    word = input("输入关键字：")
    url = "http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=" + word +'&ct=201326592&v=flip'
    result = requests.get(url)
    downlaodPic(result.text, word)