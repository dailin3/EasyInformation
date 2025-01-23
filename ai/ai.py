from .plugins import doubao as doubao
from db import *

default_ai = '豆包'
def get_ai(ai_name = default_ai):
    if ai_name == '豆包':
        return doubao.AI_Tool(),doubao.AI_Brain(),doubao.AI_Do()
    else:
        raise ValueError('Invalid AI name')
