from flask import url_for, current_app
import config

class Query:
    pass

def info_schemas():
    return

def info_schema():
    return

def args_schema(args):
    query = Query()
    query.batch = args.get('batch', 1, type=int)
    query.batch_size = args.get('batch_size', config.DEFAULT_BATCH_SIZE, type=int)

    query.group = args.get('group', 'all', type=str)
    query.type = args.get('type', "text/json", type=str)
    query.crawler_name = args.get('crawler_name', 'all', type=str)
    
    query.order_by = args.get('order_by', 'time', type=str) if (args.get('order_by', None, type=str) in ['crawler_time', 'time', 'importance']) else 'time'

    return query

