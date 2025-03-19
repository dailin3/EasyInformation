import json
import importlib.util
import config as config, os
from abc import ABC, abstractmethod

default_interval = 60
crawlers = []

class Crawler(ABC):
    '''
    规范爬虫，用于后续ai操作。
    爬虫的基类，所有爬虫都应该继承此类。这关系到爬虫的注册和查找，如果不继承此类，将无法注册和查找
    注意：1.子类必须实现run方法，否则会报错。
         2.每一个爬虫脚本文件只能有一个爬虫类，后续的爬虫类不会被查找。
         3.子类必须有name, script_location属性，用来注册和查找。
         4.子类可以有description, status属性，用来描述爬虫的信息。
         5.子类可以有其他属性，但是不会被注册和查找。
    '''

    # 爬虫的名字，用于查找
    def __init__(self):
        self.name = 'parent_crawler'
        self.description = 'default description'
        self.status = '0'
        self.interval = default_interval
        self.cron = "0 0 * * *"

    #每个爬虫都应该实现run方法，否则会报错，这里是一个抽象方法，子类必须实现
    @abstractmethod 
    def run(self):
        pass

def register(crawler: Crawler) -> None:
    '''
    将爬虫注册到crawlers列表中，方便后续查找。
    '''
    if not isinstance(crawler, Crawler):
        raise ValueError("crawler must be an instance of Crawler")
    crawlers.append(crawler)

def auto_register_crawlers() -> None:
    plugins_path = os.path.join(config.CWD, 'crawlers/plugins')
    for filename in os.listdir(plugins_path):
        if filename.endswith('.py'):
            script_location = os.path.join(plugins_path, filename)
            module_name = f"crawler_module_{filename[:-3]}"
            spec = importlib.util.spec_from_file_location(module_name, script_location)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for cls_name, cls_obj in module.__dict__.items():
                if isinstance(cls_obj, type) and hasattr(cls_obj, '__bases__') and issubclass(cls_obj, Crawler) and cls_obj is not Crawler and cls_name != 'Crawler':
                    if 'run' in cls_obj.__dict__ and callable(cls_obj.run):
                        instance = cls_obj()
                        register(instance)

auto_register_crawlers()