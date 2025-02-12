from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from models.database import Base, SessionLocal

class Item(Base):
    __tablename__ = 'item'

    # 定义字段
    item_id = Column(CHAR(36), primary_key=True, nullable=False)  # 手动输入的主键
    category_id = Column(CHAR(36), ForeignKey('category.category_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False)  # 外键关联到 category 表
    name = Column(String(255), nullable=False)  # 名称
    remark = Column(String(255), nullable=True, default='')  # 备注，默认为空字符串

    # 定义与 Category 模型的关系
    category = relationship("Category", back_populates="items")

# 在 Category 模型中添加反向关系（如果尚未定义）
from models.category_model import Category
Category.items = relationship("Item", order_by=Item.item_id, back_populates="category")

# CRUD 操作
def add_item(item_id, category_id, name, remark=None):
    """
    添加项目
    :param item_id: 项目 ID (str)，需要手动输入
    :param category_id: 分类 ID (str)
    :param name: 项目名称 (str)
    :param remark: 备注 (str, 可选)
    """
    session = SessionLocal()
    try:
        new_item = Item(
            item_id=item_id,
            category_id=category_id,
            name=name,
            remark=remark
        )
        session.add(new_item)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_items():
    """
    获取所有项目
    """
    session = SessionLocal()
    try:
        items = session.query(Item).all()
        return items
    finally:
        session.close()

def get_item_by_id(item_id):
    """
    根据项目 ID 获取项目
    :param item_id: 项目 ID (str)
    """
    session = SessionLocal()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if not item:
            raise ValueError("项目不存在")
        return item
    finally:
        session.close()

def update_item(item_id, name=None, remark=None):
    """
    更新项目信息
    :param item_id: 项目 ID (str)
    :param name: 新的项目名称 (str, 可选)
    :param remark: 新的备注 (str, 可选)
    """
    session = SessionLocal()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if item:
            if name is not None:
                item.name = name
            if remark is not None:
                item.remark = remark
            session.commit()
        else:
            raise ValueError("项目不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_item(item_id):
    """
    删除项目
    :param item_id: 项目 ID (str)
    """
    session = SessionLocal()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if item:
            session.delete(item)
            session.commit()
        else:
            raise ValueError("项目不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()