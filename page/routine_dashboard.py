import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta
# 初始化数据库
from models.database import init_db
init_db()
# 获取所有用户数据（用于下拉列表）
from models.user_model import get_all_users
users = get_all_users()
user_options = {user.username: user.user_id for user in users} if users else {}
# 获取所有分类数据（用于账单记录）
from models.category_model import get_all_categories
categories = get_all_categories()
category_options = {category.name: category.category_id for category in categories} if categories else {}
# 获取所有项目数据（用于账单记录）
from models.item_model import get_all_items
items = get_all_items()
item_options = {item.name: item.item_id for item in items} if items else {}
# 获取所有账单记录数据
from models.account_book_model import get_all_account_books
account_books = get_all_account_books()
# 获取所有健身记录数据
from models.fitness_model import get_all_fitness
fitness_records = get_all_fitness()

def adjust_salary_date(record_date):
    """
    调整工资日期为发放月份的前一个月的最后一天。
    :param record_date: 工资发放的实际日期
    :return: 调整后的日期
    """
    # 获取发放月份的第一天
    first_day_of_month = record_date.replace(day=1)
    # 前一个月的最后一天 = 当前月份第一天 - 1天
    last_day_of_previous_month = first_day_of_month - timedelta(days=1)
    return last_day_of_previous_month

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
    
    # 创建 Tab 页面
    tab1, tab2 = st.tabs(["健身记录", "账单记录"])
    
    with tab1:  # 健身记录页面
        # 用户选择、时间单位选择、年月选择器放在同一行
        col1, col2, col3 = st.columns([2, 1, 2])  # 调整列宽比例
        with col1:
            fitness_selected_user = st.selectbox(
                "选择用户", 
                list(user_options.keys()),
                key="fitness_user_selector"
            )
            user_id = user_options[fitness_selected_user]
        with col2:
            time_unit = st.radio(
                "时间单位", 
                ["按月查看", "按年查看"], 
                index=0,  # 默认选择“按月查看”
                horizontal=True
                )
        with col3:
            if time_unit == "按年查看":
                selected_year = st.selectbox(
                    "选择年份",
                    sorted({record.activity_date.year for record in fitness_records}, reverse=True),
                    key="fitness_year_selector"
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
                    key="fitness_month_selector"
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

    with tab2:  # 账单记录页面
        st.header("账单记录分析")
        
        # 用户选择、时间单位选择、年月选择器放在同一行
        col1, col2, col3 = st.columns([2, 1, 2])  # 调整列宽比例
        with col1:
            account_book_selected_user = st.selectbox(
                "选择用户", 
                list(user_options.keys()), 
                key="account_book_user_select")
            user_id = user_options[account_book_selected_user]
        with col2:
            time_unit = st.radio("时间单位", ["按年查看", "按月查看"], horizontal=True, key="bill_time_unit")
        with col3:
            if time_unit == "按年查看":
                selected_year = st.selectbox(
                    "选择年份",
                    sorted({record.date.year for record in account_books}, reverse=True),
                    key="account_book_year_selector"
                )
                filtered_records = [
                    record for record in account_books
                    if (record.date.year == selected_year or 
                        (record.date.day <= 20 and record.item_id == '1301' and adjust_salary_date(record.date).year == selected_year))
                    and record.user_id == user_id
                ]
            else:
                # 提取所有年份和月份
                all_dates = sorted({(record.date.year, record.date.month) for record in account_books}, reverse=True)
                selected_date = st.selectbox(
                    "选择年月",
                    [f"{year}-{month:02d}" for year, month in all_dates],
                    key="account_book_month_selector"
                )
                selected_year, selected_month = map(int, selected_date.split("-"))
                filtered_records = [
                    record for record in account_books
                    if ((record.date.year == selected_year and record.date.month == selected_month) or
                        (record.date.day <= 20 and record.item_id == '1301' and 
                         adjust_salary_date(record.date).year == selected_year and 
                         adjust_salary_date(record.date).month == selected_month))
                    and record.user_id == user_id
                ]
        
        # 如果没有筛选到数据
        if not filtered_records:
            st.info("当前时间范围内暂无账单记录数据。")
            return
        
        # 区分工资记录和其他记录
        final_records = []
        for record in filtered_records:
            if record.item_id == '1301' and record.date.day <= 20:  # 判断是否为工资记录
                adjusted_date = adjust_salary_date(record.date)  # 调整日期为上个月的最后一天
                # 判断调整后的日期是否属于当前筛选范围
                if time_unit == "按年查看":
                    if adjusted_date.year == selected_year:
                        record.date = adjusted_date  # 动态调整日期
                        final_records.append(record)
                else:  # 按月查看
                    if adjusted_date.year == selected_year and adjusted_date.month == selected_month:
                        record.date = adjusted_date  # 动态调整日期
                        final_records.append(record)
            else:
                # 非工资记录直接保留
                final_records.append(record)
        
        # 按日期从大到小排序
        final_records.sort(key=lambda x: x.date, reverse=True)
        
        # 计算指标：总收入、总支出、结余、支出率
        total_income = sum(record.expense - record.refund for record in final_records if record.category_id == '13')  # 收入
        total_expense = sum(record.expense - record.refund for record in final_records if record.category_id != '13')  # 支出
        balance = total_income - total_expense  # 结余
        expense_ratio = total_expense / total_income if total_income > 0 else 0  # 支出率
        
        # 在一行显示指标
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        with col_metric1:
            st.metric("总收入", f"¥{total_income:.2f}")
        with col_metric2:
            st.metric("总支出", f"¥{total_expense:.2f}")
        with col_metric3:
            st.metric("结余", f"¥{balance:.2f}")
        with col_metric4:
            st.metric("支出率", f"{expense_ratio:.2%}")
        
        # 图表布局：收入支出柱形图和分类支出柱形图并排显示
        st.subheader("图表展示")
        col_chart1, col_chart2 = st.columns(2)
        
        # 收入与支出对比柱形图
        with col_chart1:
            st.caption("收入与支出对比")
            income_data = [{"类型": "收入", "金额": total_income}]
            expense_data = [{"类型": "支出", "金额": total_expense}]
            df_income_expense = pd.DataFrame(income_data + expense_data)
            bar_chart = alt.Chart(df_income_expense).mark_bar().encode(
                x=alt.X("类型:N", title=None),
                y=alt.Y("金额:Q", title="金额"),
                color=alt.Color("类型:N", scale=alt.Scale(range=["#4C78A8", "#F8766D"]))
            ).properties(
                width=400,
                height=300,
                title="收入与支出对比"
            )
            st.altair_chart(bar_chart, use_container_width=True)
        
        # 分类支出分布柱形图
        with col_chart2:
            st.caption("分类支出分布")
            category_expenses = {}
            for record in final_records:
                if record.category_id != '13':  # 排除收入
                    category_name = next((c.name for c in categories if c.category_id == record.category_id), "未知分类")
                    category_expenses[category_name] = category_expenses.get(category_name, 0) + (record.expense - record.refund)
            df_category_expenses = pd.DataFrame(list(category_expenses.items()), columns=["分类", "金额"])
            df_category_expenses = df_category_expenses.sort_values(by="金额", ascending=False)
            bar_chart = alt.Chart(df_category_expenses).mark_bar(color="#F8766D").encode(
                x=alt.X("金额:Q", title="金额"),
                y=alt.Y("分类:N", sort="-x", title="分类"),
                tooltip=["分类:N", "金额:Q"]
            ).properties(
                width=400,
                height=300,
                title="分类支出分布"
            )
            st.altair_chart(bar_chart, use_container_width=True)
