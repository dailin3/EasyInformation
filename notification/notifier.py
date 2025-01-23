from .plugins import BarkNotification
from .notification import Notification
import tool.config as config

bark_token = config.BARK_TOKEN
defalt_clients = ['bark']

class Notifier():
    def __init__(self, clients = None):
        if clients is None:
            self.clients = get_clients(defalt_clients)
        else:
            self.clients = get_clients(clients)

    def send(self,notification: Notification):
        for client in self.clients:
            if client.name in notification.banned_clients:
                continue
            client.send(notification)

def get_client(name):
    if name == 'bark':
        return BarkNotification(bark_token)
    else:
        raise ValueError('Invalid client name')
    
def get_clients(names):
    for name in names:
        yield get_client(name)