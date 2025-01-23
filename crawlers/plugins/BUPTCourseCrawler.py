from db import *
from crawlers.crawlers import Crawler
import tool.config as config

import time, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import ChromiumOptions
from selenium.webdriver.chrome.webdriver import ChromiumDriver
from selenium.webdriver.support.ui import Select


class BUPTCourseCrawler(Crawler):
    """
    爬取bupt教务处的课表
    对于课表的爬取，涉及到对js的处理和对网页的解析，因此使用selenium进行爬取。
    爬取的信息包括：
    - 课表
    """
    def __init__(self):
        super().__init__()
        self.name = 'bupt_course_crawler'
        self.description = '爬取bupt教务处的课表'
        self.status = '0'
        self.url = 'https://jwgl.bupt.edu.cn/jsxsd/xskb/xskb_list.do'
        self.cron = "0 6 * * 1"
        

    def run(self):
        '''
        运行爬虫

        该函数用于运行爬虫，爬取教务处的课表，并将其存入数据库中。

        参数:
            无

        返回值:
            无
        '''
        print(self.name + " start running")
        chrome_options = ChromiumOptions()
        download_path = os.getcwd()+"/db/course/"
        prefs = {
            "download.default_directory": download_path,
            "download.preserve_filename": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        self.update_course(driver,download_path)


    def update_course(self,driver: ChromiumDriver,download_path: str):
        """
        更新课表,用selenuim进行模拟登录和下载，下载的文件为xls格式，需要转换为csv格式，存储在db/course文件夹下，文件名为周数类似于：'9.csv'。
        代码效率较低，需要优化，目前只能爬取当前周的课表，每周需要手动运行一次。我打算用schedule库来实现每周自动运行。
        """
        driver.get(self.url)
        user_account_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'userAccount')))
        user_account_input.send_keys(config.BUPT_USERNAME)
        password_input = driver.find_element(By.NAME, 'userPassword')
        password_input.send_keys(config.BUPT_PASSWORD)
        login_button = driver.find_element(By.CLASS_NAME, 'login_btn')
        login_button.click()
        # login

        driver.get('https://jwgl.bupt.edu.cn/jsxsd/framework/xsjsdPerson_zlxx.jsp')
        week=driver.find_element(By.XPATH,"/html/body/div[2]/h4[1]").text[3]
        print(f"正在下载第{week}周课表...")
        # get week

        driver.get(self.url)
        select_element = Select(driver.find_element(By.TAG_NAME,'select'))
        select_element.select_by_value(week)
        print_element = driver.find_element(By.ID , "dykb")
        print_element.click()
        time.sleep(3)
        print("课表下载完成！！！")
        # get course

        downloaded_file_path = download_path+f"学生个人课表_{config.BUPT_USERNAME}.xls"
        xls_file_path = os.path.join(download_path, f"{week}.xls")
        os.rename(downloaded_file_path, xls_file_path)
        df = pd.read_excel(xls_file_path)
        df.to_csv(download_path+f"{week}.csv", index=False)
        # convert to csv

        driver.quit()

if __name__ == '__main__':
    c = BUPTCourseCrawler()
    c.run()