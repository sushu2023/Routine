from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from models.database import Base, SessionLocal

class Category(Base):
    __tablename__ = 'category'

    # 定义字段
    category_id = Column(CHAR(36), primary_key=True, nullable=False)  # 手动输入的主键
    name = Column(String(50), nullable=False)  # 分类名称
    remark = Column(String(255), nullable=True)  # 备注（可选）

    # 如果有外键关联，可以在这里定义关系映射
    items = relationship("Item", back_populates="category")

# CRUD 操作
def add_category(category_id, name, remark=None):
    """
    添加分类
    :param category_id: 分类 ID (str)，需要手动输入
    :param name: 分类名称 (str)
    :param remark: 备注 (str, 可选)
    """
    session = SessionLocal()
    try:
        new_category = Category(
            category_id=category_id,
            name=name,
            remark=remark
        )
        session.add(new_category)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_categories():
    """
    获取所有分类
    """
    session = SessionLocal()
    try:
        categories = session.query(Category).all()
        return categories
    finally:
        session.close()

def get_category_by_id(category_id):
    """
    根据 ID 获取分类
    :param category_id: 分类 ID (str)
    """
    session = SessionLocal()
    try:
        category = session.query(Category).filter_by(category_id=category_id).first()
        if not category:
            raise ValueError("分类不存在")
        return category
    finally:
        session.close()

def update_category(category_id, name=None, remark=None):
    """
    更新分类信息
    :param category_id: 分类 ID (str)
    :param name: 新的分类名称 (str, 可选)
    :param remark: 新的备注 (str, 可选)
    """
    session = SessionLocal()
    try:
        category = session.query(Category).filter_by(category_id=category_id).first()
        if category:
            if name is not None:
                category.name = name
            if remark is not None:
                category.remark = remark
            session.commit()
        else:
            raise ValueError("分类不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_category(category_id):
    """
    删除分类
    :param category_id: 分类 ID (str)
    """
    session = SessionLocal()
    try:
        category = session.query(Category).filter_by(category_id=category_id).first()
        if category:
            session.delete(category)
            session.commit()
        else:
            raise ValueError("分类不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()