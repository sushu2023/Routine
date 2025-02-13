from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError  # 导入 SQLAlchemy 的异常类
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接 URL
DATABASE_URL = "mysql+pymysql://root:123456@localhost/routine"

# 创建引擎
try:
    engine = create_engine(DATABASE_URL)
    print("数据库引擎创建成功！")
except SQLAlchemyError as e:
    print(f"数据库引擎创建失败: {e}")
    raise  # 可选择抛出异常以终止程序

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()
metadata = MetaData()

def init_db():
    """初始化数据库"""
    try:
        # 尝试创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库初始化成功！")
    except SQLAlchemyError as e:
        print(f"数据库初始化失败: {e}")
        raise  # 可选择抛出异常以终止程序