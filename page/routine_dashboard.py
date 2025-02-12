import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # 用户选择、时间单位选择、年月选择器放在同一行
    col1, col2, col3 = st.columns([2, 1, 2])  # 调整列宽比例
    with col1:
        selected_user = st.selectbox("选择用户", list(user_options.keys()))
        user_id = user_options[selected_user]
    with col2:
        time_unit = st.radio("时间单位", ["按年查看", "按月查看"], horizontal=True)
    with col3:
        if time_unit == "按年查看":
            selected_year = st.selectbox(
                "选择年份",
                sorted({record.activity_date.year for record in fitness_records}, reverse=True),
                key="year_selector"
            )
            filtered_records = [
                record for record in fitness_records
                if record.activity_date.year == selected_year and record.user_id == user_id
            ]
        else:
            # 提取所有年份和月份
            all_dates = sorted({(record.activity_date.year, record.activity_date.month) for record in fitness_records}, reverse=True)
            selected_date = st.selectbox(
                "选择年月",
                [f"{year}-{month:02d}" for year, month in all_dates],
                key="month_selector"
            )
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

    # 分割线
    st.markdown("---")

    # 总体统计
    st.subheader("总体统计")
    activity_counts = {}
    for record in filtered_records:
        for activity in record.activities:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1

    total_activities = sum(activity_counts.values())

    col1, col2 = st.columns(2)
    with col1:
        st.metric("总训练次数", total_activities)

    # 图表布局：活动分布图和月度趋势统计图并排显示
    st.subheader("图表展示")
    col_chart1, col_chart2 = st.columns(2)

    # 活动分布图（条形图）
    with col_chart1:
        st.caption("健身活动分布图")
        df_activity_counts = pd.DataFrame(list(activity_counts.items()), columns=["活动", "次数"])
        df_activity_counts = df_activity_counts.sort_values(by="次数", ascending=False)
        st.bar_chart(df_activity_counts.set_index("活动"), use_container_width=True)

    # 月度趋势统计图（组合图：柱状图+折线图）
    with col_chart2:
        st.caption("月度趋势统计图")
        # 统计最近几个月的健身次数
        monthly_data = {}
        for record in fitness_records:
            if record.user_id == user_id:
                month_key = record.activity_date.strftime("%Y-%m")
                monthly_data[month_key] = monthly_data.get(month_key, 0) + len(record.activities)
        df_monthly = pd.DataFrame(list(monthly_data.items()), columns=["月份", "次数"])
        df_monthly["月份"] = pd.to_datetime(df_monthly["月份"])
        df_monthly = df_monthly.sort_values(by="月份", ascending=True)

        # 计算环比增长率
        df_monthly["环比增长"] = df_monthly["次数"].pct_change() * 100
        df_monthly["环比增长"] = df_monthly["环比增长"].fillna(0).round(2)

        # 绘制组合图
        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax2 = ax1.twinx()

        # 柱状图：每月健身次数
        ax1.bar(df_monthly["月份"].dt.strftime("%Y-%m"), df_monthly["次数"], color="skyblue", label="健身次数")
        ax1.set_xlabel("月份")
        ax1.set_ylabel("健身次数", color="skyblue")
        ax1.tick_params(axis='y', labelcolor="skyblue")

        # 折线图：环比增长率
        ax2.plot(df_monthly["月份"].dt.strftime("%Y-%m"), df_monthly["环比增长"], color="orange", marker="o", label="环比增长")
        ax2.set_ylabel("环比增长 (%)", color="orange")
        ax2.tick_params(axis='y', labelcolor="orange")

        # 添加图例
        fig.tight_layout()
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        # 显示图表
        st.pyplot(fig)