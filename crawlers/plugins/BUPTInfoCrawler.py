from db import *
from crawlers.crawlers import Crawler
import tool.config as config
from crawlers.plugins.BUPTCAS import CAS

import requests,time
from bs4 import BeautifulSoup
from ai.ai import get_ai
from notification import Notifier,Notification


user_name = config.BUPT_USERNAME
password = config.BUPT_PASSWORD

class BUPTInfoCrawler(Crawler):
    '''
    爬取bupt信息门户的信息
    考虑到信息门户的CAS verify问题，暂时不使用requests，而是使用selenium获得session，然后使用session发送请求。
    爬取的信息包括：
    - 校内通知
    '''

    def __init__(self) -> None:
        super().__init__()
        self.name = 'bupt_info_crawler'
        self.description = '爬取bupt信息门户的信息'
        self.status = '0'
        self.url = 'http://my.bupt.edu.cn/xs_index.jsp?urltype=tree.TreeTempUrl&wbtreeid=1541'
        self.main_page = 'http://my.bupt.edu.cn/'
        self.ai_tool,_,_  = get_ai()
        self.cron = "*/10 * * * *"
        self.notifier = Notifier()
        self.session = CAS()
        # redirect to main page
        self.session.get(self.url)

    def run(self):
        '''
        运行爬虫

        该函数用于运行爬虫，爬取信息门户的信息，并将其存入数据库中。

        参数:
            无

        返回值:
            无
        '''
        print(self.name + " start running")

        # 获取信息列表
        info_list = self.get_info_list()

        # 将信息内容写入info_list
        for info_element in info_list:
            info_element = self.write_info_content(info_element)
            print(info_element)

        # 将信息存入数据库
        self.save_info_list(info_list)

    def save_info_list(self, info_list: list) -> None:
        database.connect()
        for info in info_list:
            # use ai to parse the info
            summary = self.ai_tool.summerize(info['content'])
            importance = self.ai_tool.parse_importance(summary)
            group = self.ai_tool.parse_category(summary)

            # parse the notification level
            if importance < 25:
                level = 0
            elif importance < 50:
                level = 1
            elif importance < 75:
                level = 2
            else:
                level = 3
            # use href unique tag to check if the info exist in db, and save the new info
            info_db, created=Info.get_or_create(
                crawler_name=info['crawler_name'],
                href=info['href'],
                defaults={
                    'title': info['title'],
                    'author': info['author'],
                    'time': info['time'],
                    'crawler_name': info['crawler_name'],
                    'crawler_time': info['crawler_time'],
                    'content': info['content'],
                    'href': info['href'],
                    'type': info['type'],
                    'discription': info['discription'],
                    'importance': importance,
                    'summary': summary,
                    'group': group,
                    'is_read': 1
                }
            )
            # if not exist in DB
            if created:
                self.notifier.send(Notification(
                    title=info['title'],
                    content=summary,
                    level=level,
                    group=group,
                    url=info['href']
                ))
                print(f"send the message: {info['title']}")
            print(f"Saved {info['title']} to database.")
        database.close()
        
    def get_info_list(self) -> list:
        '''
        获取信息列表

        该函数用于获取信息门户网站的信息列表，并返回一个包含信息的列表。

        参数:
            cookies (dict): 包含cookies的字典，用于请求网页时的身份验证。

        返回值:
            返回一个包含信息的列表，每个信息以字典形式表示，包含以下字段:
                - 'crawler_name': 爬虫名称
                - 'type': 类型  文本/html
                - 'href': 链接
                - 'title': 标题
                - 'author': 作者
                - 'time': 时间
                - 'crawler_time': 爬取时间
                - 'readed': 是否已读
                - 'summary': 摘要
                - 'importance': 重要性
                - 'content': 内容
                - 'discription': 描述,额外的备注
        '''

        # 发送GET请求，获取网页内容
        response = self.session.get(self.url)
        print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_element = soup.find_all('a')
        for a_tag in a_element:
            if a_tag and a_tag.text == '校内通知':
                target_element = a_tag
                break
        
        url =self.main_page+target_element['href']
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_elements = soup.find('ul', class_='newslist').find_all('li')
        info_list = []
        for tr_element in tr_elements:
            crawler_name = self.name
            type = 'text'
            href = self.main_page + tr_element.find('a').get('href')
            title = tr_element.find('a').text
            author = tr_element.find('span', class_='author').text
            time = tr_element.find('span', class_='time').text
            crawler_time = self.get_time()
            discription = ''
            row = {
                'crawler_name': crawler_name,
                'type': type,
                'href': href,
                'title': title,
                'author': author,
                'time': time,
                'crawler_time': crawler_time,
                'discription': discription
            }
            info_list.append(row)
        return info_list
    
    def write_info_content(self, info_element:dict) -> dict:
        '''
        爬取信息门户的信息内容

        该函数用于爬取信息门户网站的信息内容，并将其添加到传入的字典info_element中。

        参数:
            info_element (dict): 包含信息元素的字典，需要包含键值对 'href' 和 'content'。
            cookies (dict): 包含cookies的字典，用于请求网页时的身份验证。

        返回值:
            返回更新后的info_element字典，包含了爬取到的信息内容。
        '''

        # 发送GET请求，获取网页内容
        response = self.session.get(info_element['href'])
        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析网页，获取信息内容
        content_list = []
        content = soup.find('div', class_='v_news_content')
        for elem in content.children:
            if elem.name == 'p':
                content_list.append({"type":"p","content":elem.text})
            elif elem.name == 'img':
                content_list.append({"type":"img","href":elem['src']})
            elif elem.name == 'a':
                content_list.append({"type":"a","href":elem['href'],"content":elem.text})
        

        # 将信息内容添加到info_element字典中
        info_element['content'] = content_list

        return info_element
    
    def get_time(self):
        '''
        获取当前时间

        该函数用于获取当前时间，并以指定的格式返回。

        参数:
            无

        返回值:
            返回一个字符串，表示当前时间，格式为"%Y-%m-%d %H:%M:%S"。
        '''
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

if __name__ == '__main__':
    c = BUPTInfoCrawler()
    c.run()