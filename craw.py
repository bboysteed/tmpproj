import requests
from fake_useragent import UserAgent
import json
# import pymongo
from time import strftime,gmtime


# clien=pymongo.MongoClient(host='改成自己的数据库地址')
# db=clien.Cat_eye_interface
# coll=db.eye_essay
#创建一个随机生成user-aengt的对象
ua=UserAgent()

#提取我们要的短评
def parse_json(json):
    if json:
        items=json.get('cmts')

        for item in items:
            data={
                'ID':item.get('nickName'),
                '短评':item.get('content'),
                '评分':item.get('score'),
                '用户地点':item.get('cityName'),
                '评论时间':item.get('startTime'),
                '回复数':item.get('reply'),
                '性别':item.get('gender')
            }


            #保存到数据库中
            # coll.insert_one(data)

            # '''
            # 写入本地的参数(修改文件名字和保存地方即可)
            cute=str(data)
            with open('评论.txt','a+')as p:
                p.write(cute)
                print('写入完成')


            print(data)


def Crawl_JSON(Page):
    ua = UserAgent()
    headers={
        'User-Agent':ua.random,
        'Host':'m.maoyan.com',
        'Referer':'http://m.maoyan.com/movie/1217236/comments?_v_=yes'
    }

    #猫眼电影短评接口
    page=Page
    u=0
    for i in range(page):

        try:

            offset=15*i
            The_Time= strftime("%Y-%m-%d ", gmtime())
            #http://m.maoyan.com/mmdb/comments/movie/342166.json?_v_=yes&offset=30&startTime=2018-10-18%2015%3A35%3A48
            #comment_api = 'http://m.maoyan.com/mmdb/comments/movie/1217236.json?_v_=yes&offset={0}&startTime=2018-10-18%2015%3A35%3A48'.format(offset)

            '''
            下方的comment_api中的地址可以自信更改为猫眼电影的 
            获取方法：
            1.打开浏览器
            2.按F12或者右键进去审查模式
            3.点开后 点击打开后审查模式左上角的手机模型的图标
            4.然后刷新 获取URL
            具体看https://mp.weixin.qq.com/s?__biz=MzU0NzY0NzQyNw==&mid=2247484297&idx=1&sn=c6b27dcd8fbb125bdf93dcc92e50cd6a&chksm=fb4a7925cc3df0339b554d46e918547285edf8005e749d7081bf409c76c7ba70460286c6f90d&mpshare=1&scene=23&srcid=1010VtAWxuPMTX2YYZeWGOyH#rd
            '''

            comment_api = 'http://m.maoyan.com/mmdb/comments/movie/1200486.json?_v_=yes&offset={}&startTime={}%2018%3A35%3A48'.format(offset,The_Time)
            #发送get请求
            response_coment=requests.get(url=comment_api,headers=headers)
            json_comment=response_coment.text
            json_comments=json.loads(json_comment)
            parse_json(json_comments)
            u+=15
        except:
            print('出现错误:')

The_page=int(input('请输入要爬取的页数:'))
parse_json(Crawl_JSON(The_page))