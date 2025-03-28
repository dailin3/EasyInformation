from flask import url_for, abort
import config
import xml.etree.ElementTree as ET
import json, click

class Query:
    pass

def info_schema(info):
    return {
        'id': info.id,
        'author': info.author,
        'content': info.content,
        'crawler_name': info.crawler_name,
        'crawler_time': info.crawler_time,
        'discription': info.discription,
        'href': info.href,
        'importance': info.importance,
        'is_deleted': info.is_deleted,
        'is_read': info.is_read,
        'group': info.group,
        'summary': info.summary,
        'time': info.time,
        'title': info.title,
        'type': info.type
    }


def infos_schema(items, current, prev, next, pagination):
    return {
        'self': current,
        'prev': prev,
        'next': next,
        'kind': 'infoCollection',
        'count': pagination["total"],
        'page': pagination["page"],
        'pages': pagination["pages"],
        'per_page': pagination["per_page"],
        'first': url_for('.infos', page=1, per_page=pagination["per_page"], _external=True),
        'last': url_for('.infos', page=pagination["pages"], per_page=pagination["per_page"], _external=True),
        'items': [info_schema(item) for item in items]
    }

def args_schema(args):
    allowed_args = {'page', 'per_page', 'group', 'type', 'crawler_name', 'order_by'}
    if not set(args.keys()).issubset(allowed_args):
        abort(400, description=f"Unexpected parameter")

    query = Query()
    query.page = args.get('page', 1, type=int)
    query.per_page = args.get('per_page', config.DEFAULT_BATCH_SIZE, type=int)

    query.group = args.get('group', 'all', type=str)
    query.type = args.get('type', "text/json", type=str)
    query.crawler_name = args.get('crawler_name', 'all', type=str)
    
    query.order_by = args.get('order_by', 'time', type=str) if (args.get('order_by', None, type=str) in ['crawler_time', 'time', 'importance']) else 'time'

    return query

def rss_schema(items):
    # 创建 RSS 根元素
    rss = ET.Element("rss", version="2.0", attrib={
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })
    channel = ET.SubElement(rss, "channel")

    # 添加频道信息
    ET.SubElement(channel, "title").text = "北邮消息列表"
    ET.SubElement(channel, "link").text = f"{config.HOST}:{config.PORT}/info/rss"
    ET.SubElement(channel, "description").text = "这里会展示爬虫爬取的消息"

    # 动态生成 <item>
    for article in items:
        content_html = content_render(article)
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = article.href
        ET.SubElement(item, "description").text = article.summary
        ET.SubElement(item, "pubDate").text = article.time
        ET.SubElement(item, "guid").text = article.href
        ET.SubElement(item, "content:encoded").text = content_html

    # 将 XML 转换为字符串
    rss_feed = ET.tostring(rss, encoding="utf-8", method="xml")
    return rss_feed

def content_render(item):
    item_html = ''
    for content in json.loads(item.content):
        click.echo(content)
        if content['type'] == 'p':
            item_html += f'<p>{content["content"]}</p>'
        elif content['type'] == 'img':
            item_html += f'<img src="{content["href"]}" />'
        elif content['type'] == 'a':
            item_html += f'<a href="{content["href"]}">{content["content"]}</a>'
        else:
            item_html += f'<p>render error!</p>'

    return item_html