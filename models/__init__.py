# 导入数据库连接和初始化逻辑
from .database import engine, SessionLocal, Base, init_db

# 导入用户模型和相关操作
from .user_model import User, add_user, get_all_users, update_user, delete_user

# 导入健身记录模型和相关操作
from .fitness_model import Fitness, add_fitness, get_all_fitness, update_fitness, delete_fitness

# 导入分类模型和相关操作
from .category_model import Category, add_category, get_all_categories, get_category_by_id, update_category, delete_category

# 导入项目模型和相关操作
from .item_model import Item, add_item, get_all_items, get_item_by_id, update_item, delete_item

# 导入账单模型和相关操作
from .account_book_model import AccountBook, add_account_book, get_all_account_books, get_account_book_by_id, update_account_book, delete_account_book

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
    "Category",
    "add_category",
    "get_all_categories",
    "get_category_by_id",
    "update_category",
    "delete_category",
    "Item",
    "add_item",
    "get_all_items",
    "get_item_by_id",
    "update_item",
    "delete_item",
    "AccountBook",
    "add_account_book",
    "get_all_account_books",
    "get_account_book_by_id",
    "update_account_book",
    "delete_account_book",
    "initialize_database"
]