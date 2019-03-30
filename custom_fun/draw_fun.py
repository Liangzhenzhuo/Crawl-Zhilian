# -*- coding: utf-8 -*-
# @Time    : 2019-03-29 14:17:58
# @Author  : Nismison
# @FileName: draw_fun.py
# @Description: 绘图相关函数
# @Blog    ：https://blog.tryfang.cn

import matplotlib.pyplot as plt
from warnings import filterwarnings
from time import strftime, localtime
from pyecharts import Bar, Page
from random import choice
from xpinyin import Pinyin
from bs4 import BeautifulSoup as bs
from os.path import exists
from os import mkdir
# 忽略 matplotlib 的 warning
filterwarnings(action='ignore',module='.*matplotlib.*')




# 图表自动打标签函数
def autolabel(rects, foi, unit, who):
    if foi == 'float':
        for rect in rects:
            height = rect.get_height()
            who.text(rect.get_x()+rect.get_width()/2.-0.2, 1.01*height, '%s%s' % (float(height), unit))
    elif foi == 'int':
        for rect in rects:
            height = rect.get_height()
            who.text(rect.get_x()+rect.get_width()/2.-0.2, 1.01*height, '%s%s' % (int(height), unit))
    else:
        for rect in rects:
            height = rect.get_height()
            if height >= 100:
                who.text(rect.get_x()+rect.get_width()/2.-0.23, 1.01*height, '%s%s' % (height, unit))
            else:
                who.text(rect.get_x()+rect.get_width()/2.-0.13, 1.01*height, '%s%s' % (height, unit))

# plt 绘图函数
def plt_func(x, y, y2, title, show, save, save_path):
    x_lable_font = {'weight': 'bold', 'size': 14}   #字体
    fig = plt.figure(figsize=(13.66, 7.68))     # 图表大小
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.xticks(rotation=45) # x轴文字旋转45度
    sub = plt.subplot(111)      # 生成子图一行一列占第一个
    a = sub.bar(x, y, label='岗位需求', width=-.4, color="lightskyblue", align='edge', edgecolor = 'white')
    plt.ylabel('就业岗位数量(个)', x_lable_font)    # 左边 y 轴 label
    sub2 = sub.twinx()  # 镜像一份生成右边的y轴
    b = sub2.bar(x, y2, label='收入水平', width=.4, color="yellowgreen", align='edge', edgecolor = 'white')
    plt.title("{} - 截止至 {}".format(title, strftime("%Y-%m-%d", localtime())))    # 标题
    plt.xlabel('岗位名称', x_lable_font)        # x轴label
    plt.ylabel('收入水平(K)', x_lable_font)     # 右边 y 轴 label
    # plt.margins(.006)     # margins 内容和图表边框的距离
    autolabel(rects=a, foi='', unit='', who=sub)
    autolabel(rects=b, foi='float', unit='K', who=sub2)
    fig.legend(bbox_to_anchor=(1,1), bbox_transform=sub.transAxes)      # 图例
    if save == True:
        plt.savefig("{}/{} - {}.png".format(save_path, title[:title.index("地区")], strftime("%Y-%m-%d", localtime())))     # 保存图片
        print("图片已成功保存到 {} 目录下".format(save_path))
    if show == True:
        plt.show()

# pyechart 绘图函数
def echart(x1, x2, values, title, save_path, iframe=False, **kwargs):
    color_list = ['#19CAAD', '#F4606C', '#dc5712', '#55aaad']
    page = Page(page_title=title)
    var_name_list = []
    index = 0
    for i in values:
        var_name = "bar{}".format(index)
        var_name_list.append(var_name)
        if iframe == False:
            bar = locals()[var_name] = Bar(title=i, width=1150, height=500, title_pos='center')
        else:
            bar = locals()[var_name] = Bar(title=i, width=kwargs['iframe_width'], height=kwargs['iframe_height'], title_pos='center')
        x_attr = "x{}".format(index + 1)
        bar.add(i, locals()[x_attr], values[i],
                xaxis_interval=0,                   # x轴刻度间隔，0为无间隔
                xaxis_rotate=45,                    # x轴文字旋转
                # is_label_show=True,               # 显示数值
                label_color=[choice(color_list)],   # 柱子颜色
                legend_pos="right",                 # 图例位置（'left, center, right'）
                mark_line=['average'],              # 标记平均值线（max, min, average）
                is_toolbox_show=False,              # 显示右侧工具箱（True, False）
                )   
        page.add(bar)
        index += 1
    if iframe == False:
        page.render(save_path + "/" + Pinyin().get_pinyin(title[:title.index("地区")], '') + '.html')
        print("html文件已保存到{}".format(save_path))
    else:
        save_directory = save_path + "/" + title[:title.index("地区")]
        if not exists(save_directory):
            mkdir(save_directory)
        save_file_name = Pinyin().get_pinyin(title[:title.index("地区")], '') + '.html'
        page.render(save_directory + "/" + save_file_name)
        return {"dir":save_directory, "all":save_directory + "/" + save_file_name, "file":save_file_name}
        
