# 导入数据库连接和初始化逻辑
from .database import engine, SessionLocal, Base, init_db

# 导入用户模型和相关操作
from .user_model import User, add_user, get_all_users, update_user, delete_user

# 导入健身记录模型和相关操作
from .fitness_model import Fitness, add_fitness, get_all_fitness, update_fitness, delete_fitness

# 导入账单模型和相关操作
from .account_model import Category, Item, AccountBook
from .account_crud import (
    create_category,
    get_all_categories,
    delete_category,
    create_item,
    get_items_by_category,
    delete_item,
    create_account_record,
    get_account_records_by_user,
    update_account_record,
    delete_account_record,
)

# 初始化数据库表结构
def initialize_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)

# 导出公共接口
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "init_db",
    "User",
    "add_user",
    "get_all_users",
    "update_user",
    "delete_user",
    "Fitness",
    "add_fitness",
    "get_all_fitness",
    "update_fitness",
    "delete_fitness",
    # 账单相关
    "Category",
    "Item",
    "AccountBook",
    "create_category",
    "get_all_categories",
    "delete_category",
    "create_item",
    "get_items_by_category",
    "delete_item",
    "create_account_record",
    "get_account_records_by_user",
    "update_account_record",
    "delete_account_record",
    "initialize_database",
]