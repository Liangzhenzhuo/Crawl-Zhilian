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
 - 2019年3月31日：添加pyechart可视化方式，有利于后期放iframe到网页上


-------------------------------------------------------

效果
----
 - plt 模式效果展示
![](https://blog.tryfang.cn/usr/images/demo.png)

 - pyechart 模式效果展示
 
!!!
<iframe height="260" width="600" frameborder="0" marginwidth="0" marginheight="0" border="0" src="https://blog.tryfang.cn/usr/iframe/shenzhen.html#c7fc0f8e649549809c1df2d55d80dcd3" security="restricted" scrolling='no'></iframe>
<iframe height="260" width="600" frameborder="0" marginwidth="0" marginheight="0" border="0" src="https://blog.tryfang.cn/usr/iframe/shenzhen.html#9e4cbf4b69ae4e92b5fd677a7d2a2e06" security="restricted" scrolling='no'></iframe>
!!!


--------------


个人博客:[**https://blog.tryfang.cn**][1] 欢迎各位小伙伴前来讨论
-------------------------------------------------------


[1]:https://blog.tryfang.cn
