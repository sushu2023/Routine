import uuid
from sqlalchemy import Column, String, Date, DECIMAL, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship
from models.database import Base, SessionLocal

class AccountBook(Base):
    __tablename__ = 'account_book'

    # 定义字段
    account_book_id = Column(CHAR(36), primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))  # UUID 主键
    date = Column(Date, nullable=False)  # 日期
    category_id = Column(CHAR(36), ForeignKey('category.category_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False)  # 外键关联到 category 表
    item_id = Column(CHAR(36), ForeignKey('item.item_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False)  # 外键关联到 item 表
    expense = Column(DECIMAL(10, 2), nullable=False)  # 支出金额
    refund = Column(DECIMAL(10, 2), nullable=True, default=0.00)  # 退款金额，默认为 0.00
    remarks = Column(VARCHAR(255), nullable=True, default='')  # 备注，默认为空字符串
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())  # 更新时间
    user_id = Column(CHAR(36), ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)  # 外键关联到 users 表

    # 定义关系映射
    category = relationship("Category", back_populates="account_books")
    item = relationship("Item", back_populates="account_books")
    user = relationship("User", back_populates="account_books")

# 在 Category、Item 和 User 模型中添加反向关系（如果尚未定义）
from models.category_model import Category
from models.item_model import Item
from models.user_model import User

Category.account_books = relationship("AccountBook", order_by=AccountBook.date, back_populates="category")
Item.account_books = relationship("AccountBook", order_by=AccountBook.date, back_populates="item")
User.account_books = relationship("AccountBook", order_by=AccountBook.date, back_populates="user")

# CRUD 操作
def add_account_book(date, category_id, item_id, expense, refund=None, remarks=None, user_id=None):
    """
    添加账单记录
    :param date: 日期 (datetime.date)
    :param category_id: 分类 ID (str)
    :param item_id: 项目 ID (str)
    :param expense: 支出金额 (float)
    :param refund: 退款金额 (float, 可选)
    :param remarks: 备注 (str, 可选)
    :param user_id: 用户 ID (str, 可选)
    """
    session = SessionLocal()
    try:
        new_record = AccountBook(
            date=date,
            category_id=category_id,
            item_id=item_id,
            expense=expense,
            refund=refund,
            remarks=remarks,
            user_id=user_id
        )
        session.add(new_record)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_account_books():
    """
    获取所有账单记录
    """
    session = SessionLocal()
    try:
        records = session.query(AccountBook).all()
        return records
    finally:
        session.close()

def get_account_book_by_id(account_book_id):
    """
    根据账单 ID 获取账单记录
    :param account_book_id: 账单 ID (str)
    """
    session = SessionLocal()
    try:
        record = session.query(AccountBook).filter_by(account_book_id=account_book_id).first()
        if not record:
            raise ValueError("账单记录不存在")
        return record
    finally:
        session.close()

def update_account_book(account_book_id, date=None, category_id=None, item_id=None, expense=None, refund=None, remarks=None, user_id=None):
    """
    更新账单记录
    :param account_book_id: 账单 ID (str)
    :param date: 新的日期 (datetime.date, 可选)
    :param category_id: 新的分类 ID (str, 可选)
    :param item_id: 新的项目 ID (str, 可选)
    :param expense: 新的支出金额 (float, 可选)
    :param refund: 新的退款金额 (float, 可选)
    :param remarks: 新的备注 (str, 可选)
    :param user_id: 新的用户 ID (str, 可选)
    """
    session = SessionLocal()
    try:
        record = session.query(AccountBook).filter_by(account_book_id=account_book_id).first()
        if record:
            if date is not None:
                record.date = date
            if category_id is not None:
                record.category_id = category_id
            if item_id is not None:
                record.item_id = item_id
            if expense is not None:
                record.expense = expense
            if refund is not None:
                record.refund = refund
            if remarks is not None:
                record.remarks = remarks
            if user_id is not None:
                record.user_id = user_id
            session.commit()
        else:
            raise ValueError("账单记录不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_account_book(account_book_id):
    """
    删除账单记录
    :param account_book_id: 账单 ID (str)
    """
    session = SessionLocal()
    try:
        record = session.query(AccountBook).filter_by(account_book_id=account_book_id).first()
        if record:
            session.delete(record)
            session.commit()
        else:
            raise ValueError("账单记录不存在")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()