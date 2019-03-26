from requests import get
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from json import loads
from pymysql import connect
from re import search

# 构造随机请求头
header = {"User-Agent": UserAgent().random}
# 连接数据库
db = connect("localhost", "root", "o9ptZVkJib9p", "zhilian")
# 创建游标对象
cursor = db.cursor()


def work_crawler():
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


if __name__ == "__main__":
    work_crawler()
