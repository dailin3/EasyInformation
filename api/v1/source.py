from .schemas import info_schema, info_schemas, args_schema
from api.v1 import api_bp
import click

from db.db_model import Assignments, Info, Notifications
from flask import request, jsonify
from flask.views import MethodView

api_bp.route('/')(lambda: 'Hello World!')

class InfoAPI(MethodView):
    def get(self):
        query = args_schema(request.args)
        # 创建基础查询
        peewee_query = Info.select()

        # 添加过滤条件
        if query.group != 'all':
            peewee_query = peewee_query.where(Info.group == query.group)
        
        if query.type != 'all':
            peewee_query = peewee_query.where(Info.type == query.type)
        
        if query.crawler_name != 'all':
            peewee_query = peewee_query.where(Info.crawler_name == query.crawler_name)

        # 添加排序条件
        if query.order_by == 'crawler_time':
            peewee_query = peewee_query.order_by(Info.crawler_time.desc())
        elif query.order_by == 'importance':
            peewee_query = peewee_query.order_by(Info.importance.desc())
        else:
            peewee_query = peewee_query.order_by(Info.crawler_time.desc())

        # 添加分页条件
        peewee_query = peewee_query.paginate(query.batch, query.batch_size)

        for info in peewee_query:
            click.echo(info.title)

        return "",200
    

api_bp.add_url_rule('/infos', view_func=InfoAPI.as_view('infos'), methods=['GET'])