from pydantic import BaseModel, Field
from typing import Optional

class Notification(BaseModel):
    title: str = Field(title='标题')
    content: Optional[str] = Field(title='内容')
    level: int = Field(1, title='等级', description='0: 静音, 1: 默认, 2: 普通, 3: 重要', ge=0, le=3)
    group: Optional[str] = Field(None, title='分组')
    url: Optional[str] = Field(None, title='链接', description='点击通知后跳转的链接')
    banned_clients: Optional[list] = Field([], title='禁用客户端', description='禁用的客户端')