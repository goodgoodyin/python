# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 20:53:12 2018

@author: hao
"""
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import re
import urllib
import csv
import jieba
import pandas as pd
import numpy
from scipy.misc import imread
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
# 伪装ip
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]


def get_one_page(city,keyword, page):
    
    url ='http://search.51job.com/list/'+city+',000000,0000,00,9,99,'+keyword+',2,'+ str(page)+'.html'
    
    r = urllib.request.urlopen(url) 
    html = r.read().decode('gbk')
    return html



def parse_one_page(html):
    pattern = re.compile(r'class="t1 ">.*? <a target="_blank" title="(.*?)" href="(.*?)".*?'
                         '<span class="t2"><a target="_blank" title="(.*?)".*?'
                         '<span class="t3">(.*?)</span>.*?'
                         '<span class="t4">(.*?)</span>.*? '
                         '<span class="t5">(.*?)</span>',re.S)
    items = re.findall(pattern, html)
    for item in items:
        
        job_name = item[0]
        job_name = job_name.replace('<b>', '')
        job_name = job_name.replace('</b>', '')
        
        temp = item[4]
       
        
        avgSalary = 0
        
        if temp != '面议' and temp != '':            
            idx = temp.find('-')
            minSalary = float(temp[0:idx])
            maxSalary = float(temp[idx+1:(len(temp)-3)])
            if temp[len(temp)-3] == '千':           
                maxSalary = maxSalary * 1000
                minSalary = minSalary * 1000
                avgSalary = (maxSalary + minSalary)/2
            elif temp[len(temp)-3] == '万':
                maxSalary = maxSalary * 10000
                minSalary = minSalary * 10000
                avgSalary = (maxSalary + minSalary)/2
            else:
                avgSalary = 0
        yield {
                
                'job' : job_name,
                'website' : item[1],
                'company' : item[2],
                'address' : item[3],
                'salary' : item[4],
                'data' : item[5],
                'avgSalary' : avgSalary
                }
        
        
    
def get_job_detail(html):
    page_num = 0
    
    try:
        req = urllib.request.Request(html, headers = hds[page_num%len(hds)])
        source_code = urlopen(req).read()
        
    except (HTTPError, URLError) as e:     
        print(e)
        return None
    
    soup = BeautifulSoup(source_code,'html.parser',fromEncoding="gb18030")
    
    p_soup = soup.find('p', {'class':'msg ltype'}).get('title')
    
    p_list = p_soup.split('|')

    add = p_list[0] # 地址
    years = p_list[1] # 经验
    edu = p_list[2] # 学历
    num = p_list[3] # 招收人数
    
    
    inf = ''
  
    for informs in soup.find_all('div', {'class': 'bmsg job_msg inbox'}):
       
        for inform in informs.find_all('p'):
            inform = inform.get_text().strip()
            if inform != '':
                inf = inf + inform
          
    list_scale = []
    for scales in soup.find_all('div',{'class' : 'com_tag'}):
        for scale in  scales.find_all('p'):
            scale = scale.get_text().strip() # strip() 去除空格
            if scale != '':
                list_scale.append(scale)
        
        cp_flag = list_scale[0]
        
        cp_num = list_scale[1]
        
        cp_trade = list_scale[2]
        
    return {'inf': inf, 'address' : add, 'education' : edu, 'num' : num, 'years': years, 'cp_flag' : cp_flag, 'cp_num':cp_num, cp_trade :cp_trade} 

    
def write_csv_headers(path, headers):
   '''
   写入表头
   '''
   with open(path, 'a', encoding='gb18030', newline='') as f:
       f_csv = csv.DictWriter(f, headers)
       f_csv.writeheader()
       
def write_csv_rows(path, headers, rows):
    # 写入行
    with open(path, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        # 如果写入数据字典则写入一行，否则为多行
        if type(rows) == type({}):
            f_csv.writerow(rows)
        else:
            f_csv.writerows(rows)
        
def read_csv_column(path, column): 
   # 读取一列
     with open(path, 'r', encoding='gb18030', newline='') as f: 
         reader = csv.reader(f) 
         return [row[column] for row in reader]

def write_txt_file(path, txt):
    # 写入txt文本 
    with open(path, 'a', encoding = 'gb18030', newline='') as f:
        f.write(txt)
        
def read_txt_file(path):
    '''
    读取txt文本
    '''
    with open(path, 'r', encoding='gb18030', newline='') as f:
        return f.read()        
# 工资统计        
        
def main(city, keyword, pages):
    csv_filename = 'qcwy' + city + '_' + keyword + '.csv'
    txt_filename = 'qcwy' + city + '_' + keyword + '.txt'
    headers = ['job', 'years', 'education', 'salary','avgSalary', 'company', 'scale', 'website']
    write_csv_headers(csv_filename, headers)
    salaries = []
    for i in range(pages):
        # 获取该网页所有职位信息， 写入csv文件
        job_dict = {}
        html = get_one_page(city, keyword, i)
        items = parse_one_page(html)
        for item in items:   
                                
            job_detail = get_job_detail(item.get('website'))
            
            job_dict['job'] = item.get('job')
            job_dict['salary'] = item.get('salary')   
            job_dict['avgSalary'] = item.get('avgSalary')
            job_dict['company'] = item.get('company') 
            job_dict['website'] = item.get('website')
            if job_detail != '':
                job_dict['years'] = job_detail.get('years').strip() 
                job_dict['education'] = job_detail.get('education').strip()             
                job_dict['scale'] = job_detail.get('cp_num') 
                
            # 数据清洗
            pattern = re.compile(r'[一-龥]+')
            filterdata = re.findall(pattern, job_detail.get('inf'))
            write_txt_file(txt_filename, ''.join(filterdata))
            write_csv_rows(csv_filename, headers, job_dict)
    sal = read_csv_column(csv_filename, 4) 
    # 撇除第一项，并转换成整形，生成新的列表 
    for i in range(len(sal) - 1): 
        # 工资为'0'的表示招聘上写的是'面议',不做统计 
        if not sal[i] == '0': 
            salaries.append(float(sal[i + 1]))

    plt.hist(salaries, bins=20, )
    plt.show()
    # stop word    去除常见词
    content = read_txt_file(txt_filename) 
    segment = jieba.lcut(content) 
    words_df = pd.DataFrame({'segment':segment}) 
    stopwords = pd.read_csv("stopWords.txt",index_col=False,quoting=3,sep=" ",names=['stopword'],encoding='utf-8') 
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)] 
    # 词频统计
    words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size}) 
    words_stat = words_stat.reset_index().sort_values(by=["计数"],ascending=False)
    
    # 设置词云属性
    color_mask = imread('wxy.jpg')
    wordcloud = WordCloud(font_path= "simhei.ttf", # 设计字体可以显示中文
                          background_color = "white", # 背景颜色
                          max_words = 100, # 词云显示大词数
                          mask = color_mask, # 设置背景图片
                          max_font_size = 100, # 设置最大值
                          random_state = 42,
                          width = 1000, height = 860, margin = 2,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                          )
    # 生成词云, 可以用generate输入全部文本,也可以我们计算好词频后使用generate_from_frequencies函数
    word_frequence = {x[0]:x[1]for x in words_stat.head(100).values}
    word_frequence_dict = {}
    for key in word_frequence:
        word_frequence_dict[key] = word_frequence[key]
    wordcloud.generate_from_frequencies(word_frequence_dict) 
     # 从背景图片生成颜色值  
    image_colors = ImageColorGenerator(color_mask) 
     # 重新上色 
    wordcloud.recolor(color_func=image_colors) 
     # 保存图片 
    wordcloud.to_file('output.png') 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.show()

    # wordcloud = wordcloud.fit_words(word_frequence_list)
    # plt.imshow(wordcloud)

    # wordcloud.generate(words_stat)


            
if __name__ == '__main__':
    
 
    main('040000', 'python', 2)      
   