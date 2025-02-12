import streamlit as st
from models.fitness_model import add_fitness, get_all_fitness, update_fitness, delete_fitness
from datetime import date

# 初始化数据库
from models.database import init_db
init_db()

# 获取所有用户数据（用于下拉列表）
from models.user_model import get_all_users
users = get_all_users()
user_options = {user.username: user.user_id for user in users} if users else {}

# 固定的健身活动选项
ACTIVITIES = ["胸部", "背部", "手臂", "肩部", "腹部", "腿部", "有氧", "未健身"]

st.header("健身活动管理")

# 获取所有健身记录数据
fitness_records = get_all_fitness()

# 显示健身记录列表
if fitness_records:
    fitness_data = [
        {
            "日期": record.activity_date,
            "活动": ", ".join(record.activities),
            "状态": "已健身" if record.status else "未健身",
            "用户": next((u.username for u in users if u.user_id == record.user_id), "未知用户"),
        }
        for record in fitness_records
    ]
    st.dataframe(fitness_data, use_container_width=True, hide_index=True)
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
                if "未健身" in activities and len(activities) > 1:
                    st.toast("选择‘未健身’时不能同时选择其他活动！", icon="❌")
                elif not activities:
                    st.toast("请至少选择一项健身活动！", icon="❌")
                elif not users:
                    st.toast("无法添加健身记录，请先添加用户！", icon="❌")
                else:
                    user_id = user_options[user_name]
                    status = 0 if "未健身" in activities else 1
                    activities = [] if "未健身" in activities else activities
                    add_fitness(activity_date=activity_date, activities=activities, status=status, user_id=user_id)
                    st.toast("健身记录添加成功！", icon="✅")
                    st.rerun()
            except Exception as e:
                st.toast(f"添加失败: {str(e)}", icon="❌")

# 更新健身记录
if fitness_records and users:
    with st.expander("更新健身记录"):
        fitness_to_update = st.selectbox(
            "选择要更新的健身记录",
            [f"{record.activity_date} ({', '.join(record.activities)})" for record in fitness_records],
        )
        fitness_id_to_update = fitness_records[
            [f"{r.activity_date} ({', '.join(r.activities)})" for r in fitness_records].index(fitness_to_update)
        ].fitness_id
        new_activities = st.multiselect("新健身活动（多选）", ACTIVITIES)
        new_user_name = st.selectbox("新用户", list(user_options.keys()))
        if st.button("更新健身记录"):
            try:
                if "未健身" in new_activities and len(new_activities) > 1:
                    st.toast("选择‘未健身’时不能同时选择其他活动！", icon="❌")
                elif not new_activities:
                    st.toast("请至少选择一项健身活动！", icon="❌")
                else:
                    new_user_id = user_options[new_user_name]
                    status = 0 if "未健身" in new_activities else 1
                    new_activities = [] if "未健身" in new_activities else new_activities
                    update_fitness(fitness_id=fitness_id_to_update, activities=new_activities, status=status)
                    st.toast("健身记录更新成功！", icon="✅")
                    st.rerun()
            except Exception as e:
                st.toast(f"更新失败: {str(e)}", icon="❌")

# 删除健身记录
if fitness_records:
    with st.expander("删除健身记录"):
        fitness_to_delete = st.selectbox(
            "选择要删除的健身记录",
            [f"{record.activity_date} ({', '.join(record.activities)})" for record in fitness_records],
        )
        fitness_id_to_delete = fitness_records[
            [f"{r.activity_date} ({', '.join(r.activities)})" for r in fitness_records].index(fitness_to_delete)
        ].fitness_id
        if st.button("删除健身记录"):
            try:
                delete_fitness(fitness_id=fitness_id_to_delete)
                st.toast("健身记录删除成功！", icon="✅")
                st.rerun()
            except Exception as e:
                st.toast(f"删除失败: {str(e)}", icon="❌")