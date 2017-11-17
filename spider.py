# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def gettotalurl(baseurl,header,page):
    print'正在打开第' + str(page) + '页网站页面'
    urllist = []
    try:
        r = requests.get(baseurl,headers = header)
        r.encoding = 'utf-8'
        html = r.text
        #print html
        soup = BeautifulSoup(html,"html.parser")
        product = soup.find_all('span',class_="is-account")
        for i in product:
            url = i.a.attrs['href']
            urllist.append(url)
        return urllist
    except Exception,e:
        print "链接失败!"

def getinfo(url,header):
    print '开始获取商品数据',url
    try:
        r = requests.get(url,headers = header)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html,"html.parser")
        title = soup.title.string.split('_')[0]#获得商品标题
        price = soup.find('span',class_="price").string#获得商品价格
        time = soup.find('span',class_="num")#获取商品交易次数，首次交易为1
        if time:
            time = time.string
        else:
            time = "首次交易"
        imgurls = soup.find('ul',class_="slider-items")#图片
        if imgurls:
            imgurl = imgurls.find_all('img')
            for i in imgurl:
                picurl = i.get('src')
                return {
                    'title': title,
                    'price': price,
                    'time': time,
                    'picurl':picurl
                }
        else:
            picurl = '无图片'
            return {
                'title':title,
                'price':price,
                'time':time,
                'picurl':picurl
            }
    except:
        print '请求信息出错',url

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print '储存成功',result
        return True
    else:
        return False

def run():
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    for x in range(150):
        page = x + 1
        baseurl = 'https://www.jiaoyimao.com/g4502/n' + str(page) + '.html'
        for url in gettotalurl(baseurl,header,page):
            result = getinfo(url,header)
            save_to_mongo(result)

run()