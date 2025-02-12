import streamlit as st
import pandas as pd
from models.user_model import add_user, get_all_users, update_user, delete_user

# 初始化数据库
from models.database import init_db
init_db()

def user_management_page():
    # 获取所有用户数据
    users = get_all_users()
    user_options = {user.username: user.user_id for user in users} if users else {}

    # 页面标题
    st.header("用户管理")

    # 显示用户列表
    if users:
        user_data = [{"用户名": user.username, "密码": user.password, "邮箱": user.email} for user in users]
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无用户数据。")

    # 侧边栏：添加用户
    with st.sidebar.expander("添加用户"):
        with st.form("add_user_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            email = st.text_input("邮箱")  # 去掉“（可选）”
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    add_user(username=username, password=password, email=email)
                    st.toast("用户添加成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新用户
    if users:
        with st.sidebar.expander("更新用户"):
            user_to_update = st.selectbox("选择要更新的用户", list(user_options.keys()), key="update_user_select")
            new_username = st.text_input("新用户名")
            new_password = st.text_input("新密码", type="password")
            new_email = st.text_input("邮箱")
            if st.button("更新用户"):
                try:
                    user_id = user_options[user_to_update]
                    update_user(user_id=user_id, username=new_username, password=new_password, email=new_email)
                    st.toast("用户更新成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除用户
    if users:
        with st.sidebar.expander("删除用户"):
            user_to_delete = st.selectbox("选择要删除的用户", list(user_options.keys()), key="delete_user_select")
            if st.button("删除用户"):
                try:
                    user_id = user_options[user_to_delete]
                    delete_user(user_id=user_id)
                    st.toast("用户删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")