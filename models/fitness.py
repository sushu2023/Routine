import uuid
from sqlalchemy import Column, CHAR, Date, JSON, TINYINT, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base, SessionLocal

class Fitness(Base):
    __tablename__ = 'fitness'

    # 定义字段
    fitness_id = Column(CHAR(36), primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    activity_date = Column(Date, nullable=False, unique=True)  # 健身日期，唯一性约束
    activities = Column(JSON, nullable=False)  # JSON 字段存储健身活动列表
    status = Column(TINYINT(1), nullable=False, default=0)  # 健身状态：0-未健身，1-已健身
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())  # 更新时间
    user_id = Column(CHAR(36), ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)  # 外键关联 users 表

    # 关系映射
    user = relationship("User", back_populates="fitness_records")

# 在 User 模型中添加反向关系（如果尚未定义）
from models.user_model import User
User.fitness_records = relationship("Fitness", order_by=Fitness.activity_date, back_populates="user")

# CRUD 操作

def add_fitness(activity_date, activities, status=0, user_id=None):
    """
    添加健身记录
    :param activity_date: 健身日期 (datetime.date)
    :param activities: 健身活动列表 (list of str)
    :param status: 健身状态 (int, 默认 0)
    :param user_id: 用户 ID (str, 可选)
    """
    session = SessionLocal()
    try:
        new_fitness = Fitness(
            activity_date=activity_date,
            activities=activities,
            status=status,
            user_id=user_id
        )
        session.add(new_fitness)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_fitness():
    """获取所有健身记录"""
    session = SessionLocal()
    try:
        fitness_records = session.query(Fitness).all()
        return fitness_records
    finally:
        session.close()

def get_fitness_by_user(user_id):
    """根据用户 ID 获取健身记录"""
    session = SessionLocal()
    try:
        fitness_records = session.query(Fitness).filter_by(user_id=user_id).all()
        return fitness_records
    finally:
        session.close()

def update_fitness(fitness_id, activities=None, status=None):
    """
    更新健身记录
    :param fitness_id: 健身记录 ID (str)
    :param activities: 新的健身活动列表 (list of str, 可选)
    :param status: 新的健身状态 (int, 可选)
    """
    session = SessionLocal()
    try:
        fitness_record = session.query(Fitness).filter_by(fitness_id=fitness_id).first()
        if fitness_record:
            if activities is not None:
                fitness_record.activities = activities
            if status is not None:
                fitness_record.status = status
            session.commit()
        else:
            raise ValueError("健身记录不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_fitness(fitness_id):
    """删除健身记录"""
    session = SessionLocal()
    try:
        fitness_record = session.query(Fitness).filter_by(fitness_id=fitness_id).first()
        if fitness_record:
            session.delete(fitness_record)
            session.commit()
        else:
            raise ValueError("健身记录不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()