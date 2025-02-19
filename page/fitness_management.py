import streamlit as st
import pandas as pd
from datetime import date, timedelta

# 初始化数据库
from models.database import init_db
init_db()

# 获取所有用户数据（用于下拉列表）
from models.user_model import get_all_users
users = get_all_users()
user_options = {user.username: user.user_id for user in users} if users else {}

# 获取所有健身管理函数
from models.fitness_model import get_all_fitness, add_fitness, update_fitness, delete_fitness

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

def fitness_management_page():
    st.header("健身管理")

    # 用户选择、时间单位选择、年月选择器放在同一行
    col1, col2, col3 = st.columns([2, 1, 2])  # 调整列宽比例
    with col1:
        selected_user = st.selectbox(
            "选择用户", 
            list(user_options.keys()),
            key="fitness_user_selector"
        )
        user_id = user_options[selected_user]
    
    with col2:
        time_unit = st.radio(
            "时间单位", 
            ["按月查看", "按年查看"], 
            index=0,  # 默认选择“按月查看”
            horizontal=True
        )
    
    with col3:
        # 获取最新数据并按日期降序排列
        fitness_records = get_all_fitness()
        fitness_records.sort(key=lambda x: x.activity_date, reverse=True)  # 按日期降序排列
        
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
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric("总训练次数", total_activities)
    with col_metric2:
        st.metric("总训练天数", training_days)
    with col_metric3:
        # 显示训练频率（大指标）和分子/分母（小指标）
        st.metric(
            label="训练频率",
            value=f"{training_frequency:.2%}",
            delta=f"{training_days} / {total_days}",  # 小指标：分子 / 分母
            delta_color="off"  # 禁用颜色变化
        )

    # 构建健身记录数据
    fitness_data = [
        {
            "日期": record.activity_date,
            "活动": ", ".join(record.activities),
            "状态": "已健身" if record.status else "未健身",
            "用户": next((u.username for u in users if u.user_id == record.user_id), "未知用户"),
        }
        for record in filtered_records
    ]
    df_fitness = pd.DataFrame(fitness_data)
    st.dataframe(df_fitness, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引

    # 侧边栏：添加健身记录
    with st.sidebar.expander("添加健身记录"):
        with st.form("add_fitness_form"):
            activity_date = st.date_input("健身日期", value=date.today())
            activities = st.multiselect("健身活动（多选）", ["胸部", "背部", "手臂", "肩部", "腹部", "腿部", "有氧", "未健身"])
            user_name = st.selectbox("用户（可选）", list(user_options.keys())) if users else None
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    if "未健身" in activities and len(activities) > 1:
                        st.toast("选择‘未健身’时不能同时选择其他活动！", icon="❌")
                    elif not activities:
                        st.toast("请至少选择一项健身活动！", icon="❌")
                    elif not users:
                        st.toast("无法添加健身记录，请先添加用户！", icon="❌")
                    else:
                        user_id = user_options[user_name]
                        status = 0 if "未健身" in activities else 1  # 设置状态
                        activities = [] if "未健身" in activities else activities  # 清空活动列表
                        add_fitness(activity_date=activity_date, activities=activities, status=status, user_id=user_id)
                        st.toast("健身记录添加成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新健身记录
    if fitness_records and users:
        with st.sidebar.expander("更新健身记录"):
            fitness_to_update = st.selectbox(
                "选择要更新的健身记录",
                [f"{record.activity_date} ({', '.join(record.activities)})" for record in fitness_records],
                key="update_fitness_select"
            )
            fitness_id_to_update = fitness_records[
                [f"{r.activity_date} ({', '.join(r.activities)})" for r in fitness_records].index(fitness_to_update)
            ].fitness_id
            new_activities = st.multiselect("新健身活动（多选）", ["胸部", "背部", "手臂", "肩部", "腹部", "腿部", "有氧", "未健身"])
            new_user_name = st.selectbox("新用户", list(user_options.keys()))
            if st.button("更新健身记录"):
                try:
                    if "未健身" in new_activities and len(new_activities) > 1:
                        st.toast("选择‘未健身’时不能同时选择其他活动！", icon="❌")
                    elif not new_activities:
                        st.toast("请至少选择一项健身活动！", icon="❌")
                    else:
                        new_user_id = user_options[new_user_name]
                        status = 0 if "未健身" in new_activities else 1  # 设置状态
                        new_activities = [] if "未健身" in new_activities else new_activities  # 清空活动列表
                        update_fitness(fitness_id=fitness_id_to_update, activities=new_activities, status=status)
                        st.toast("健身记录更新成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除健身记录
    if fitness_records:
        with st.sidebar.expander("删除健身记录"):
            fitness_to_delete = st.selectbox(
                "选择要删除的健身记录",
                [f"{record.activity_date} ({', '.join(record.activities)})" for record in fitness_records],
                key="delete_fitness_select"
            )
            fitness_id_to_delete = fitness_records[
                [f"{r.activity_date} ({', '.join(r.activities)})" for r in fitness_records].index(fitness_to_delete)
            ].fitness_id
            if st.button("删除健身记录"):
                try:
                    delete_fitness(fitness_id=fitness_id_to_delete)
                    st.toast("健身记录删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")