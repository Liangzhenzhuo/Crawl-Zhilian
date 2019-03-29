# -*- coding: utf-8 -*-
# @Time    : 2019-03-29 14:23:37
# @Author  : Nismison
# @FileName: thread_fuc.py
# @Description: 线程相关函数
# @Blog    ：https://blog.tryfang.cn

from threading import Thread
from custom_fun import analysis_fun

# 爬虫函数批量创建线程
def thread_create(city_dict):
    # 线程池
    thread_pool = []
    # 批量创建线程放到线程池中
    for key in city_dict:
        value = city_dict[key]
        th = Thread(target=analysis_fun.zhilian_crawler, args=(key, value, key))
        thread_pool.append(th)
    # 从线程池中批量启动线程
    for th in thread_pool:
        th.start()
    # 等待子线程执行结束
    for th in thread_pool:
        Thread.join(th)