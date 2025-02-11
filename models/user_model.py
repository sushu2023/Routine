import uuid
from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.dialects.mysql import CHAR
from models.database import Base, SessionLocal

class User(Base):
    __tablename__ = 'users'

    # 定义字段
    user_id = Column(CHAR(36), primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)  # 不为空，移除 unique 约束
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

# CRUD 操作

def add_user(username, password, email):
    """添加用户"""
    session = SessionLocal()
    try:
        new_user = User(
            username=username,
            password=password,
            email=email
        )
        session.add(new_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_users():
    """获取所有用户"""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return users
    finally:
        session.close()

def delete_user(user_id):
    """删除用户"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
        else:
            raise ValueError("用户不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_user(user_id, username=None, password=None, email=None):
    """更新用户信息"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            if username:
                user.username = username
            if password:
                user.password = password
            if email:
                user.email = email
            session.commit()
        else:
            raise ValueError("用户不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()