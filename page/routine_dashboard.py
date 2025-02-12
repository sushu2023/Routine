import streamlit as st
import pandas as pd

# 初始化数据库
from models.database import init_db
init_db()

# 获取所有用户数据（用于下拉列表）
from models.user_model import get_all_users
users = get_all_users()
user_options = {user.username: user.user_id for user in users} if users else {}

# 获取所有健身记录数据
from models.fitness_model import get_all_fitness
fitness_records = get_all_fitness()

def routine_dashboard_page():
    st.header("日常仪表盘")

    # 用户选择
    if users:
        selected_user = st.selectbox("选择用户", list(user_options.keys()))
        user_id = user_options[selected_user]
    else:
        st.warning("请先添加用户！")
        return

    # 显示健身记录统计
    st.subheader("健身记录统计")
    user_fitness_records = [record for record in fitness_records if record.user_id == user_id]
    if user_fitness_records:
        fitness_data = [
            {
                "日期": record.activity_date,
                "活动": ", ".join(record.activities),
                "状态": "已健身" if record.status else "未健身",
            }
            for record in user_fitness_records
        ]
        df_fitness = pd.DataFrame(fitness_data)
        st.dataframe(df_fitness, use_container_width=True, hide_index=True)
    else:
        st.info("暂无健身记录数据。")

    # 消费记录统计（占位）
    st.subheader("消费记录统计")
    st.info("消费记录功能尚未开发。")

    # 日常总结（占位）
    st.subheader("日常总结")
    st.write("这里是用户的日常总结内容。")