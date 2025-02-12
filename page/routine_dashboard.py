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
    st.header("图表分析")

    # 用户选择
    if users:
        selected_user = st.selectbox("选择用户", list(user_options.keys()))
        user_id = user_options[selected_user]
    else:
        st.warning("请先添加用户！")
        return

    # 年月切换器
    time_unit = st.radio("选择时间单位", ["按年查看", "按月查看"], horizontal=True)

    # 年月选择器
    if time_unit == "按年查看":
        selected_year = st.selectbox("选择年份", sorted({record.activity_date.year for record in fitness_records}, reverse=True))
        filtered_records = [record for record in fitness_records if record.activity_date.year == selected_year and record.user_id == user_id]
    else:
        # 提取所有年份和月份
        all_dates = sorted({(record.activity_date.year, record.activity_date.month) for record in fitness_records}, reverse=True)
        selected_date = st.selectbox("选择年月", [f"{year}-{month:02d}" for year, month in all_dates])
        selected_year, selected_month = map(int, selected_date.split("-"))
        filtered_records = [
            record for record in fitness_records
            if record.activity_date.year == selected_year
            and record.activity_date.month == selected_month
            and record.user_id == user_id
        ]

    # 如果没有筛选到数据
    if not filtered_records:
        st.info("当前时间范围内暂无健身记录数据。")
        return

    # 数据准备
    activity_counts = {}
    total_duration = 0
    for record in filtered_records:
        for activity in record.activities:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        total_duration += len(record.activities) * 30  # 假设每次活动30分钟

    df_activity_counts = pd.DataFrame(list(activity_counts.items()), columns=["活动", "次数"])

    # 活动分布图
    st.subheader("健身活动分布图")
    st.bar_chart(df_activity_counts.set_index("活动"))

    # 时间趋势图
    st.subheader("健身时长趋势")
    daily_data = {}
    for record in filtered_records:
        date_key = record.activity_date.strftime("%Y-%m-%d")
        daily_data[date_key] = daily_data.get(date_key, 0) + len(record.activities) * 30  # 假设每次活动30分钟
    df_daily_data = pd.DataFrame(list(daily_data.items()), columns=["日期", "健身时长（分钟）"])
    df_daily_data["日期"] = pd.to_datetime(df_daily_data["日期"])
    st.line_chart(df_daily_data.set_index("日期")[["健身时长（分钟）"]])

    # 总体统计
    st.subheader("总体统计")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总健身次数", sum(activity_counts.values()))
    with col2:
        st.metric("总健身时长（分钟）", total_duration)