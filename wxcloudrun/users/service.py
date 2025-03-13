from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy.exc import SQLAlchemyError
from wxcloudrun import db
from .models import User, UserPhoto, Order

class UserService:
    @staticmethod
    def create_user(openid: str, nickname: str = None, phone: str = None, avatar_url: str = None) -> User:
        """创建新用户"""
        try:
            user = User(
                openid=openid,
                nickname=nickname,
                phone=phone,
                avatar_url=avatar_url
            )
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"创建用户失败: {str(e)}")

    @staticmethod
    def add_user_photo(user_id: int, photo_type: int, photo_url: str) -> UserPhoto:
        """添加用户照片"""
        try:
            photo = UserPhoto(
                user_id=user_id,
                photo_type=photo_type,
                photo_url=photo_url
            )
            db.session.add(photo)
            db.session.commit()
            return photo
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"添加用户照片失败: {str(e)}")

    @staticmethod
    def update_user_photo(photo_id: int, photo_url: str) -> UserPhoto:
        """更新用户照片"""
        try:
            photo = UserPhoto.query.get(photo_id)
            if not photo:
                raise Exception("照片不存在")
            photo.photo_url = photo_url
            db.session.commit()
            return photo
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"更新用户照片失败: {str(e)}")

    @staticmethod
    def delete_user_photo(photo_id: int) -> bool:
        """逻辑删除用户照片"""
        try:
            photo = UserPhoto.query.get(photo_id)
            if not photo:
                raise Exception("照片不存在")
            photo.is_deleted = True
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"删除用户照片失败: {str(e)}")

    @staticmethod
    def update_user_balance(user_id: int, amount: Decimal, is_increase: bool = True) -> User:
        """更新用户余额"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise Exception("用户不存在")
            if is_increase:
                user.balance += amount
            else:
                if user.balance < amount:
                    raise Exception("余额不足")
                user.balance -= amount
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"更新用户余额失败: {str(e)}")

    @staticmethod
    def update_user_vip(user_id: int, vip_level: int, expire_time: datetime) -> User:
        """更新用户会员状态"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise Exception("用户不存在")
            user.is_vip = True
            user.vip_level = vip_level
            user.vip_expire_time = expire_time
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"更新用户会员状态失败: {str(e)}")

    @staticmethod
    def update_user_avatar(user_id: int, avatar_url: str) -> User:
        """更新用户头像"""
        try:
            user = User.query.get(user_id)
            if not user:
                raise Exception("用户不存在")
            user.avatar_url = avatar_url
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"更新用户头像失败: {str(e)}")

    @staticmethod
    def create_order(user_id: int, amount: Decimal, order_type: int, drawing_id: int = None) -> Order:
        """创建订单"""
        try:
            order = Order(
                user_id=user_id,
                order_no=f"ORD{uuid.uuid4().hex[:16].upper()}",
                amount=amount,
                order_type=order_type,
                drawing_id=drawing_id
            )
            db.session.add(order)
            db.session.commit()
            return order
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"创建订单失败: {str(e)}")

    @staticmethod
    def update_order_status(order_id: int, status: int) -> Order:
        """更新订单状态"""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise Exception("订单不存在")
            order.status = status
            db.session.commit()
            return order
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"更新订单状态失败: {str(e)}")

    @staticmethod
    def delete_order(order_id: int) -> bool:
        """逻辑删除订单"""
        try:
            order = Order.query.get(order_id)
            if not order:
                raise Exception("订单不存在")
            order.is_deleted = True
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"删除订单失败: {str(e)}")

    @staticmethod
    def get_user_orders(user_id: int, page: int = 1, per_page: int = 20):
        """获取用户订单列表"""
        try:
            return Order.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).order_by(
                Order.created_at.desc()
            ).paginate(page=page, per_page=per_page)
        except SQLAlchemyError as e:
            raise Exception(f"获取用户订单列表失败: {str(e)}") 