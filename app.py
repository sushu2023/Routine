import streamlit as st
import pandas as pd
from models.user_model import add_user, get_all_users, update_user, delete_user
from models.fitness_model import add_fitness, get_all_fitness, update_fitness, delete_fitness
from datetime import date

# 初始化数据库
from models.database import init_db
init_db()

# 页面标题
st.title("用户与健身管理系统")

# 获取所有用户数据（用于下拉列表）
users = get_all_users()
user_options = {user.username: user.user_id for user in users} if users else {}

# 固定的健身活动选项（新增“未健身”）
ACTIVITIES = ["胸部", "背部", "手臂", "肩部", "腹部", "腿部", "有氧", "未健身"]

# 侧边栏选择页面
page = st.sidebar.radio("选择功能", ["用户管理", "健身记录管理"])

if page == "用户管理":
    st.header("用户管理")

    # 显示用户列表（包括密码列）
    if users:
        user_data = [{"用户名": user.username, "密码": user.password, "邮箱": user.email} for user in users]
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
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
                    st.toast("用户添加成功！", icon="✅")  # 成功提示
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")  # 失败提示

    # 更新用户
    if users:
        with st.expander("更新用户"):
            user_to_update = st.selectbox("选择要更新的用户", list(user_options.keys()), key="update_user_select")
            new_username = st.text_input("新用户名")
            new_password = st.text_input("新密码", type="password")
            new_email = st.text_input("新邮箱")
            if st.button("更新用户"):
                try:
                    user_id = user_options[user_to_update]
                    update_user(user_id=user_id, username=new_username, password=new_password, email=new_email)
                    st.toast("用户更新成功！", icon="✅")  # 成功提示
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")  # 失败提示

    # 删除用户
    if users:
        with st.expander("删除用户"):
            user_to_delete = st.selectbox("选择要删除的用户", list(user_options.keys()), key="delete_user_select")
            if st.button("删除用户"):
                try:
                    user_id = user_options[user_to_delete]
                    delete_user(user_id=user_id)
                    st.toast("用户删除成功！", icon="✅")  # 成功提示
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")  # 失败提示

elif page == "健身记录管理":
    st.header("健身记录管理")

    # 获取所有健身记录数据
    fitness_records = get_all_fitness()

    # 按日期降序排序
    if fitness_records:
        fitness_records.sort(key=lambda x: x.activity_date, reverse=True)  # 按日期降序排列
        fitness_data = [
            {
                "日期": record.activity_date,
                "活动": ", ".join(record.activities),
                "状态": "已健身" if record.status else "未健身",
                "用户": next((u.username for u in users if u.user_id == record.user_id), "未知用户"),
            }
            for record in fitness_records
        ]
        df_fitness = pd.DataFrame(fitness_data)
        st.dataframe(df_fitness, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无健身记录数据。")

    # 添加健身记录
    with st.expander("添加健身记录"):
        with st.form("add_fitness_form"):
            activity_date = st.date_input("健身日期")
            activities = st.multiselect("健身活动（多选）", ACTIVITIES)
            if users:
                user_name = st.selectbox("用户", list(user_options.keys()))
            else:
                st.warning("请先添加用户！")
                user_name = None
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    # 检查是否选择了“未健身”
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

    # 更新健身记录
    if fitness_records and users:
        with st.expander("更新健身记录"):
            fitness_to_update = st.selectbox(
                "选择要更新的健身记录",
                [f"{record.activity_date} ({', '.join(record.activities)})" for record in fitness_records],
                key="update_fitness_select"
            )
            fitness_id_to_update = fitness_records[
                [f"{r.activity_date} ({', '.join(r.activities)})" for r in fitness_records].index(fitness_to_update)
            ].fitness_id
            new_activities = st.multiselect("新健身活动（多选）", ACTIVITIES)
            new_user_name = st.selectbox("新用户", list(user_options.keys()))
            if st.button("更新健身记录"):
                try:
                    # 检查是否选择了“未健身”
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

    # 删除健身记录
    if fitness_records:
        with st.expander("删除健身记录"):
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