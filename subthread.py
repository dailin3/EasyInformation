import threading
from crawlers import *
from db import *
from notification import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
    
scheduler = BackgroundScheduler()

def start_crawlers_threads():
    # to start add all crawlers into scheduler

    # TODO: add a setting from config function
    for crawler_inst in crawlers:
        if crawler_inst.status == "1":
            cron = CronTrigger().from_crontab(crawler_inst.cron)
            name = crawler_inst.name + "_thread"
            scheduler.add_job(crawler_inst.run, trigger= cron, id= name)
            print(name + " join to scheduler")
    scheduler.start()


class NotificationThread():
    # to clear the notifications table
    def init(self):
        self.is_alive = False
        self.thread = threading.Thread(target=self.start_loop, name='notification_thread')
        self.notifier = Notifier()
        self.interval = 1000  # TODO: Add interval setting

    def start_loop(self):
        while self.is_alive:
            self.send_notifications()
            self.thread.wait(self.interval)
            
    def send_notifications(self):
        # TODO: Add time judgement
        database.connect()
        notifications = Notifications.select().where(Notifications.is_announced == 0)
        for notification in notifications:
            self.notifier.send(notification.to_notification)
            notification.is_announced = 1
            notification.save()
        database.close()

