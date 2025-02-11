from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint

# 创建基础类
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    # 定义字段
    user_id = Column(CHAR(36), primary_key=True, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # 定义表的元信息
    __table_args__ = (
        UniqueConstraint('email', name='unique_email'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8', 'mysql_collate': 'utf8_general_ci'}
    )

# 示例：生成建表语句（仅用于调试）
if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine('mysql+pymysql://root:123456@localhost/routine')  # 替换为实际数据库连接信息
    Base.metadata.create_all(engine)