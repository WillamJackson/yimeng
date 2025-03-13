from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from wxcloudrun import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    phone = Column(String(20))
    balance = Column(DECIMAL(10, 2), default=0.00)
    avatar_url = Column(String(255))
    is_vip = Column(Boolean, default=False)
    vip_expire_time = Column(DateTime)
    vip_level = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UserPhoto(db.Model):
    __tablename__ = 'user_photos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    photo_type = Column(Integer, nullable=False)  # 1-头像 2-全身照
    photo_url = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship('User', backref='photos')

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_no = Column(String(64), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    order_type = Column(Integer, nullable=False)  # 1-充值 2-消费
    drawing_id = Column(Integer)
    status = Column(Integer, default=0)  # 0-待支付 1-已支付 2-已取消
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship('User', backref='orders') 