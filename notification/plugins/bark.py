import requests
from ..notification import Notification

class BarkNotification():
    inportant_payload = {
        'level' : 'critical',
        'sound' : 'alarm',
        'call' : '1',
        'badge' : '1',
        'volume' : '8',
    }

    normal_payload = {
        'level' : 'active',
        'sound' : 'glass',
    }

    silence_payload = {
        'level' : 'passive',
        'sound' : 'newmail',
    }

    def __init__(self,token):
        self.name = 'bark'
        self.token = token
        self.url = f"https://api.day.app/{token}/"

    def send(self,notification: Notification):
        level = notification.level
        if level == 3:
            payload = self.inportant_payload
        elif level == 2:
            payload = self.normal_payload
        elif level == 1:
            payload ={}
        elif level == 0:
            payload = self.silence_payload
        else:
            payload = self.silence_payload
        if notification.group:
            payload['group'] = notification.group
        if notification.url:
            payload['url'] = notification.url

        res=requests.get(self.url + notification.title + '/' +  notification.content , params=payload)

        if res.status_code == 200:
            return True
        else:
            return False
