from peewee import *
from typing import Optional
from notification import Notification

database = SqliteDatabase('db/main.db')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Assignments(BaseModel):
    id = AutoField(primary_key=True, column_name='id')
    course_name = TextField(column_name='courseName', null=True)
    assignment_end_time = TextField(column_name='assignmentEndTime', null=True)
    assignment_title = TextField(column_name='assignmentTitle', null=True)
    chapter_name = TextField(column_name='chapterName', null=True)
    assignment_content = TextField(column_name='assignmentContent', null=True)
    assignment_resource = TextField(column_name='assignmentResource', null=True)
    assignment_status = TextField(column_name='assignmentStatus', null=True)
    assignment_type = TextField(column_name='assignmentType', null=True)
    course_id = TextField(column_name='courseId', null=True)
    href = TextField(null=True)
    is_delete = IntegerField(column_name='isDelete', constraints=[SQL("DEFAULT 0")], null=True)
    is_open_evaluation = IntegerField(column_name='isOpenEvaluation', null=True)
    is_over_time = IntegerField(column_name='isOverTime', null=True)
    remark = TextField(null=True)
    status = IntegerField(null=True)
    submit_time = TextField(column_name='submitTime', null=True)

    class Meta:
        table_name = 'assignments'
        primary_key = False

class Info(BaseModel):
    id = AutoField(primary_key=True, column_name="id")
    author = TextField(null=True, column_name='author')
    content = TextField(null=True, column_name='content')
    crawler_name = TextField(null=True, column_name='crawler_name')
    crawler_time = TextField(null=True, column_name='crawler_time')
    discription = TextField(null=True, column_name='discription')
    href = TextField(unique=True, null=True, column_name='href')
    importance = FloatField(default=0,null=True, column_name='importance')
    is_deleted = IntegerField(default=0, null=True, column_name='is_deleted')
    is_read = IntegerField(default=0, null=True, column_name='readed')   #is readed by AI 0未读 1已读
    group = TextField(null=True, column_name='group')
    summary = TextField(null=True, column_name='summary')
    time = TextField(null=True, column_name='time')
    title = TextField(null=True, column_name='title')
    type = TextField(null=True, column_name='type')

    class Meta:
        table_name = 'info'

class Notifications(BaseModel):
    id = AutoField(primary_key=True, column_name="id")
    time = TextField(null= False , column_name="time")
    title = TextField(null=True, column_name="title")
    content = TextField(null= False, column_name= "content")
    level = IntegerField(null= False, column_name= "level")
    group = TextField(null= False, column_name= "group")
    is_announced = IntegerField(column_name='isAnnounced',default= 0, null=True)
    url = TextField(null= False, column_name= "url")
    is_deleted = IntegerField(column_name='isDeleted', default= 0, null=True)

    @property
    def to_notification(self):
        return Notification(title=self.title, content=self.content, level=self.level, group=self.group, url=self.url)

    class Meta:
        table_name = 'notifications'



if __name__ == '__main__':
    database.connect()
    database.create_tables([Info, Assignments,Notifications])
    database.close()