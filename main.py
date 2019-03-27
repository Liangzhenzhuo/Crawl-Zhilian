from requests import get, Session
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from json import loads
from pymysql import connect
from re import search
from requests.adapters import HTTPAdapter

# 构造随机请求头
header = {"User-Agent": UserAgent().random}
# 连接数据库
db = connect("localhost", "root", "o9ptZVkJib9p", "zhilian")
# 创建游标对象
cursor = db.cursor()


def zhilian_crawler():
    zhilian_url = "https://www.zhaopin.com/nanning/"
    zhilian_get = get(zhilian_url, headers=header)
    zhilian_bs = bs(zhilian_get.text, features="html.parser")
    posistions = zhilian_bs.select(
        ".zp-jobNavigater__list li .zp-jobNavigater__pop a")
    for posistion in posistions:
        posistion_title = posistion.text
        # 大概看了一下基本上没有哪个行业招聘信息超过5页，所以range(5)够用了
        for page in range(5):
            # 拼接请求url
            posistion_href = "https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=90&cityId=785&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3&_v=0.32608946&x-zp-page-request-id=dbb76be8d2494593b499fc44b1acd457-1553612808344-306559".format(
                page * 90, posistion_title)
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
                # 拼接查询sql语句
                search_sql = """select * from job where job_name='{}' and company_name='{}'""".format(
                    job_name, company_name)
                # 如果数据已经存在 跳过
                if cursor.execute(search_sql) != 0:
                    continue
                else:
                    # 拼接插入sql语句
                    insert_sql = """insert into job(city, salary, welfare, empl_type, job_name, company_name, company_type, company_size, edu_level, business_area, working_exp) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(
                        city, salary, welfare, empl_type, job_name, company_name, company_type, company_size, edu_level, business_area, working_exp)
                    # 执行sql语句
                    cursor.execute(insert_sql)
                    # 提交操作
                    db.commit()
                    print(job_info)


def crawler_51_iob():
    page = 1
    while True:
        job_51_url = "https://jobs.51job.com/nanning/p{}".format(page)
        job_51_get = get(job_51_url, headers=header)
        job_51_bs = bs(job_51_get.text, features="html.parser")
        posistion_block = job_51_bs.select('.detlist .e')
        if len(posistion_block) == 0:
            return
        for posistion in posistion_block:
            job_name = posistion.select_one("span a")['title']  # 职位名称
            company_name = posistion.select_one(".name")['title']  # 公司名称
            if search("'", company_name):
                company_name = company_name.replace("'", '')
            city = posistion.select_one("span.name").text  # 城市
            salary = posistion.select("span.location")[-1].text  # 工资
            order = posistion.select_one("p.order").text
            edu_level = order[order.index('学历要求') + 5:order.index("工作经验") - 1]  # 学历要求
            working_exp = order[order.index('工作经验') + 5:order.index("公司性质") - 1].replace("-", '至')  # 工作经验
            company_type = order[order.index('公司性质') + 5:order.index("公司规模") - 1]  # 公司性质
            company_size = order[order.index('公司规模') + 5: -1].replace("-", '至').strip('\t')  # 公司规模
            job_des = posistion.select_one("p.text")['title']  # 职位描述
            job_info = [job_name, company_name, city, salary,edu_level, working_exp, company_type, company_size]
            search_sql = """select * from job where job_name='{}' and company_name='{}'""".format(
                job_name, company_name)
            if cursor.execute(search_sql) != 0:
                continue
            else:
                insert_sql = """insert into job(job_name, company_name, city, salary, edu_level, working_exp, company_type, company_size, job_des) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(
                        job_name, company_name, city, salary, edu_level, working_exp, company_type, company_size, job_des)
                try:
                    cursor.execute(insert_sql)
                    db.commit()
                    print(job_info)
                except:
                    continue
        page += 1

def liepin():
    session = Session()
    session.mount('http://', HTTPAdapter(max_retries=2))
    session.mount('https://', HTTPAdapter(max_retries=2))
    liepin_url = "https://www.liepin.com/it/"
    liepin_get = session.get(liepin_url, headers=header)
    liepin_bs = bs(liepin_get.text, features="html.parser")
    for posistion in liepin_bs.select(".sidebar li dl dd a"):
        pager_get = session.get("https://www.liepin.com/zhaopin/?imscid=R000000035&key={}&dqs=110020".format(posistion.text))
        if search("pagerbar", pager_get.text):
            pager_bs = bs(pager_get.text, features="html.parser")
            page_num = pager_bs.select_one("div.pagerbar a.last")['href'].split("&")[-1].split("=")[-1]
        else:
            page_num = 0
        for page in range(int(page_num) + 1):
            job_page_get = session.get("https://www.liepin.com/zhaopin/?imscid=R000000035&key={}&dqs=110020&curPage={}".format(posistion.text, page))
            job_page_bs = bs(job_page_get.text, features="html.parser")
            job_block = job_page_bs.select(".sojob-list .sojob-item-main")
            for job in job_block:
                job_name = job.select_one("h3").text.strip()
                salary = job.select_one("p.condition span.text-warning").text
                city = "南宁"
                business_area = job.select_one("p.condition .area").text
                edu_level = job.select_one("p.condition span.edu").text
                working_exp = job.select("p.condition span")[-1].text
                company_name = job.select_one(".company-info p.company-name").text.strip()
                company_type = job.select_one(".company-info p.field-financing").text.strip()
                welfare = ''
                for e in job.select(".company-info p.temptation span"):
                    welfare += e.text + '/'
                source = "猎聘"
                job_href = job.select_one(".job-info h3 a")['href']
                if not search("http", job_href):
                    job_href = "https://www.liepin.com" + job_href
                job_more_get = session.get(job_href)
                job_more_bs = bs(job_more_get.text, features="html.parser")
                job_des = job_more_bs.select_one(".job-description .content").text.strip()
                search_sql = """select * from job where job_name='{}' and company_name='{}'""".format(
                    job_name, company_name)
                if cursor.execute(search_sql) != 0:
                    continue
                else:
                    insert_sql = """insert into job (job_name, salary, city, business_area, edu_level, working_exp, company_name, company_type, welfare, job_des, source) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(job_name, salary, city, business_area, edu_level, working_exp, company_name, company_type, welfare, job_des, source)
                    cursor.execute(insert_sql)
                    db.commit()
                    print(job_name)


if __name__ == "__main__":
    liepin()
    cursor.close()
    db.close()
 
