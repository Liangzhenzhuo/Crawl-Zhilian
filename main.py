import matplotlib.pyplot as plt
from json import loads
from re import search, IGNORECASE, findall
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from pymysql import connect
from pymysql.err import ProgrammingError
from requests import Session

# 构造随机请求头
header = {"User-Agent": UserAgent().random}
# 连接数据库
db = connect("localhost", "root", "o9ptZVkJib9p", "zhilian")
# 创建游标对象
cursor = db.cursor()
session = Session()


def zhilian_crawler(city, city_num, db_name):
    zhilian_url = "https://www.zhaopin.com/{}/".format(city)
    zhilian_get = session.get(zhilian_url, headers={"User-Agent": UserAgent().random})
    zhilian_bs = bs(zhilian_get.text, features="html.parser")
    posistions = zhilian_bs.select(
        ".zp-jobNavigater__list li .zp-jobNavigater__pop a")
    for posistion in posistions:
        posistion_title = posistion.text
        # 大概看了一下基本上没有哪个行业招聘信息超过5页，所以range(5)够用了
        for page in range(5):
            # 拼接请求url
            posistion_href = "https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=90&cityId={}&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3&_v=0.32608946&x-zp-page-request-id=dbb76be8d2494593b499fc44b1acd457-1553612808344-306559".format(
                page * 90, city_num, posistion_title)
            posistion_get = session.get(posistion_href, headers={"User-Agent": UserAgent().random})
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

# 工资分析函数
def salary_fenxi(string):
    if search("面议", string) or search("/", string) or search("以下", string) or search("校招", string):
        return None
    else:
        res = findall(r'(\d+(\.\d+)?)',string)
        return res[0][0], res[1][0]
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

# 绘图函数
def plt_func(x, y, y2, title):
    x_lable_font = {'weight': 'bold', 'size': 14}   #字体
    fig = plt.figure(figsize=(13.66, 7.68))     # 图表大小
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.xticks(rotation=45) # x轴文字旋转45度
    plt.title(title)    # 标题
    sub = plt.subplot(111)      # 生成子图一行一列占第一个
    a = sub.bar(x, y, label='岗位需求', width=-.4, color="lightskyblue", align='edge', edgecolor = 'white')
    plt.ylabel('就业岗位数量(个)', x_lable_font)    # 左边 y 轴 label
    sub2 = sub.twinx()  # 镜像一份生成右边的y轴
    b = sub2.bar(x, y2, label='收入水平', width=.4, color="yellowgreen", align='edge', edgecolor = 'white')
    autolabel(rects=a, foi='', unit='', who=sub)
    autolabel(rects=b, foi='float', unit='K', who=sub2)
    plt.xlabel('岗位名称', x_lable_font)        # x轴label
    plt.ylabel('收入水平(K)', x_lable_font)     # 右边 y 轴 label
    # plt.margins(.006)     # margins 内容和图表边框的距离
    fig.legend(bbox_to_anchor=(1,1), bbox_transform=sub.transAxes)      # 图例
    plt.savefig(title + ".png")     # 保存图片

# 求平均数函数
def avg(before, after):
    if len(after) == 0:
        return 0
    else:
        avg_res = round(before / len(after), 1)
        return avg_res

# 数据分析函数
def job_fenxi(db_name):
    """
    _s：保存工资数据列表
    _n：工资数据列表的sum
    什么都没有的：岗位数量
    """
    java = 0
    java_n = 0
    java_s = []
    c = 0
    c_n = 0
    c_s = []
    html = 0
    html_n = 0
    html_s = []
    php = 0
    php_n = 0
    php_s = []
    python = 0
    python_n = 0
    python_s = []
    big_data = 0
    big_data_n = 0
    big_data_s = []
    ios = 0
    ios_n = 0
    ios_s = []
    android = 0
    android_n = 0
    android_s = []
    net = 0
    net_n = 0
    net_s = []
    suanfa = 0
    suanfa_n = 0
    suanfa_s = []
    small_app = 0
    small_app_n = 0
    small_app_s = []
    rgzn = 0
    rgzn_n = 0
    rgzn_s = []
    database = 0
    database_n = 0
    database_s = []
    yunwei = 0
    yunwei_n = 0
    yunwei_s = []
    qianrushi = 0
    qianrushi_n = 0
    qianrushi_s = []
    auto = 0
    auto_n = 0
    auto_s = []
    node = 0
    node_n = 0
    node_s = []
    system = 0
    system_n = 0
    system_s = []
    qukuailian = 0
    qukuailian_n = 0
    qukuailian_s = []
    cloud = 0
    cloud_n = 0
    cloud_s = []
    network = 0
    network_n = 0
    network_s = []
    search_sql = """select job_name,salary salary from {}""".format(db_name)
    cursor.execute(search_sql)
    fetch_all = cursor.fetchall()
    for fetch in fetch_all:
        res = fetch[0]
        salary = salary_fenxi(fetch[1])
        # 判断职位
        if search("java", res, IGNORECASE):
            java += 1
            if salary != None:
                java_s.append(salary[0])
                java_s.append(salary[1])
        if search(r"c\+", res, IGNORECASE) or search("c#", res, IGNORECASE):
            c += 1
            if salary != None:
                c_s.append(salary[0])
                c_s.append(salary[1])
        if search("html", res, IGNORECASE) or search("前端", res) or search("web", res, IGNORECASE) or search("css", res, IGNORECASE) or search("seo", res, IGNORECASE):
            html += 1
            if salary != None:
                html_s.append(salary[0])
                html_s.append(salary[1])
        if search("python", res, IGNORECASE):
            python += 1
            if salary != None:
                python_s.append(salary[0])
                python_s.append(salary[1])
        if search("php", res, IGNORECASE):
            php += 1
            if salary != None:
                php_s.append(salary[0])
                php_s.append(salary[1])
        if search("大数据", res) or search("数据分析", res) or search("Hadoop", res, IGNORECASE) or search("数据挖掘", res) or search("爬虫", res):
            big_data += 1
            if salary != None:
                big_data_s.append(salary[0])
                big_data_s.append(salary[1])
        if search("人工智能", res) or search("ai", res, IGNORECASE) or search("人脸识别", res) or search("图像识别", res) or search("机器学习", res) or search("深度学习", res) or search("机器视觉", res) or search("计算机视觉", res):
            rgzn += 1
            if salary != None:
                rgzn_s.append(salary[0])
                rgzn_s.append(salary[1])
        if search("ios", res, IGNORECASE):
            ios += 1
            if salary != None:
                ios_s.append(salary[0])
                ios_s.append(salary[1])
        if search("android", res, IGNORECASE) or search("安卓", res, IGNORECASE):
            android += 1
            if salary != None:
                android_s.append(salary[0])
                android_s.append(salary[1])
        if search("net", res, IGNORECASE):
            net += 1
            if salary != None:
                net_s.append(salary[0])
                net_s.append(salary[1])
        if search("node.js", res, IGNORECASE):
            node += 1
            if salary != None:
                node_s.append(salary[0])
                node_s.append(salary[1])
        if search("数据库", res) or search("mysql", res, IGNORECASE) or search("oracle", res, IGNORECASE):
            database += 1
            if salary != None:
                database_s.append(salary[0])
                database_s.append(salary[1])
        if search("算法", res):
            suanfa += 1
            if salary != None:
                suanfa_s.append(salary[0])
                suanfa_s.append(salary[1])
        if search("小程序", res):
            small_app += 1
            if salary != None:
                small_app_s.append(salary[0])
                small_app_s.append(salary[1])
        if search("运维", res):
            yunwei += 1
            if salary != None:
                yunwei_s.append(salary[0])
                yunwei_s.append(salary[1])
        if search("嵌入", res):
            qianrushi += 1
            if salary != None:
                qianrushi_s.append(salary[0])
                qianrushi_s.append(salary[1])
        if search("自动化", res):
            auto += 1
            if salary != None:
                auto_s.append(salary[0])
                auto_s.append(salary[1])
        if search("区块链", res):
            qukuailian += 1
            if salary != None:
                qukuailian_s.append(salary[0])
                qukuailian_s.append(salary[1])
        if search("云", res):
            cloud += 1
            if salary != None:
                cloud_s.append(salary[0])
                cloud_s.append(salary[1])
        if search("系统", res) or search("linux", res, IGNORECASE) or search("centos", res, IGNORECASE) or search("debian", res, IGNORECASE):
            system += 1
            if salary != None:
                system_s.append(salary[0])
                system_s.append(salary[1])
        if search("网络工程", res) or search("网络运维", res) or search("网络安全", res) or search("网络运营", res) or search("网络管理", res) or search("网络架构", res) or search("光网络", res) or search("网络维护", res):
            network += 1
            if salary != None:
                network_s.append(salary[0])
                network_s.append(salary[1])

    c_n = sum(list(map(float, c_s)))
    network_n = sum(list(map(float, network_s)))
    java_n = sum(list(map(float, java_s)))
    php_n = sum(list(map(float, php_s)))
    python_n = sum(list(map(float, python_s)))
    html_n = sum(list(map(float, html_s)))
    big_data_n = sum(list(map(float, big_data_s)))
    ios_n = sum(list(map(float, ios_s)))
    android_n = sum(list(map(float, android_s)))
    net_n = sum(list(map(float, net_s)))
    suanfa_n = sum(list(map(float, suanfa_s)))
    small_app_n = sum(list(map(float, small_app_s)))
    rgzn_n = sum(list(map(float, rgzn_s)))
    database_n = sum(list(map(float, database_s)))
    yunwei_n = sum(list(map(float, yunwei_s)))
    qianrushi_n = sum(list(map(float, qianrushi_s)))
    auto_n = sum(list(map(float, auto_s)))
    system_n = sum(list(map(float, system_s)))
    node_n = sum(list(map(float, node_s)))
    qukuailian_n = sum(list(map(float, qukuailian_s)))
    cloud_n = sum(list(map(float, cloud_s)))
    
    # 规定x轴
    x = ['C语言', 'Java', 'PHP', 'Python', 'Web', '数据分析', 'IOS', 'Andriod', '.Net', '算法', '小程序', '人工智能', '数据库', '运维', '嵌入式', '自动化', '系统', 'Node.js', "区块链", '云', '网络']    
    # 规定y轴
    y1 = [c, java, php, python, html, big_data, ios, android, net, suanfa, small_app, rgzn, database, yunwei, qianrushi, auto, system, node, qukuailian, cloud, network]
    y2 = [avg(c_n, c_s), avg(java_n, java_s), avg(php_n, php_s), avg(python_n, python_s), avg(html_n, html_s), avg(big_data_n, big_data_s), avg(ios_n, ios_s), avg(android_n, android_s), avg(net_n, net_s), avg(suanfa_n, suanfa_s), avg(small_app_n, small_app_s), avg(rgzn_n, rgzn_s), avg(database_n, database_s), avg(yunwei_n, yunwei_s), avg(qianrushi_n, qianrushi_s), avg(auto_n, auto_s), avg(system_n, system_s), avg(node_n, node_s), avg(qukuailian_n, qukuailian_s), avg(cloud_n, cloud_s), avg(network_n, network_s)]
    # 排序
    data1=[(type_name, type_count, salary) for type_name, type_count, salary in zip(y1, x, y2)]
    data1.sort(reverse=True)
    count1=[type_name for type_name,type_count, salary in data1]
    name1=[type_count for type_name,type_count, salary in data1]
    salary1=[salary for type_name,type_count, salary in data1]
    plt_func(x=name1, y=count1, y2=salary1, title="南宁地区IT行业部分技术岗位招聘数量与平均收入水平统计（不完全统计）")

if __name__ == "__main__":
    # 爬取函数
    zhilian_crawler(city="beijing", city_num="530", db_name="beijing")
    # 结束后关闭游标、数据库连接
    cursor.close()
    db.close()
    # 数据分析函数
    job_fenxi(db_name="shenzhen")
