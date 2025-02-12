import streamlit as st
from models.user_model import add_user, get_all_users, update_user, delete_user

# 初始化数据库
from models.database import init_db
init_db()

# 获取所有用户数据
users = get_all_users()

st.header("用户管理")

# 显示用户列表
if users:
    user_data = [{"用户名": user.username, "邮箱": user.email} for user in users]
    st.dataframe(user_data, use_container_width=True, hide_index=True)
else:
    st.info("暂无用户数据。")

# 添加用户
with st.expander("添加用户"):
    with st.form("add_user_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        email = st.text_input("邮箱（可选）")
        submitted = st.form_submit_button("提交")
        if submitted:
            try:
                add_user(username=username, password=password, email=email)
                st.toast("用户添加成功！", icon="✅")
                st.rerun()
            except Exception as e:
                st.toast(f"添加失败: {str(e)}", icon="❌")

# 更新用户
if users:
    with st.expander("更新用户"):
        user_to_update = st.selectbox("选择要更新的用户", [user.username for user in users])
        new_username = st.text_input("新用户名")
        new_password = st.text_input("新密码", type="password")
        new_email = st.text_input("新邮箱")
        if st.button("更新用户"):
            try:
                user_id = next(user.user_id for user in users if user.username == user_to_update)
                update_user(user_id=user_id, username=new_username, password=new_password, email=new_email)
                st.toast("用户更新成功！", icon="✅")
                st.rerun()
            except Exception as e:
                st.toast(f"更新失败: {str(e)}", icon="❌")

# 删除用户
if users:
    with st.expander("删除用户"):
        user_to_delete = st.selectbox("选择要删除的用户", [user.username for user in users])
        if st.button("删除用户"):
            try:
                user_id = next(user.user_id for user in users if user.username == user_to_delete)
                delete_user(user_id=user_id)
                st.toast("用户删除成功！", icon="✅")
                st.rerun()
            except Exception as e:
                st.toast(f"删除失败: {str(e)}", icon="❌")