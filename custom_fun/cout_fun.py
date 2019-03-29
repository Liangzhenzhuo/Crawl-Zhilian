# -*- coding: utf-8 -*-
# @Time    : 2019-03-29 14:18:12
# @Author  : Nismison
# @FileName: cout_fun.py
# @Description: 计算相关函数
# @Blog    ：https://blog.tryfang.cn

# 求平均数函数
def avg(before, after):
    if len(after) == 0:
        return 0
    else:
        avg_res = round(before / len(after), 1)
        return avg_res

# 字符串列表转换数字求和
def trans_sum(str_list: list):
    return sum(list(map(float, str_list)))