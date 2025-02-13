import streamlit as st
import pandas as pd
from datetime import date, timedelta
from models.account_book_model import (
    add_account_book, get_all_account_books, update_account_book, delete_account_book, get_account_book_by_id
)
from models.category_model import get_all_categories
from models.item_model import get_all_items
from models.user_model import get_all_users

# 初始化数据库
from models.database import init_db
init_db()

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

def account_book_management_page():
    # 页面标题
    st.header("账单管理")

    # 获取所有分类数据（用于下拉列表）
    categories = get_all_categories()
    category_options = {category.name: category.category_id for category in categories} if categories else {}

    # 获取所有项目数据（用于下拉列表）
    items = get_all_items()
    item_options = {item.name: item.item_id for item in items} if items else {}

    # 获取所有用户数据（用于下拉列表）
    users = get_all_users()
    user_options = {user.username: user.user_id for user in users} if users else {}

    # 获取所有账单记录数据
    account_books = get_all_account_books()

    # 筛选器：选择用户、时间单位、选择年份/月份
    col1, col2, col3 = st.columns([2, 1, 2])  # 调整列宽比例
    with col1:
        selected_user = st.selectbox("选择用户", list(user_options.keys()))
        user_id = user_options[selected_user]
    with col2:
        # 时间单位筛选器，默认为“按月查看”，且顺序调整为“按月查看”在前
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
                sorted({record.date.year for record in account_books}, reverse=True),
                key="year_selector"
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
                key="month_selector"
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

    # 计算指标：总收入、总支出、支出率
    total_income = sum(
        (record.expense - record.refund) for record in final_records if record.category_id == '13'
    )  # 收入
    total_expense = sum(
        (record.expense - record.refund) for record in final_records if record.category_id != '13'
    )  # 支出
    expense_ratio = total_expense / total_income if total_income > 0 else 0  # 支出率

    # 显示指标
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric(label="总收入", value=f"¥{total_income:.2f}")
    with col_metric2:
        st.metric(label="总支出", value=f"¥{total_expense:.2f}")
    with col_metric3:
        st.metric(label="支出率", value=f"{expense_ratio:.2%}")

    # 构建账单数据（隐藏账单 ID）
    account_book_data = [
        {
            "日期": book.date,
            "分类": next((c.name for c in categories if c.category_id == book.category_id), "未知分类"),
            "项目": next((i.name for i in items if i.item_id == book.item_id), "未知项目"),
            "实际金额": f"{book.expense - book.refund:.2f}",  # 实际金额 = 支出金额 - 退款金额
            "备注": book.remarks,
            "用户": next((u.username for u in users if u.user_id == book.user_id), "未知用户"),
        }
        for book in final_records
    ]
    df_account_books = pd.DataFrame(account_book_data)
    st.dataframe(df_account_books, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引

    # 侧边栏：添加账单记录
    with st.sidebar.expander("添加账单记录"):
        with st.form("add_account_book_form"):
            record_date = st.date_input("账单日期", value=date.today())
            category_name = st.selectbox("分类", list(category_options.keys())) if categories else None
            item_name = st.selectbox("项目", list(item_options.keys())) if items else None
            expense = st.number_input("支出金额", min_value=0.0, step=0.01, format="%.2f")
            refund = st.number_input("退款金额（可选）", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            remarks = st.text_input("备注（可选）", "")
            user_name = st.selectbox("用户（可选）", list(user_options.keys())) if users else None
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    if not categories or not items:
                        st.toast("请先添加分类和项目！", icon="❌")
                    else:
                        category_id = category_options[category_name]
                        item_id = item_options[item_name]
                        user_id = user_options[user_name] if user_name else None

                        # 如果是工资记录，调整日期为上个月的最后一天
                        if item_id == '1301' and record_date.day <= 20:  # 判断是否为工资记录
                            record_date = adjust_salary_date(record_date)

                        add_account_book(
                            date=record_date,
                            category_id=category_id,
                            item_id=item_id,
                            expense=expense,
                            refund=refund,
                            remarks=remarks,
                            user_id=user_id
                        )
                        st.toast("账单记录添加成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新账单记录
    if account_books and categories and items:
        with st.sidebar.expander("更新账单记录"):
            account_book_to_update = st.selectbox(
                "选择要更新的账单记录",
                [f"{book.date} ({book.account_book_id})" for book in account_books],
                key="update_account_book_select"
            )
            account_book_id_to_update = account_books[
                [f"{b.date} ({b.account_book_id})" for b in account_books].index(account_book_to_update)
            ].account_book_id
            new_record_date = st.date_input("新账单日期", value=date.today())
            new_category_name = st.selectbox("新分类", list(category_options.keys()))
            new_item_name = st.selectbox("新项目", list(item_options.keys()))
            new_expense = st.number_input("新支出金额", min_value=0.0, step=0.01, format="%.2f")
            new_refund = st.number_input("新退款金额（可选）", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            new_remarks = st.text_input("新备注（可选）", "")
            new_user_name = st.selectbox("新用户（可选）", list(user_options.keys())) if users else None
            if st.button("更新账单记录"):
                try:
                    new_category_id = category_options[new_category_name]
                    new_item_id = item_options[new_item_name]
                    new_user_id = user_options[new_user_name] if new_user_name else None

                    # 如果是工资记录，调整日期为上个月的最后一天
                    if new_item_id == '1301' and new_record_date.day <= 20:  # 判断是否为工资记录
                        new_record_date = adjust_salary_date(new_record_date)

                    update_account_book(
                        account_book_id=account_book_id_to_update,
                        date=new_record_date,
                        category_id=new_category_id,
                        item_id=new_item_id,
                        expense=new_expense,
                        refund=new_refund,
                        remarks=new_remarks,
                        user_id=new_user_id
                    )
                    st.toast("账单记录更新成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除账单记录
    if account_books:
        with st.sidebar.expander("删除账单记录"):
            account_book_to_delete = st.selectbox(
                "选择要删除的账单记录",
                [f"{book.date} ({book.account_book_id})" for book in account_books],
                key="delete_account_book_select"
            )
            account_book_id_to_delete = account_books[
                [f"{b.date} ({b.account_book_id})" for b in account_books].index(account_book_to_delete)
            ].account_book_id
            if st.button("删除账单记录"):
                try:
                    delete_account_book(account_book_id=account_book_id_to_delete)
                    st.toast("账单记录删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")