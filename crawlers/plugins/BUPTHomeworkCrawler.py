from db import *
from crawlers.crawlers import Crawler
import config 
from notification import Notifier,Notification

import time, requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta

user_name = config.BUPT_USERNAME
password = config.BUPT_PASSWORD
url_all_course = "https://apiucloud.bupt.edu.cn/ykt-site/site/list/student/current?size=9999&userId="
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
        self.url = 'https://ucloud.bupt.edu.cn/'
        self.cron = "*/20 * * * *"
        self.notifier = Notifier()

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
        print(self.name + " start running")
        cookies = self.get_cookies()
        info = BUPTHomeWorkCrawler.parse_cookies(cookies)
        headers = info['header']
        uuid = info['uuid']
        course_id = self.get_all_course(uuid=uuid,headers=headers)
        if database.is_closed:
            database.connect()
        for course_name,course_id in course_id.items():
            assignment_info = self.get_unfinished_per_course(course_id,course_name,uuid,headers)
            for job in assignment_info:
                work, created = Assignments.get_or_create(
                    assignment_id = str(job["assignment_id"]),
                    assignment_content = job['assignmentContent'],
                    assignment_end_time = job['assignmentEndTime'],
                    assignment_begin_time = job['assignmentBeginTime'],
                    assignment_status = job['assignmentStatus'],
                    assignment_title = job['assignmentTitle'],
                    assignment_type = job['assignmentType'],
                    chapter_name = job['chapterName'],
                    course_name = job['courseName'],
                    href = f"https://ucloud.bupt.edu.cn/uclass/course.html#/student/assignmentDetails_fullpage?activeTabName=first&assignmentId={job["assignment_id"]}",
                    status = job['status'],
                    submit_time = job['submitTime'],
                )

                self.do_notification(job,created,work)

        database.close()
        print(self.name + " stop running")

    
    def do_notification(self,job,created,work):
    # old homework operation: judge the ddl.
        if not created:
            # Compare assignment_end_time with the current time
            assignment_end_time = datetime.strptime(job['assignmentEndTime'], "%Y-%m-%d %H:%M")
            assignment_begin_time = datetime.strptime(job['assignmentBeginTime'], "%Y-%m-%d %H:%M")
            time_interval = assignment_end_time - assignment_begin_time
            time_remain = assignment_end_time - datetime.now()
            remain_time_per = time_remain/time_interval

            if (remain_time_per< 0.1) and work.notice_times <3:
                self.notifier.send(Notification(
                title=job['courseName']+"作业提交马上截止！",
                content="记得在"+job['assignmentEndTime']+"之前提交："+job['assignmentTitle'],
                level=3,
                group="作业提醒",
                url=f"https://ucloud.bupt.edu.cn/uclass/course.html#/student/assignmentDetails_fullpage?activeTabName=first&assignmentId={int(job["assignment_id"])}"
            ))
                work.notice_times += 1
                work.save()
                print(f"send the message about homework(50%): {job['assignmentTitle']}")

            if (remain_time_per< 0.5) and work.notice_times <2:
                self.notifier.send(Notification(
                title=job['courseName']+"作业提交时间已经过半！",
                content="记得在"+job['assignmentEndTime']+"之前提交："+job['assignmentTitle'],
                level=2,
                group="作业提醒",
                url=f"https://ucloud.bupt.edu.cn/uclass/course.html#/student/assignmentDetails_fullpage?activeTabName=first&assignmentId={int(job["assignment_id"])}"
            ))
                work.notice_times += 1
                work.save()
                print(f"send the message about homework(50%): {job['assignmentTitle']}")
        # new homework notification
        else:
            self.notifier.send(Notification(
                title=job['courseName']+"作业来了！",
                content="记得在"+job['assignmentEndTime']+"之前提交："+job['assignmentTitle'],
                level=1,
                group="作业提醒",
                url=f"https://ucloud.bupt.edu.cn/uclass/course.html#/student/assignmentDetails_fullpage?activeTabName=first&assignmentId={job["assignment_id"]}"
            ))
            work.notice_times += 1
            work.save()
            print(f"send the message about homework(new): {job['assignmentTitle']}")


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
        response = requests.get(url_assignment+assignment_id,headers=headers)
        data = response.json()["data"]
        content = data["assignmentContent"]
        assignment_begin_time = data["assignmentBeginTime"]
        return {"content":content,
                "assignment_begin_time":assignment_begin_time}

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
        response = requests.post(url_work_per_course, json=payload,headers=headers)
        data = response.json()
        records = data['data']['records']
        unsubmitted_jobs = []
        for record in records:
            submit_time_str = record['submitTime']
            if submit_time_str == "":
                details = self.get_assginment_detail(record['id'],headers)
                content = details["content"]
                assignment_begin_time = details["assignment_begin_time"]
                job_info = {
                    "courseName": course_name,
                    "assignment_id": record['id'],
                    "assignmentEndTime": record['assignmentEndTime'],
                    "assignmentBeginTime": assignment_begin_time,
                    "assignmentTitle": record['assignmentTitle'],
                    "submitTime": record['submitTime'],
                    "status": record['status'],
                    "assignmentStatus": record['assignmentStatus'],
                    "chapterName": record['chapterName'],
                    "assignmentType": record['assignmentType'],
                    "assignmentContent": content,
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
        course = list(requests.get(url_all_course+uuid, headers=headers).json()["data"]["records"])
        course_id = {}
        for c in course:
            course_id[c["siteName"]] = c["id"]
        return course_id
    
    @staticmethod
    def parse_cookies(cookies:list) -> dict:
        '''
        解析cookies
        该函数用于解析cookies，提取请求头和UUID。
        参数:
            cookies: cookies
        返回值:
            返回一个字典，包含请求头和UUID。
        '''
        header = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31',
        }
        uuid = ''
        token = ''
        info = {}

        for cookie in cookies:
            if  cookie['name'] == 'iClass-token':
                token = cookie['value']
                header['Blade-Auth'] = cookie['value']
            if  cookie['name'] == 'iClass-uuid':
                uuid = cookie['value']

        info['header'] = header
        info['uuid'] = uuid
        info['token'] = token
        return info


    def get_cookies(self) -> list:
        '''
        获取cookies
        该函数用于获取cookies。
        参数:
            无
        返回值:
            返回一个列表，包含cookies。
        '''
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")  # 启用无头模式
        options.add_argument("--disable-gpu")  # 禁用GPU加速
        options.add_argument("--no-sandbox")  # 解决某些环境下的权限问题
        options.add_argument("--disable-dev-shm-usage")  # 解决资源受限问题
        excutable_path = config.CHROME_DRIVER_PATH
        service = Service(excutable_path)
        driver = webdriver.Chrome(options=options, service=service)
        driver.execute_script(f"window.open('{self.url}', '_blank');")
        time.sleep(3)   # 由于反爬机制，我们不能直接使用driver.get()方法，而是使用execute_script()方法打开新的标签页，推测因为太快切换标签页会被识别为机器人
        driver.switch_to.window(driver.window_handles[1])
        driver.switch_to.frame('loginIframe')
        password_login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-title"]/a[2]')))
        time.sleep(3)
        password_login.click()
        user_account_input = driver.find_element(By.ID, 'username')
        user_account_input.send_keys(user_name)
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys(password)
        login_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[3]/div[2]/div[7]/input')
        login_button.click()
        time.sleep(5)
        cookies = driver.get_cookies()
        driver.quit()
        return cookies
if __name__ == '__main__':
    c = BUPTHomeWorkCrawler()
    c.run()