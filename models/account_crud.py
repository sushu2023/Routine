from sqlalchemy.orm import Session
from models.account_model import Category, Item, AccountBook
from datetime import datetime


# Category 操作
def create_category(db: Session, name: str, remark: str = None):
    """创建分类"""
    category = Category(name=name, remark=remark)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_all_categories(db: Session):
    """获取所有分类"""
    return db.query(Category).all()


def delete_category(db: Session, category_id: int):
    """删除分类"""
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return category


# Item 操作
def create_item(db: Session, item_id: str, category_id: int, name: str, remark: str = ""):
    """创建项目"""
    item = Item(item_id=item_id, category_id=category_id, name=name, remark=remark)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_items_by_category(db: Session, category_id: int):
    """根据分类ID获取项目"""
    return db.query(Item).filter(Item.category_id == category_id).all()


def delete_item(db: Session, item_id: str):
    """删除项目"""
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item


# AccountBook 操作
def create_account_record(
    db: Session,
    record_id: str,
    date: datetime,
    category_id: int,
    item_id: str,
    expense: float,
    refund: float = 0.00,
    remarks: str = "",
    user_id: str = None
):
    """创建账单记录"""
    record = AccountBook(
        id=record_id,
        date=date,
        category_id=category_id,
        item_id=item_id,
        expense=expense,
        refund=refund,
        remarks=remarks,
        user_id=user_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_account_records_by_user(db: Session, user_id: str):
    """根据用户ID获取账单记录"""
    return db.query(AccountBook).filter(AccountBook.user_id == user_id).all()


def update_account_record(db: Session, record_id: str, updates: dict):
    """更新账单记录"""
    record = db.query(AccountBook).filter(AccountBook.id == record_id).first()
    if record:
        for key, value in updates.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
    return record


def delete_account_record(db: Session, record_id: str):
    """删除账单记录"""
    record = db.query(AccountBook).filter(AccountBook.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
    return record