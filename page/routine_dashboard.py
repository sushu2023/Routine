import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

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


def calculate_training_frequency(filtered_records, time_unit, selected_year, selected_month=None):
    """
    计算训练频率，并返回分子（训练天数）、分母（总天数）和频率值
    """
    # 获取 status 为 1 的训练天数
    training_days = len({record.activity_date for record in filtered_records if record.status == 1})

    # 根据时间单位和选择的时间范围计算总天数
    today = date.today()
    if time_unit == "按年查看":
        if selected_year == today.year:  # 当前年份
            start_of_year = date(selected_year, 1, 1)
            total_days = (today - start_of_year).days + 1
        else:  # 往年
            start_of_year = date(selected_year, 1, 1)
            end_of_year = date(selected_year, 12, 31)
            total_days = (end_of_year - start_of_year).days + 1
    else:  # 按月查看
        if selected_year == today.year and selected_month == today.month:  # 当前月份
            start_of_month = date(selected_year, selected_month, 1)
            total_days = (today - start_of_month).days + 1
        else:  # 往月
            if selected_month == 12:
                next_month = date(selected_year + 1, 1, 1)
            else:
                next_month = date(selected_year, selected_month + 1, 1)
            start_of_month = date(selected_year, selected_month, 1)
            total_days = (next_month - start_of_month).days

    # 计算训练频率
    if total_days > 0:
        training_frequency = training_days / total_days
    else:
        training_frequency = 0

    return training_days, total_days, training_frequency


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
        if record.status == 1:  # 只统计 status 为 1 的活动
            for activity in record.activities:
                activity_counts[activity] = activity_counts.get(activity, 0) + 1

    total_activities = sum(activity_counts.values())

    # 计算训练频率
    training_days, total_days, training_frequency = calculate_training_frequency(
        filtered_records, time_unit, selected_year, selected_month if time_unit == "按月查看" else None
    )

    # 在同一行显示总训练次数、总训练天数和训练频率
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总训练次数", total_activities)
    with col2:
        st.metric("总训练天数", training_days)
    with col3:
        # 显示训练频率（大指标）和分子/分母（小指标）
        st.metric(
            label="训练频率",
            value=f"{training_frequency:.2%}",
            delta=f"{training_days} / {total_days}",  # 小指标：分子 / 分母
            delta_color="off"  # 禁用颜色变化
        )

    # 图表布局：活动分布图和月度趋势统计图并排显示
    st.subheader("图表展示")
    col_chart1, col_chart2 = st.columns(2)

    # 活动分布图（横向条形图）
    with col_chart1:
        st.caption("健身活动分布图")
        df_activity_counts = pd.DataFrame(list(activity_counts.items()), columns=["活动", "次数"])
        df_activity_counts = df_activity_counts.sort_values(by="次数", ascending=False)

        # Altair 横向条形图
        bar_chart = alt.Chart(df_activity_counts).mark_bar(
            color="#4C78A8",  # 条形颜色
            cornerRadiusTopLeft=5,  # 圆角
            cornerRadiusTopRight=5
        ).encode(
            x=alt.X("次数:Q", title="训练次数", axis=alt.Axis(grid=False)),  # X 轴为次数
            y=alt.Y("活动:N", sort="-x", title="健身活动"),  # Y 轴为活动，按次数降序排列
            tooltip=["活动:N", "次数:Q"]
        ).properties(
            width=400,
            height=300,
            title="健身活动分布"
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            labelColor="#666666",  # 标签颜色
            titleColor="#333333"   # 标题颜色
        ).configure_title(
            fontSize=16,
            anchor="start",
            color="#333333"  # 标题颜色
        )

        st.altair_chart(bar_chart, use_container_width=True)

    # 月度趋势统计图（组合图：柱状图+折线图）
    with col_chart2:
        st.caption("月度趋势统计图")
        # 统计最近几个月的健身次数
        monthly_data = {}
        for record in fitness_records:
            if record.user_id == user_id and record.status == 1:  # 只统计 status 为 1 的记录
                month_key = record.activity_date.strftime("%Y-%m")
                monthly_data[month_key] = monthly_data.get(month_key, 0) + len(record.activities)

        df_monthly = pd.DataFrame(list(monthly_data.items()), columns=["月份", "次数"])
        df_monthly["月份"] = pd.to_datetime(df_monthly["月份"])
        df_monthly = df_monthly.sort_values(by="月份", ascending=True)

        # 计算环比增长率
        df_monthly["环比增长"] = df_monthly["次数"].pct_change() * 100
        df_monthly["环比增长"] = df_monthly["环比增长"].fillna(0).round(2)

        # Altair 基础配置
        base = alt.Chart(df_monthly).encode(
            x=alt.X("月份:T", title="月份", axis=alt.Axis(format="%Y-%m", grid=False)),
        )

        # 柱状图：每月健身次数
        bar = base.mark_bar(color="#4C78A8").encode(
            y=alt.Y("次数:Q", title="健身次数", axis=alt.Axis(grid=False)),
            tooltip=["月份:T", "次数:Q"]
        )

        # 折线图：环比增长率
        line = base.mark_line(color="red", point=True).encode(
            y=alt.Y("环比增长:Q", title="环比增长 (%)", axis=alt.Axis(grid=False)),
            tooltip=["月份:T", "环比增长:Q"]
        )

        # 合并图表
        combined_chart = alt.layer(bar, line).resolve_scale(
            y="independent"  # 独立的 Y 轴
        ).properties(
            width=600,
            height=300,
            title="月度趋势统计"
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            labelColor="#666666",  # 标签颜色
            titleColor="#333333"   # 标题颜色
        ).configure_title(
            fontSize=16,
            anchor="start",
            color="#333333"  # 标题颜色
        )

        st.altair_chart(combined_chart, use_container_width=True)