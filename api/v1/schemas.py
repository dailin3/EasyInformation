from flask import url_for, abort
import config

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

