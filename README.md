**Crawl-Zhilian**
=============
![](https://img.shields.io/badge/pymysql-0.9.3-brightgreen.svg) ![](https://img.shields.io/badge/requests-2.21.0-green.svg) ![](https://img.shields.io/badge/matplotlib-3.0.3-yellowgreen.svg) ![](https://img.shields.io/badge/beautifulsoup4-4.7.1-yellow.svg) ![](https://img.shields.io/badge/xpinyin-0.5.6-orange.svg)

> **Python爬取某联招聘所有招聘信息存入Mysql数据库并进行数据可视化分析**



---------------
**目录结构**
------
```
│  main.py                  //主程序文件
│  README.md                //readme
└─custom_fun                //自定义模块
    │  analysis_fun.py      //数据分析相关函数
    │  cout_fun.py          //计数相关函数
    │  draw_fun.py          //绘图相关函数
    │  thread_fuc.py        //线程相关函数
    └─__init__.py  
```
    

-----------------------
更新日志
-------
 - 2019年3月31日：添加pyechart可视化方式，支持自动生成html文件以及自动生成iframe标签，为后期将分析结果嵌入网页内等操作提供更便捷的代码


-------------------------------------------------------

效果
----
 - plt 模式效果展示
![](https://blog.tryfang.cn/usr/images/demo.png)

 - pyechart 模式效果图	 - pyechart 模式效果展示
![](https://blog.tryfang.cn/usr/images/demo2.png)


[1]:https://blog.tryfang.cn
