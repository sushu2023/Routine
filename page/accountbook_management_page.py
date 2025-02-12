import streamlit as st
import pandas as pd
from datetime import date
from models.account_model import AccountBook, create_account_record, get_account_records_by_user, delete_account_record
from models.user_model import get_all_users
from models.account_crud import get_all_categories, get_items_by_category
from models.database import init_db

# 初始化数据库
init_db()

def accountbook_management_page():
    # 获取所有用户、分类和项目数据
    users = get_all_users()
    user_options = {user.username: user.user_id for user in users} if users else {}
    categories = get_all_categories()
    category_options = {category.name: category.category_id for category in categories} if categories else {}

    # 页面标题
    st.header("账单管理")

    # 显示账单记录
    if users:
        selected_user = st.selectbox("选择用户", list(user_options.keys()))
        records = get_account_records_by_user(user_id=user_options[selected_user])
        if records:
            record_data = [
                {
                    "账单ID": record.id,
                    "日期": record.date,
                    "分类": next((c.name for c in categories if c.category_id == record.category_id), "未知"),
                    "项目": next((i.name for i in get_items_by_category(record.category_id) if i.item_id == record.item_id), "未知"),
                    "支出": record.expense,
                    "退款": record.refund,
                    "备注": record.remarks
                }
                for record in records
            ]
            df_records = pd.DataFrame(record_data)
            st.dataframe(df_records, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
        else:
            st.info("该用户暂无账单记录。")
    else:
        st.info("暂无用户数据，请先添加用户。")

    # 侧边栏：添加账单记录
    with st.sidebar.expander("添加账单记录"):
        with st.form("add_account_form"):
            record_id = st.text_input("账单ID（唯一标识）")
            selected_user = st.selectbox("用户", list(user_options.keys()))
            selected_category = st.selectbox("分类", list(category_options.keys()))
            items = get_items_by_category(category_id=category_options[selected_category])
            item_options = {item.name: item.item_id for item in items} if items else {}
            selected_item = st.selectbox("项目", list(item_options.keys()))
            record_date = st.date_input("日期", value=date.today())
            expense = st.number_input("支出金额", min_value=0.0, step=0.01)
            refund = st.number_input("退款金额", min_value=0.0, step=0.01)
            remarks = st.text_input("备注（可选）")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    create_account_record(
                        record_id=record_id,
                        date=record_date,
                        category_id=category_options[selected_category],
                        item_id=item_options[selected_item],
                        expense=expense,
                        refund=refund,
                        remarks=remarks,
                        user_id=user_options[selected_user]
                    )
                    st.toast("账单记录添加成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：删除账单记录
    if users:
        with st.sidebar.expander("删除账单记录"):
            selected_user = st.selectbox("选择用户", list(user_options.keys()), key="delete_account_user_select")
            records = get_account_records_by_user(user_id=user_options[selected_user])
            if records:
                record_to_delete = st.selectbox("选择要删除的账单记录", [record.id for record in records], key="delete_account_select")
                if st.button("删除账单记录"):
                    try:
                        delete_account_record(record_id=record_to_delete)
                        st.toast("账单记录删除成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                    except Exception as e:
                        st.toast(f"删除失败: {str(e)}", icon="❌")