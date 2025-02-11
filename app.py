import streamlit as st
from models.user_model import add_user, get_all_users, update_user, delete_user
from models.fitness_model import add_fitness, get_all_fitness, update_fitness, delete_fitness
from datetime import date

# 初始化数据库
from models.database import init_db
init_db()

# 页面标题
st.title("用户与健身管理系统")

# 固定的健身活动选项
ACTIVITIES = ["胸部", "背部", "手臂", "肩部", "腹部", "腿部", "有氧"]

# 侧边栏选择页面
page = st.sidebar.radio("选择功能", ["用户管理", "健身记录管理"])

if page == "用户管理":
    st.header("用户管理")

    # 显示用户列表
    users = get_all_users()
    if users:
        user_data = [{"用户 ID": user.user_id, "用户名": user.username, "邮箱": user.email} for user in users]
        st.table(user_data)
    else:
        st.info("暂无用户数据。")

    # 添加用户
    with st.expander("添加用户"):
        with st.form("add_user_form"):
            username = st.text_input("用户名")
            email = st.text_input("邮箱（可选）")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    add_user(username=username, password="default_password", email=email)
                    st.success("用户添加成功！")
                except Exception as e:
                    st.error(f"添加失败: {str(e)}")

    # 更新用户
    with st.expander("更新用户"):
        user_id_to_update = st.text_input("输入要更新的用户 ID")
        new_username = st.text_input("新用户名")
        new_email = st.text_input("新邮箱")
        if st.button("更新用户"):
            try:
                update_user(user_id=user_id_to_update, username=new_username, email=new_email)
                st.success("用户更新成功！")
            except Exception as e:
                st.error(f"更新失败: {str(e)}")

    # 删除用户
    with st.expander("删除用户"):
        user_id_to_delete = st.text_input("输入要删除的用户 ID")
        if st.button("删除用户"):
            try:
                delete_user(user_id=user_id_to_delete)
                st.success("用户删除成功！")
            except Exception as e:
                st.error(f"删除失败: {str(e)}")

elif page == "健身记录管理":
    st.header("健身记录管理")

    # 显示健身记录列表
    fitness_records = get_all_fitness()
    if fitness_records:
        fitness_data = [
            {
                "健身 ID": record.fitness_id,
                "日期": record.activity_date,
                "活动": ", ".join(record.activities),
                "状态": "已健身" if record.status else "未健身",
                "用户 ID": record.user_id,
            }
            for record in fitness_records
        ]
        st.table(fitness_data)
    else:
        st.info("暂无健身记录数据。")

    # 添加健身记录
    with st.expander("添加健身记录"):
        with st.form("add_fitness_form"):
            activity_date = st.date_input("健身日期")
            activities = st.multiselect("健身活动（多选）", ACTIVITIES)
            status = st.selectbox("健身状态", [0, 1], format_func=lambda x: "未健身" if x == 0 else "已健身")
            user_id = st.text_input("用户 ID（可选）")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    if not activities:
                        st.error("请至少选择一项健身活动！")
                    else:
                        add_fitness(activity_date=activity_date, activities=activities, status=status, user_id=user_id or None)
                        st.success("健身记录添加成功！")
                except Exception as e:
                    st.error(f"添加失败: {str(e)}")

    # 更新健身记录
    with st.expander("更新健身记录"):
        fitness_id_to_update = st.text_input("输入要更新的健身记录 ID")
        new_activities = st.multiselect("新健身活动（多选）", ACTIVITIES)
        new_status = st.selectbox("新健身状态", [0, 1], format_func=lambda x: "未健身" if x == 0 else "已健身")
        if st.button("更新健身记录"):
            try:
                if not new_activities:
                    st.error("请至少选择一项健身活动！")
                else:
                    update_fitness(fitness_id=fitness_id_to_update, activities=new_activities, status=new_status)
                    st.success("健身记录更新成功！")
            except Exception as e:
                st.error(f"更新失败: {str(e)}")

    # 删除健身记录
    with st.expander("删除健身记录"):
        fitness_id_to_delete = st.text_input("输入要删除的健身记录 ID")
        if st.button("删除健身记录"):
            try:
                delete_fitness(fitness_id=fitness_id_to_delete)
                st.success("健身记录删除成功！")
            except Exception as e:
                st.error(f"删除失败: {str(e)}")