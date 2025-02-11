from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接 URL
DATABASE_URL = "mysql+pymysql://root:123456@localhost/routine"

# 创建引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()
metadata = MetaData()

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)