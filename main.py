# -*- coding: utf-8 -*-
# @Time    : 2019-03-27 00:59:10
# @Author  : Nismison
# @FileName: main.py
# @Description: 数据可视化分析
# @Blog    ：https://blog.tryfang.cn

from custom_fun import analysis_fun, cout_fun, draw_fun, thread_fuc

if __name__ == "__main__":
    # 调用数据分析函数
    analysis_fun.job_fenxi(city="深圳", show=False, save=True, mode="pyechart", save_path=r"C:\Users\wn\Desktop")
    # 调用爬虫函数
    # city_dict = {"南宁": "785", "深圳": "765", "上海": "538", "北京": "530"}
    # city_dict = {"上海": "538"}
    # thread_fuc.thread_create(city_dict=city_dict)
    
