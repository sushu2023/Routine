# 导入数据库连接和初始化逻辑
from .database import engine, SessionLocal, Base, init_db

# 导入用户模型和相关操作
from .user_model import User, add_user, get_all_users, update_user, delete_user

# 导入健身记录模型和相关操作
from .fitness_model import Fitness, add_fitness, get_all_fitness, update_fitness, delete_fitness

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
    "initialize_database"
]