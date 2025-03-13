from flask import request, jsonify
from run import app
from .service import UserService
from wxcloudrun.response import make_succ_response, make_err_response
from decimal import Decimal
from datetime import datetime

# 用户注册
@app.route('/api/user/register', methods=['POST'])
def register_user():
    try:
        params = request.get_json()
        if not params.get('openid'):
            return make_err_response('缺少openid参数')
            
        user = UserService.create_user(
            openid=params['openid'],
            nickname=params.get('nickname'),
            phone=params.get('phone'),
            avatar_url=params.get('avatar_url')
        )
        return make_succ_response({
            'user_id': user.id,
            'openid': user.openid,
            'nickname': user.nickname,
            'balance': float(user.balance),
            'is_vip': user.is_vip,
            'vip_level': user.vip_level
        })
    except Exception as e:
        return make_err_response(str(e))

# 上传用户照片
@app.route('/api/user/photo', methods=['POST'])
def add_user_photo():
    try:
        params = request.get_json()
        if not all(k in params for k in ['user_id', 'photo_type', 'photo_url']):
            return make_err_response('缺少必要参数')
            
        photo = UserService.add_user_photo(
            user_id=params['user_id'],
            photo_type=params['photo_type'],
            photo_url=params['photo_url']
        )
        return make_succ_response({
            'photo_id': photo.id,
            'photo_url': photo.photo_url
        })
    except Exception as e:
        return make_err_response(str(e))

# 更新用户照片
@app.route('/api/user/photo/<int:photo_id>', methods=['PUT'])
def update_user_photo(photo_id):
    try:
        params = request.get_json()
        if 'photo_url' not in params:
            return make_err_response('缺少photo_url参数')
            
        photo = UserService.update_user_photo(
            photo_id=photo_id,
            photo_url=params['photo_url']
        )
        return make_succ_response({
            'photo_id': photo.id,
            'photo_url': photo.photo_url
        })
    except Exception as e:
        return make_err_response(str(e))

# 删除用户照片
@app.route('/api/user/photo/<int:photo_id>', methods=['DELETE'])
def delete_user_photo(photo_id):
    try:
        UserService.delete_user_photo(photo_id)
        return make_succ_response({'message': '删除成功'})
    except Exception as e:
        return make_err_response(str(e))

# 更新用户余额
@app.route('/api/user/balance', methods=['POST'])
def update_balance():
    try:
        params = request.get_json()
        if not all(k in params for k in ['user_id', 'amount', 'is_increase']):
            return make_err_response('缺少必要参数')
            
        user = UserService.update_user_balance(
            user_id=params['user_id'],
            amount=Decimal(str(params['amount'])),
            is_increase=params['is_increase']
        )
        return make_succ_response({
            'user_id': user.id,
            'balance': float(user.balance)
        })
    except Exception as e:
        return make_err_response(str(e))

# 更新会员状态
@app.route('/api/user/vip', methods=['POST'])
def update_vip():
    try:
        params = request.get_json()
        if not all(k in params for k in ['user_id', 'vip_level', 'expire_time']):
            return make_err_response('缺少必要参数')
            
        user = UserService.update_user_vip(
            user_id=params['user_id'],
            vip_level=params['vip_level'],
            expire_time=datetime.fromisoformat(params['expire_time'])
        )
        return make_succ_response({
            'user_id': user.id,
            'is_vip': user.is_vip,
            'vip_level': user.vip_level,
            'vip_expire_time': user.vip_expire_time.isoformat() if user.vip_expire_time else None
        })
    except Exception as e:
        return make_err_response(str(e))

# 创建订单
@app.route('/api/order', methods=['POST'])
def create_order():
    try:
        params = request.get_json()
        if not all(k in params for k in ['user_id', 'amount', 'order_type']):
            return make_err_response('缺少必要参数')
            
        order = UserService.create_order(
            user_id=params['user_id'],
            amount=Decimal(str(params['amount'])),
            order_type=params['order_type'],
            drawing_id=params.get('drawing_id')
        )
        return make_succ_response({
            'order_id': order.id,
            'order_no': order.order_no,
            'amount': float(order.amount),
            'status': order.status
        })
    except Exception as e:
        return make_err_response(str(e))

# 更新订单状态
@app.route('/api/order/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        params = request.get_json()
        if 'status' not in params:
            return make_err_response('缺少status参数')
            
        order = UserService.update_order_status(
            order_id=order_id,
            status=params['status']
        )
        return make_succ_response({
            'order_id': order.id,
            'status': order.status
        })
    except Exception as e:
        return make_err_response(str(e))

# 获取用户订单列表
@app.route('/api/user/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = UserService.get_user_orders(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        orders = [{
            'order_id': order.id,
            'order_no': order.order_no,
            'amount': float(order.amount),
            'order_type': order.order_type,
            'status': order.status,
            'created_at': order.created_at.isoformat()
        } for order in pagination.items]
        
        return make_succ_response({
            'orders': orders,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        return make_err_response(str(e))