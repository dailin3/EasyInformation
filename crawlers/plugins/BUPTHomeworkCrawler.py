from db import *
from crawlers.crawlers import Crawler
import config as config
from crawlers.plugins.BUPTCAS import CAS

import time, requests
from urllib.parse import urlparse, parse_qs, quote
from datetime import datetime, timedelta
from base64 import b64encode


user_name = config.BUPT_USERNAME
password = config.BUPT_PASSWORD
url_all_course = "https://apiucloud.bupt.edu.cn/ykt-site/site/list/student/current?size=999&userId="
url_work_per_course = "https://apiucloud.bupt.edu.cn/ykt-site/work/student/list"
url_assignment = "https://apiucloud.bupt.edu.cn/ykt-site/work/detail?assignmentId="

class BUPTHomeWorkCrawler(Crawler):
    """
    爬取bupt作业的信息
    对于作业的爬取，涉及到对js的处理和对网页的解析，因此使用selenium进行爬取。
    爬取的信息包括：
    - 作业
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = 'bupt_homework_crawler'
        self.description = '爬取bupt作业的信息'
        self.status = '1'
        self.login_url ="https://auth.bupt.edu.cn/authserver/login?service=http://ucloud.bupt.edu.cn"
        self.token_url = "https://apiucloud.bupt.edu.cn/ykt-basics/oauth/token"
        self.info_url = "https://apiucloud.bupt.edu.cn/ykt-basics/info"
        self.current_url = "https://apiucloud.bupt.edu.cn/ykt-site/base-term/current"
        self.user_url = "https://apiucloud.bupt.edu.cn/ykt-basics/userroledomaindept/listByUserId"
        self.check_url = "https://apiucloud.bupt.edu.cn/blade-portal/home-page-info/getShufflingWebList"
        self.cron = "*/20 * * * *"

    def run(self):
        """
        执行BUPTHomeworkCrawler的主要逻辑。
        该方法执行以下步骤：
        1. 使用get_cookies方法获取cookies。
        2. 解析cookies以提取headers和UUID。
        3. 使用get_all_course方法获取所有课程ID。
        4. 遍历每门课程并使用get_unfinished_per_course方法获取未完成的作业。
        返回:
            None
        """
        self._login()

        print(self.name + " start running")
        uuid = self.user_id
        headers = {
            "Authorization": self.authorization,
            "Blade-Auth": self.access_token
        }
        course_id = self.get_all_course(uuid=uuid,headers=headers)
        database.connect()
        for course_name,course_id in course_id.items():
            assignment_info = self.get_unfinished_per_course(course_id,course_name,uuid,headers)
            for job in assignment_info:
                resources = {}
                for resource in job['assignmentResource']:
                    resources[resource['resourceName']] = resource['resourceId']
                Assignments.get_or_create(
                    assignment_content = job['assignmentContent'],
                    assignment_end_time = job['assignmentEndTime'],
                    assignment_resource = str(resources),
                    assignment_status = job['assignmentStatus'],
                    assignment_title = job['assignmentTitle'],
                    assignment_type = job['assignmentType'],
                    chapter_name = job['chapterName'],
                    course_id = job['courseId'],
                    course_name = job['courseName'],
                    href = f"https://ucloud.bupt.edu.cn/uclass/course.html#/student/assignmentDetails_fullpage?activeTabName=first&assignmentId={job["id"]}",
                    is_open_evaluation = job['isOpenEvaluation'],
                    is_over_time = job['isOverTime'],
                    status = job['status'],
                    submit_time = job['submitTime']
                )
        database.close()
        print("作业爬取完成")

    def get_assginment_detail(self,assignment_id,headers):
        '''
        获取作业的详细信息
        该函数用于获取作业的详细信息，包括作业内容和作业资源。
        参数:
            assignment_id: 作业ID
            headers: 请求头
        返回值:
            返回一个元组，包含作业内容和作业资源。
            '''
        response = self.session.get(url_assignment+assignment_id,headers=headers)
        data = response.json()["data"]
        content = data["assignmentContent"]
        resources=data['assignmentResource']
        return content,resources

    def get_unfinished_per_course(self,course_id,course_name,uuid,headers):
        '''
        获取每门课程的未完成作业
        该函数用于获取每门课程的未完成作业。
        参数:
            course_id: 课程ID
            course_name: 课程名称
            uuid: 用户ID
            headers: 请求头
        返回值:
            返回一个列表，包含未完成的作业信息。
            列表中每个元素是一个字典，包含以下字段:
                - courseName: 课程名称
                - courseId: 课程ID
                - id: 作业ID
                - assignmentEndTime: 作业截止时间
                - assignmentTitle: 作业标题
                - submitTime: 提交时间
                - isOpenEvaluation: 是否开启评价
                - status: 是否逾期
                - assignmentStatus: 作业状态
                - chapterName: 章节名称
                - assignmentType: 作业类型
                - isOverTime: 是否逾期
                - assignmentContent: 作业内容
                - assignmentResource    作业资源
        '''
        payload = {
            "siteId": course_id,
            "userId": uuid,
            "current": 1
        }
        response = self.session.post(url_work_per_course, json=payload,headers=headers)
        data = response.json()
        records = data['data']['records']
        unsubmitted_jobs = []
        for record in records:
            submit_time_str = record['submitTime']
            if submit_time_str == "":
                details = self.get_assginment_detail(record['id'],headers)
                content = details[0]
                resources = details[1]
                job_info = {
                    "courseName": course_name,
                    "courseId": course_id,
                    "id": record['id'],
                    "assignmentEndTime": record['assignmentEndTime'],
                    "assignmentTitle": record['assignmentTitle'],
                    "submitTime": record['submitTime'],
                    "isOpenEvaluation": record['isOpenEvaluation'],
                    "status": record['status'],
                    "assignmentStatus": record['assignmentStatus'],
                    "chapterName": record['chapterName'],
                    "assignmentType": record['assignmentType'],
                    "isOverTime": record['isOverTime'],
                    "assignmentContent": content,
                    "assignmentResource": resources
                }
                unsubmitted_jobs.append(job_info)
        return unsubmitted_jobs

    def get_all_course(self,uuid,headers) -> list:
        '''
        获取所有课程
        该函数用于获取所有课程。
        参数:
            uuid: 用户ID
            headers: 请求头
        返回值:
            返回一个字典，包含课程名称和课程ID。
        '''
        course = list(self.session.get(url_all_course+uuid,headers=headers).json()["data"]["records"])
        course_id = {}
        for c in course:
            course_id[c["siteName"]] = c["id"]
        return course_id
    
    def _login(self):
        self.session = CAS()
        self.authorization = "Basic " + b64encode("portal:portal_secret".encode()).decode()
        resp = self.session.get(self.login_url)
        self.ticket = parse_qs(urlparse(resp.url).query)["ticket"][0]
        resp = self.session.post(
            self.token_url,
            headers={
                "Authorization": self.authorization,
            },
            data={
                "ticket": self.ticket,
                "grant_type": "third"
            }
        )
        data = resp.json()
        print(data)
        self.user_id = data["user_id"]
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.role_name = data["role_name"]
        self.loginId = data["loginId"]
        self.user_name = data["user_name"]
        self.real_name = data["real_name"]
        self.avatar = data["avatar"]
        self.dept_id = data["dept_id"]
        self.identity = f"{self.role_name}:{self.dept_id}"
        self._get_cookies()
    
    def _get_cookies(self):
        info = self.session.get(
            self.info_url,
            headers={
                "Authorization": self.authorization,
                "Blade-Auth": self.access_token
            }
        ).json()["data"]
        current = self.session.get(
            self.current_url,
            headers={
                "Authorization": self.authorization,
                "Blade-Auth": self.access_token
            }
        ).json()["data"]
        user = self.session.get(
            self.user_url,
            headers={
                "Authorization": self.authorization,
                "Blade-Auth": self.access_token
            }
        ).json()["data"]

        cookies = {}
        cookies["iClass-uuid"] = self.user_id
        cookies["iClass-token"] = self.access_token
        cookies["iClass-refresh_token"] = self.refresh_token
        cookies["iClass-login-meth"] = "icloud"
        cookies["iClass-expert-account"] = self.user_name
        cookies["iClass-real_name"] = quote(self.real_name)
        cookies["iClass-role_name"] = self.role_name
        cookies["iClass-avatar"] = self.avatar
        cookies["iClass-loginId"] = self.loginId
        cookies["iClass-user-info"] = quote(str(info))
        cookies["iClass-current-term"] = quote(str(current))
        cookies["iClass-identity"] = self.identity
        cookies["iClass-user-role"] = quote(str(user[0]))
        cookies["iClass-login-roles"] = quote(str(user))

        for cookie in cookies:
            self.session.cookies.set(
                name=cookie,
                value=cookies[cookie],
                domain="ucloud.bupt.edu.cn",
                expires=(datetime.now() + timedelta(hours=1)).timestamp()
            )

if __name__ == '__main__':
    c = BUPTHomeWorkCrawler()
    c.run()