import streamlit as st
import pandas as pd
from datetime import date
from models.account_book_model import (
    add_account_book, get_all_account_books, update_account_book, delete_account_book, get_account_book_by_id
)
from models.category_model import get_all_categories
from models.item_model import get_all_items
from models.user_model import get_all_users

# 初始化数据库
from models.database import init_db
init_db()

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

    # 获取所有账单记录数据，并按日期从大到小排序
    account_books = get_all_account_books()
    if account_books:
        # 按日期降序排序
        account_books.sort(key=lambda x: x.date, reverse=True)

        # 构建账单数据（隐藏账单 ID）
        account_book_data = [
            {
                "日期": book.date,
                "分类": next((c.name for c in categories if c.category_id == book.category_id), "未知分类"),
                "项目": next((i.name for i in items if i.item_id == book.item_id), "未知项目"),
                "支出金额": f"{book.expense:.2f}",
                "退款金额": f"{book.refund:.2f}" if book.refund else "0.00",
                "备注": book.remarks,
                "用户": next((u.username for u in users if u.user_id == book.user_id), "未知用户"),
            }
            for book in account_books
        ]
        df_account_books = pd.DataFrame(account_book_data)
        st.dataframe(df_account_books, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无账单记录数据。")

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