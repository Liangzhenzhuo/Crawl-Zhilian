# -*- coding: utf-8 -*-
# @Time    : 2019-03-29 14:17:46
# @Author  : Nismison
# @FileName: analysis_fun.py
# @Description: 数据分析相关函数
# @Blog    ：https://blog.tryfang.cn

from re import search, findall, IGNORECASE
from pymysql import connect
from fake_useragent import UserAgent
from requests import get
from bs4 import BeautifulSoup as bs
from json import loads, decoder
from pymysql.err import ProgrammingError
from custom_fun import cout_fun, draw_fun
from collections import Counter
from xpinyin import Pinyin
from os.path import dirname



# 工资分析函数
def salary_fenxi(string: str):
    if search("面议", string) or search("/", string) or search("以下", string) or search("校招", string):
        return None
    else:
        res = findall(r'(\d+(\.\d+)?)',string)
        return res[0][0], res[1][0]


# 关键词匹配函数
def condition(string_: str, list_: list):
    res = False
    for i in list_:
        if search(i, string_, IGNORECASE):
            res = True
    return res


# 爬虫函数
def zhilian_crawler(city_name, city_num, db_name):
    p = Pinyin()
    city_pinyin = p.get_pinyin(city_name, '')
    db_name = p.get_pinyin(db_name, '')
    # 连接数据库
    db = connect("localhost", "root", "o9ptZVkJib9p", "zhilian")
    # 创建游标对象
    cursor = db.cursor()
    print("爬取任务 - {} 开始".format(city_name))
    zhilian_url = "https://www.zhaopin.com/{}/".format(city_pinyin)
    zhilian_get = get(zhilian_url, headers={"User-Agent": UserAgent().random})
    zhilian_bs = bs(zhilian_get.text, features="html.parser")
    posistions = zhilian_bs.select(
        ".zp-jobNavigater__list li .zp-jobNavigater__pop a")
    for posistion in posistions:
        posistion_title = posistion.text
        # 大概看了一下基本上没有哪个行业招聘信息超过20页，所以range(20)够用了
        for page in range(20):
            # 拼接请求url
            posistion_href = "https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=90&cityId={}&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3&_v=0.32608946&x-zp-page-request-id=dbb76be8d2494593b499fc44b1acd457-1553612808344-306559".format(
                page * 90, city_num, posistion_title)
            header = {"User-Agent": UserAgent().chrome}
            posistion_get = get(posistion_href, headers=header)
            # 解析响应内容
            job_json = loads(posistion_get.text)["data"]["results"]
            # 如果相应内容为空 跳出循环
            if len(job_json) == 0:
                break
            for job in job_json:
                city = job['city']['display']  # 城市
                salary = job['salary']  # 工资
                welfare = ''  # 福利
                for welfare_i in job['welfare']:
                    welfare += welfare_i + '/'
                empl_type = job['emplType']  # 工作类型，全职/兼职
                job_name = job['jobName']  # 职位名称
                company_name = job['company']['name']  # 公司名称
                company_type = job['company']['type']['name']  # 公司类型
                company_size = job['company']['size']['name']  # 公司规模
                edu_level = job['eduLevel']['name']  # 学历要求
                if search('businessArea', str(job)):  # 办公地点
                    business_area = job['businessArea']
                else:
                    business_area = 'None'
                working_exp = job['workingExp']['name']  # 工作经验
                job_info = [city, salary, welfare, empl_type, job_name, company_name,
                            company_type, company_size, edu_level, business_area, working_exp]
                try:
                    # 拼接查询sql语句
                    search_sql = """select * from {} where job_name='{}' and company_name='{}'""".format(
                        db_name, job_name, company_name)
                    # 如果数据已经存在 跳过
                    if cursor.execute(search_sql) != 0:
                        print("重复")
                        continue
                    else:
                        # 拼接插入sql语句
                        insert_sql = """insert into {}(city, salary, welfare, empl_type, job_name, company_name, company_type, company_size, edu_level, business_area, working_exp, source) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '智联招聘')""".format(
                            db_name, city, salary, welfare, empl_type, job_name, company_name, company_type, company_size, edu_level, business_area, working_exp)
                        # 执行sql语句
                        cursor.execute(insert_sql)
                        # 提交操作
                        db.commit()
                        print(job_info)
                except ProgrammingError:
                    continue
    print("爬取任务 - {} 完成".format(city))
    cursor.close()
    db.close()

    # 数据分析函数
def job_fenxi(city: str, show: bool=True, save: bool=True, save_path: str=dirname(__file__)):
    """
    _s：保存工资数据列表
    _n：工资数据列表的sum
    _c：职位匹配关键词
    """
    db = connect("localhost", "root", "o9ptZVkJib9p", "zhilian")
    # 创建游标对象
    cursor = db.cursor()
    pinyin = Pinyin()
    db_name = pinyin.get_pinyin(city, '')
    # 岗位数据存放列表
    positions = []
    java_s, c_s, html_s, php_s, python_s, big_data_s, ios_s, android_s, net_s, suanfa_s, small_app_s, rgzn_s, database_s, yunwei_s, qianrushi_s, auto_s, node_s, system_s, qukuailian_s, cloud_s, network_s = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    # 关键词，方便修改添加
    java_c = ["java", "jsp"]
    c_c = [r"c\+", "c#"]
    html_c = ["html", "web", "css", "前端", "seo"]
    php_c = ["php"]
    python_c = ["python"]
    big_data_c = ["大数据", '数据分析', '数据挖掘', '爬虫']
    ios_c = ["ios"]
    android_c = ['安卓', 'android']
    net_c = [".net"]
    suanfa_c = ["算法"]
    small_app_c = ["小程序"]
    rgzn_c = ["人工智能", "ai", "人脸识别", "图像识别", "机器学习", "深度学习", "机器视觉", "计算机视觉", ]
    database_c = ["数据库", "mysql", "Oracle", ]
    yunwei_c = ["系统运维", "软件运维", "系统维护", "软件维护"]
    qianrushi_c = ["嵌入", ]
    auto_c = ["自动", ]
    node_c = ["node", "node.js", ]
    system_c = ["系统", "Linux", "centos", "debian", "Ubuntu", ]
    qukuailian_c = ["区块链", ]
    cloud_c = ["云", ]
    network_c = ["网络运维", "网络安全", "网络运营", "网络管理", "网络架构", "网络搭建", "光网络", "网络维护", ]
    
    search_sql = """select job_name,salary salary from {}""".format(db_name)
    cursor.execute(search_sql)
    for fetch in cursor.fetchall():
        job_name = fetch[0]
        salary = salary_fenxi(fetch[1])
        # 判断职位关键词
        if condition(job_name, java_c):
            positions.append('java')
            if salary != None:
                java_s.append(salary[0])
                java_s.append(salary[1])
        if condition(job_name, c_c):
            positions.append('c')
            if salary != None:
                c_s.append(salary[0])
                c_s.append(salary[1])
        if condition(job_name, html_c):
            positions.append('html')
            if salary != None:
                html_s.append(salary[0])
                html_s.append(salary[1])
        if condition(job_name, python_c):
            positions.append('python')
            if salary != None:
                python_s.append(salary[0])
                python_s.append(salary[1])
        if condition(job_name, php_c):
            positions.append('php')
            if salary != None:
                php_s.append(salary[0])
                php_s.append(salary[1])
        if condition(job_name, big_data_c):
            positions.append('big_data')
            if salary != None:
                big_data_s.append(salary[0])
                big_data_s.append(salary[1])
        if condition(job_name, rgzn_c):
            positions.append('rgzn')
            if salary != None:
                rgzn_s.append(salary[0])
                rgzn_s.append(salary[1])
        if condition(job_name, ios_c):
            positions.append('ios')
            if salary != None:
                ios_s.append(salary[0])
                ios_s.append(salary[1])
        if condition(job_name, android_c):
            positions.append('android')
            if salary != None:
                android_s.append(salary[0])
                android_s.append(salary[1])
        if condition(job_name, net_c):
            positions.append('net')
            if salary != None:
                net_s.append(salary[0])
                net_s.append(salary[1])
        if condition(job_name, node_c):
            positions.append('node')
            if salary != None:
                node_s.append(salary[0])
                node_s.append(salary[1])
        if condition(job_name, database_c):
            positions.append('database')
            if salary != None:
                database_s.append(salary[0])
                database_s.append(salary[1])
        if condition(job_name, suanfa_c):
            positions.append('suanfa')
            if salary != None:
                suanfa_s.append(salary[0])
                suanfa_s.append(salary[1])
        if condition(job_name, small_app_c):
            positions.append('small_app')
            if salary != None:
                small_app_s.append(salary[0])
                small_app_s.append(salary[1])
        if condition(job_name, yunwei_c):
            positions.append('yunwei')
            if salary != None:
                yunwei_s.append(salary[0])
                yunwei_s.append(salary[1])
        if condition(job_name, qianrushi_c):
            positions.append('qianrushi')
            if salary != None:
                qianrushi_s.append(salary[0])
                qianrushi_s.append(salary[1])
        if condition(job_name, auto_c):
            positions.append('auto')
            if salary != None:
                auto_s.append(salary[0])
                auto_s.append(salary[1])
        if condition(job_name, qukuailian_c):
            positions.append('qukuailian')
            if salary != None:
                qukuailian_s.append(salary[0])
                qukuailian_s.append(salary[1])
        if condition(job_name, cloud_c):
            positions.append('cloud')
            if salary != None:
                cloud_s.append(salary[0])
                cloud_s.append(salary[1])
        if condition(job_name, system_c):
            positions.append('system')
            if salary != None:
                system_s.append(salary[0])
                system_s.append(salary[1])
        if condition(job_name, network_c):
            positions.append('network')
            if salary != None:
                network_s.append(salary[0])
                network_s.append(salary[1])

    c_n = cout_fun.trans_sum(c_s)
    network_n = cout_fun.trans_sum(network_s)
    java_n = cout_fun.trans_sum(java_s)
    php_n = cout_fun.trans_sum(php_s)
    python_n = cout_fun.trans_sum(python_s)
    html_n = cout_fun.trans_sum(html_s)
    big_data_n = cout_fun.trans_sum(big_data_s)
    ios_n = cout_fun.trans_sum(ios_s)
    android_n = cout_fun.trans_sum(android_s)
    net_n = cout_fun.trans_sum(net_s)
    suanfa_n = cout_fun.trans_sum(suanfa_s)
    small_app_n = cout_fun.trans_sum(small_app_s)
    rgzn_n = cout_fun.trans_sum(rgzn_s)
    database_n = cout_fun.trans_sum(database_s)
    yunwei_n = cout_fun.trans_sum(yunwei_s)
    qianrushi_n = cout_fun.trans_sum(qianrushi_s)
    auto_n = cout_fun.trans_sum(auto_s)
    system_n = cout_fun.trans_sum(system_s)
    node_n = cout_fun.trans_sum(node_s)
    qukuailian_n = cout_fun.trans_sum(qukuailian_s)
    cloud_n = cout_fun.trans_sum(cloud_s)
    # 分析岗位数量列表数据
    positions_dict = dict(Counter(positions))
    # 规定x轴
    x = ['C语言', 'Java', 'Php', 'Python', 'Web前端', '数据分析', 'IOS', 'Andriod', '.Net', '算法', '小程序', '人工智能', '数据库', '运维', '嵌入式', ' 自动化', '系统', 'Node.js', "区块链", '云', '网络']
    # 规定y轴
    y1 = [positions_dict['c'], positions_dict['java'], positions_dict['php'], positions_dict['python'], positions_dict['html'], positions_dict['big_data'], positions_dict['ios'], positions_dict['android'], positions_dict['net'], positions_dict['suanfa'], positions_dict['small_app'], positions_dict['rgzn'], positions_dict['database'], positions_dict['yunwei'], positions_dict['qianrushi'], positions_dict['auto'], positions_dict['system'], positions_dict['node'], positions_dict['qukuailian'], positions_dict['cloud'], positions_dict['network']]
    y2 = [cout_fun.avg(c_n, c_s), cout_fun.avg(java_n, java_s), cout_fun.avg(php_n, php_s), cout_fun.avg(python_n, python_s), cout_fun.avg(html_n, html_s), cout_fun.avg(big_data_n, big_data_s), cout_fun.avg(ios_n, ios_s), cout_fun.avg(android_n, android_s), cout_fun.avg(net_n, net_s), cout_fun.avg(suanfa_n, suanfa_s), cout_fun.avg(small_app_n, small_app_s), cout_fun.avg(rgzn_n, rgzn_s), cout_fun.avg(database_n, database_s), cout_fun.avg(yunwei_n, yunwei_s), cout_fun.avg(qianrushi_n, qianrushi_s), cout_fun.avg(auto_n, auto_s), cout_fun.avg(system_n, system_s), cout_fun.avg(node_n, node_s), cout_fun.avg(qukuailian_n, qukuailian_s), cout_fun.avg(cloud_n, cloud_s), cout_fun.avg(network_n, network_s)]
    # 排序
    data1=[(type_name, type_count, salary) for type_name, type_count, salary in zip(y1, x, y2)]
    data1.sort(reverse=True)
    count1=[type_name for type_name,type_count, salary in data1]
    name1=[type_count for type_name,type_count, salary in data1]
    salary1=[salary for type_name,type_count, salary in data1]
    # 调用绘图函数
    draw_fun.plt_func(x=name1, y=count1, y2=salary1, title="{}地区IT行业部分技术岗位某招聘网站岗位数量与平均收入水平(不完全统计) ".format(city), show=show, save=save, save_path=save_path)
    cursor.close()
    db.close()