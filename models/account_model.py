from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from models.database import Base

class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)  # 分类ID
    name = Column(String(50), nullable=False)                            # 分类名称
    remark = Column(String(255), nullable=True)                          # 备注

    # 关联关系：一个分类可以有多个项目
    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "item"

    item_id = Column(String(4), primary_key=True)                        # 项目ID
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)  # 分类ID
    name = Column(String(255), nullable=False)                           # 项目名称
    remark = Column(String(255), nullable=True, default="")              # 备注

    # 关联关系：一个项目属于一个分类
    category = relationship("Category", back_populates="items")


class AccountBook(Base):
    __tablename__ = "account_book"

    id = Column(String(12), primary_key=True)                            # 账单ID
    date = Column(Date, nullable=False)                                  # 日期
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)  # 分类ID
    item_id = Column(String(4), ForeignKey("item.item_id"), nullable=False)            # 项目ID
    expense = Column(DECIMAL(10, 2), nullable=False)                     # 支出金额
    refund = Column(DECIMAL(10, 2), nullable=True, default=0.00)         # 退款金额
    remarks = Column(String(255), nullable=True, default="")             # 备注
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")  # 创建时间
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP", 
                        server_onupdate="CURRENT_TIMESTAMP")             # 更新时间
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)           # 用户ID

    # 关联关系：账单属于某个分类和项目
    category = relationship("Category")
    item = relationship("Item")