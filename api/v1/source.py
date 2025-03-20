from .schemas import infos_schema, args_schema
from api.v1 import api_bp
import click

from db.db_model import Assignments, Info, Notifications
from flask import request, jsonify
from math import ceil
from flask.views import MethodView
from flask import url_for
from flask import abort

api_bp.route('/')(lambda: 'Hello World!')

class InfosAPI(MethodView):
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

        # 获取总记录数
        total_records = peewee_query.count()

        # 分页
        page = query.page
        per_page = query.per_page
        peewee_query = peewee_query.paginate(page, per_page)

        # 如果没有记录，报错
        if total_records == 0 or page > ceil(total_records / per_page):
            abort(404)
            

        # 计算分页元信息
        pagination = {
            'total': total_records,
            'page': page,
            'per_page': per_page,
            'pages': ceil(total_records / per_page) if per_page > 0 else 0
        }

        # 获取当前页的记录
        items = list(peewee_query)

        # 构造分页链接
        current = url_for('.infos', batch=page, batch_size=per_page, _external=True)
        prev = url_for('.infos', batch=page - 1, batch_size=per_page, _external=True) if page > 1 else None
        next = url_for('.infos', batch=page + 1, batch_size=per_page, _external=True) if page < pagination['pages'] else None

        # 返回分页结果
        return jsonify(infos_schema(items, current, prev, next, pagination))
    
class Info(MethodView):
    def delete(self, id):
        info = Info.get_or_none(Info.id == id)
        if info is None:
            abort(404)
        info.is_deleted = True
        info.save()
        return '', 204
    

api_bp.add_url_rule('/infos', view_func=InfosAPI.as_view('infos'), methods=['GET'])
api_bp.add_url_rule('/info/<int:id>', view_func=Info.as_view('info'), methods=['DELETE'])