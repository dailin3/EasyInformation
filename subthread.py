import threading
import config
from crawlers import *
from db import *
from notification import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
    
scheduler = BackgroundScheduler()

def start_crawlers_threads():
    # to start add all crawlers into scheduler

    # TODO: add a setting from config function
    for crawler_inst in crawlers:
        if crawler_inst.status == "1":
            cron = CronTrigger().from_crontab(crawler_inst.cron)
            name = crawler_inst.name + "_thread"
            scheduler.add_job(crawler_inst.run, trigger= cron, id= name, coalesce=True)
            print(name + " join to scheduler")
    scheduler.start()


class NotificationThread():
    # to clear the notifications table
    def __init__(self):
        self.is_alive = True
        self.thread = threading.Thread(target=self.loop, name='notification_thread')
        self.notifier = Notifier()
        self.interval = config.NOTIFICATION_INTERVAL  # TODO: Add interval setting

    def loop(self):
        while self.is_alive:
            self.send_notifications()
            time.sleep(self.interval)
    
    def start_loop(self):
        self.thread.start()
        print("notification thread started")
            
    def send_notifications(self):
        # TODO: Add time judgement
        database.connect()
        notifications = Notifications.select().where(Notifications.is_announced == 0)
        for notification in notifications:
            self.notifier.send(notification.to_notification)
            notification.is_announced = 1
            notification.save()
        database.close()

    def stop(self):
        self.is_alive = False
        self.thread.join()
        print("notification thread stoped")