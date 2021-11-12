## 调用要使用的包
import json
import random
import requests
import time
import pandas as pd
from pyecharts.charts import Bar, Geo, Line, WordCloud, Page
from pyecharts.globals import ChartType
from pyecharts import options as opts
import jieba
import matplotlib
import threading

matplotlib.use('TkAgg')
from collections import Counter

## 设置headers和cookie
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
          'Connection': 'keep-alive',
          }
cookies = '_lxsdk_cuid=16af878591fc8-0b4776002c4f8d-5a40201d-1fa400-16af8785920c8; uuid_n_v=v1; iuuid=2E994CD042C211ECBF8A3BAF5A3C526CF6ECF6D0E33446F99FCEBE758B73EFFB; selectci=true; selectci=true; ci=10%2C%E4%B8%8A%E6%B5%B7; ci=10%2C%E4%B8%8A%E6%B5%B7; ci=10%2C%E4%B8%8A%E6%B5%B7; __mta=217846313.1636616250704.1636616255545.1636629118101.3; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1636616193,1636616210,1636708528; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk=174B924042C211ECAA79039A1A6DBD2B2B5C9D92C9884377ADD371B49718BE36; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1636708536; _lxsdk_s=17d136e3010-456-e77-bf1%7C%7C5'
cookie = {}
for line in cookies.split(';'):
    name, value = cookies.strip().split('=', 1)
    cookie[name] = value

missions = []

def getHttpProxy(n):
    print(n)
    resp = requests.get(f"http://dev.kdlapi.com/api/getproxy/?orderid=953671667394527&num={n}&area=%E5%9B%BD%E5%86%85&protocol=2&method=1&an_an=1&quality=0&sep=1").text
    proxys = resp.split("|")
    proxies = [{
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    } for proxy in proxys]
    print(proxies)

    return proxies

# def getinfo():
#     thread_num = 1
#     all = 15
#     per = int(all/thread_num)
#     for i in range(1, thread_num+1):
#         t = threading.Thread(target=ThreadGetinfo, args=(i*15, i*15+per+1))
#         global missions
#         missions.append(t)
#         # t.start()
#     for m in missions:
#         m.start()
#         time.sleep(6)
#     for m in missions:
#         m.join()


def getinfo():
    yaoshen = pd.DataFrame(columns=['date', 'score', 'city', 'comment', 'nick'])
    for i in range(855, 15000, 15):
        time.sleep(2)
        # print(i)
        url = f'https://m.maoyan.com/review/v2/comments.json?movieId=1200486&userId=-1&offset={i}&limit=15&ts=0&type=3'
        # print()
        html = requests.get(url=url, cookies=cookie, headers=header)
        cnt = repr(html.text[:40])
        info = "success!" if "cmts" in cnt else "error"
        print("[x]",i,url,cnt,"...", info)
        if info == "error":
            print(html.text)
            print("网站反爬...")
            return
        try:
            html = html.json()
        except Exception as e:
            print("web error",e)
            continue

        # data = json.loads(html.decode('utf-8'))
        data = html
        data_cmts = data["cmts"]
        # data_hcmts = data["hcmts"]
        for item in data_cmts:
            yaoshen = yaoshen.append({'date': item['time'].split(' ')[0], 'city': item['cityName'],
                                      'score': item['score'], 'comment': item['content'],
                                      'nick': item['nick']}, ignore_index=True)
        # for item in data_hcmts:
        #     yaoshen = yaoshen.append({'date': item['time'].split(' ')[0], 'city': item['cityName'],
        #                       'score': item['score'], 'comment': item['content'],
        #                       'nick': item['nick']}, ignore_index=True)
        # print(yaoshen)
        yaoshen.to_excel('我不是药神855-.xlsx', index=False)
        # except:
        #     print("Catch err")
        #     continue
        # break
    # yaoshen.to_excel('我不是药神_m_edit.xlsx', index=False)

# 去重
def quchong():
    data = pd.read_excel("我不是药神_m_edit.xlsx")
    data = data.drop_duplicates()
    data = pd.DataFrame(data)
    data.to_excel('./我不是药神new3.xlsx')


def charts():
    ## 可以直接读取我们已经爬到的数据进行分析
    yaoshen_com = pd.read_excel('./我不是药神new.xlsx')
    grouped = yaoshen_com.groupby(['city'])
    grouped_pct = grouped['score']
    # print(grouped_pct)
    # ## 全国热力图
    city_com = grouped_pct.agg(['mean', 'count'])
    city_com.reset_index(inplace=True)
    city_com['mean'] = round(city_com['mean'], 2)

    def heat_geo() -> Geo:
        data = [(city_com['city'][i], city_com['count'][i]) for i in range(0, city_com.shape[0])]
        geo =Geo() \
            .add_schema(maptype="china") \
            .add(
            "geo",
            data,
            type_=ChartType.HEATMAP,
            symbol_size=1,
            blur_size=5,
            point_size=7,

        ) \
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False)) \
            .set_global_opts(

            visualmap_opts=opts.VisualMapOpts(),
            title_opts=opts.TitleOpts(title="评论分布热力图"),
        )
        # .render("我不是药神全国热力图.html")
        return geo

    def bar_line() -> Bar:
        ## 主要城市评论数与评分
        city_main = city_com.sort_values('count', ascending=False)[0:20]
        attr = list(city_main['city'])
        v1 = list(city_main['count'])
        v2 = list(city_main['mean'])
        print(list(attr), v1, v2)
        bar = Bar() \
            .add_xaxis(attr) \
            .add_yaxis("评论数", v1) \
            .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} 分"), interval=1

            ),
            # xaxis=opts.AxisOpts(
            #     axislabel_opts=opts.LabelOpts(rotate=30)
            # )
        ) \
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False)) \
            .set_global_opts(
            title_opts=opts.TitleOpts(title="评论数评分统计图"),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} 个")),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30))
        )

        line = Line().add_xaxis(attr).add_yaxis("评分", v2, yaxis_index=1)
        bar.overlap(line)
        # bar.render("评论数评分统计图.html")
        return bar

    def line() -> Line:
        # ## 主要城市评分降序
        city_main = city_com.sort_values('count', ascending=False)[0:20]
        city_score = city_main.sort_values('mean', ascending=False)[0:20]
        attr = city_score['city']
        v1 = city_score['mean']

        li = Line() \
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(rotate=30)),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ) \
            .add_xaxis(xaxis_data=attr) \
            .add_yaxis(
            series_name="",
            y_axis=v1,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        # .render("basic_line_chart.html")
        return li

        ## 主要城市评分全国分布

    def heat() -> Geo:
        city_score_area = city_com.sort_values('count', ascending=False)[0:500]
        city_score_area.reset_index(inplace=True)
        data = [(city_score_area['city'][i], city_score_area['mean'][i]) for i in range(0, city_score_area.shape[0])]

        geo = Geo() \
            .add_schema(maptype="china") \
            .add(
            "geo",
            data,
            type_=ChartType.HEATMAP,
            # symbol_size=1,
            # blur_size=5,
            # point_size=7,

        ) \
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False)) \
            .set_global_opts(

            visualmap_opts=opts.VisualMapOpts(),
            title_opts=opts.TitleOpts(title="《我不是药神》全国主要城市打分图"),
        )
        # .render("我不是药神全国主要城市打分图.html")
        return geo

    def word_cloud() -> WordCloud:
        ## 绘制词云
        wc = WordCloud()
        yaoshen_str = ' '.join(yaoshen_com['comment'])
        words_list = []
        word_generator = jieba.cut_for_search(yaoshen_str)
        for word in word_generator:
            words_list.append(word)
        words_list = [k for k in words_list if len(k) > 1]
        yaoshen_count = Counter(words_list)
        ans = [t for t in tuple(yaoshen_count.items()) if t[1] > 4]
        # print(ans)
        # (
        #     WordCloud()
        wc.add(series_name="评论分析", data_pair=ans, word_size_range=[10, 100]) \
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="评论分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        # .render("basic_wordcloud.html")
        # )
        return wc

    def page_simple_layout():
        page = Page(layout=Page.SimplePageLayout)
        page.add(
            heat_geo(),
            word_cloud(),
            heat(),
            line(),
            bar_line(),
        )
        page.render("page_simple_layout.html")
    page_simple_layout()

if __name__ == '__main__':

    getinfo()
    # quchong()
    # charts()
