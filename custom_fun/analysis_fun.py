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
    for i in range(len(list_)):
        if i == 0:
            continue
        else:
            if search(list_[i], string_, IGNORECASE):
                res = True
    return res


# 爬虫函数
def zhilian_crawler(city_name, city_num, db_name):
    p = Pinyin()
    city_pinyin = p.get_pinyin(city_name, '')
    db_name = p.get_pinyin(db_name, '')
    # 连接数据库
    db = connect("localhost", "root", "", "zhilian")
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
        # 大概看了一下基本上没有哪个行业招聘信息超过12页，所以range(12)够用了
        for page in range(12):
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
    print("爬取任务 - {} 完成".format(city_name))
    cursor.close()
    db.close()

# 数据分析函数
def job_fenxi(city, mode, show=True, save=True, save_path=dirname(__file__)):
    """
    _s：保存工资数据列表
    _n：工资数据列表的sum
    _c：职位匹配关键词
    """
    db = connect("localhost", "root", "", "zhilian")
    # 创建游标对象
    cursor = db.cursor()
    pinyin = Pinyin()
    db_name = pinyin.get_pinyin(city, '')
    # 岗位数据存放列表
    positions = []
    java_s, c_s, html_s, php_s, python_s, big_data_s, ios_s, android_s, net_s, suanfa_s, small_app_s, rgzn_s, database_s, yunwei_s, qianrushi_s, auto_s, node_s, system_s, qukuailian_s, cloud_s, network_s = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    # 关键词，方便修改添加
    java_c = ["Java", "Java", "jsp"]
    c_c = ["C语言", r"c\+", "c#"]
    html_c = ["Web前端", "html", "web", "css", "前端", "seo"]
    php_c = ["PHP", "PHP"]
    python_c = ["Python", "Python"]
    big_data_c = ["大数据", "大数据", '数据分析', '数据挖掘', '爬虫']
    ios_c = ["IOS", "IOS"]
    android_c = ['Android', 'Android', '安卓']
    net_c = [".Net", ".Net"]
    suanfa_c = ["算法", "算法"]
    small_app_c = ["小程序", "小程序"]
    rgzn_c = ["人工智能", "人工智能", "ai", "人脸识别", "图像识别", "机器学习", "深度学习", "机器视觉", "计算机视觉", ]
    database_c = ["数据库", "数据库", "mysql", "Oracle", ]
    yunwei_c = ["运维", "系统运维", "软件运维", "系统维护", "软件维护"]
    qianrushi_c = ["嵌入式", "嵌入", ]
    auto_c = ["自动化", "自动", ]
    node_c = ["Node.js", "Node.js", "node", ]
    system_c = ["系统", "系统", "Linux", "centos", "debian", "Ubuntu", ]
    qukuailian_c = ["区块链", "区块链", ]
    cloud_c = ["Cloud", "cloud", "云", ]
    network_c = ["网络", "网络运维", "网络安全", "网络运营", "网络管理", "网络架构", "网络搭建", "光网络", "网络维护", ]
    
    search_sql = """select job_name,salary salary from {}""".format(db_name)
    cursor.execute(search_sql)
    for fetch in cursor.fetchall():
        job_name = fetch[0]
        salary = salary_fenxi(fetch[1])
        # 判断职位关键词
        if condition(job_name, java_c):
            positions.append('java')
            if salary is not None:
                java_s.append(salary[0])
                java_s.append(salary[1])
        if condition(job_name, c_c):
            positions.append('c')
            if salary is not None:
                c_s.append(salary[0])
                c_s.append(salary[1])
        if condition(job_name, html_c):
            positions.append('html')
            if salary is not None:
                html_s.append(salary[0])
                html_s.append(salary[1])
        if condition(job_name, python_c):
            positions.append('python')
            if salary is not None:
                python_s.append(salary[0])
                python_s.append(salary[1])
        if condition(job_name, php_c):
            positions.append('php')
            if salary is not None:
                php_s.append(salary[0])
                php_s.append(salary[1])
        if condition(job_name, big_data_c):
            positions.append('big_data')
            if salary is not None:
                big_data_s.append(salary[0])
                big_data_s.append(salary[1])
        if condition(job_name, rgzn_c):
            positions.append('rgzn')
            if salary is not None:
                rgzn_s.append(salary[0])
                rgzn_s.append(salary[1])
        if condition(job_name, ios_c):
            positions.append('ios')
            if salary is not None:
                ios_s.append(salary[0])
                ios_s.append(salary[1])
        if condition(job_name, android_c):
            positions.append('android')
            if salary is not None:
                android_s.append(salary[0])
                android_s.append(salary[1])
        if condition(job_name, net_c):
            positions.append('net')
            if salary is not None:
                net_s.append(salary[0])
                net_s.append(salary[1])
        if condition(job_name, node_c):
            positions.append('node')
            if salary is not None:
                node_s.append(salary[0])
                node_s.append(salary[1])
        if condition(job_name, database_c):
            positions.append('database')
            if salary is not None:
                database_s.append(salary[0])
                database_s.append(salary[1])
        if condition(job_name, suanfa_c):
            positions.append('suanfa')
            if salary is not None:
                suanfa_s.append(salary[0])
                suanfa_s.append(salary[1])
        if condition(job_name, small_app_c):
            positions.append('small_app')
            if salary is not None:
                small_app_s.append(salary[0])
                small_app_s.append(salary[1])
        if condition(job_name, yunwei_c):
            positions.append('yunwei')
            if salary is not None:
                yunwei_s.append(salary[0])
                yunwei_s.append(salary[1])
        if condition(job_name, qianrushi_c):
            positions.append('qianrushi')
            if salary is not None:
                qianrushi_s.append(salary[0])
                qianrushi_s.append(salary[1])
        if condition(job_name, auto_c):
            positions.append('auto')
            if salary is not None:
                auto_s.append(salary[0])
                auto_s.append(salary[1])
        if condition(job_name, qukuailian_c):
            positions.append('qukuailian')
            if salary is not None:
                qukuailian_s.append(salary[0])
                qukuailian_s.append(salary[1])
        if condition(job_name, cloud_c):
            positions.append('cloud')
            if salary is not None:
                cloud_s.append(salary[0])
                cloud_s.append(salary[1])
        if condition(job_name, system_c):
            positions.append('system')
            if salary is not None:
                system_s.append(salary[0])
                system_s.append(salary[1])
        if condition(job_name, network_c):
            positions.append('network')
            if salary is not None:
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

    # x轴
    x = []
    # 岗位数量轴
    count_y = []
    # 收入轴
    salary_y = []
    # 分析岗位数量列表数据
    positions_dict = dict(Counter(positions))
    positions_list = list(Counter(positions))
    for position in positions_list:
        x.append(locals()[position + '_c'][0])
        count_y.append(positions_dict[position])
        salary_y.append(cout_fun.avg(locals()[position + '_n'], locals()[position + '_s']))

    # 调用绘图函数
    if mode == 'pyechart':
        # 排序
        data1 = [(type_name, type_count) for type_name, type_count in zip(count_y, x)]
        data1.sort(reverse=True)
        x1 = [type_count for type_name, type_count in data1]
        y1 = [type_name for type_name, type_count in data1]
        data2 = [(type_name, type_salary) for type_name, type_salary in zip(salary_y, x)]
        data2.sort(reverse=True)
        x2 = [type_salary for type_name, type_salary in data2]
        y2 = [type_name for type_name, type_salary in data2]
        values = {"岗位数量（个）": y1, "收入水平（K）": y2}
        draw_fun.echart(x1=x1, x2=x2, values=values, title="{}地区IT行业部分技术岗位某招聘网站岗位数量与平均收入水平(不完全统计) ".format(city), save_path=save_path)
    elif mode == 'plt':
        # 排序
        data1 = [(type_name, type_count, salary) for type_name, type_count, salary in zip(count_y, x, salary_y)]
        data1.sort(reverse=True)
        count1 = [type_name for type_name, type_count, salary in data1]
        name1 = [type_count for type_name, type_count, salary in data1]
        salary1 = [salary for type_name, type_count, salary in data1]
        draw_fun.plt_func(x=name1, y=count1, y2=salary1, title="{}地区IT行业部分技术岗位某招聘网站岗位数量与平均收入水平(不完全统计) ".format(city), show=show, save=save, save_path=save_path)
    cursor.close()
    db.close()
