import streamlit as st
import pandas as pd
from models.category_model import add_category, get_all_categories, update_category, delete_category, get_category_by_id

# 初始化数据库
from models.database import init_db
init_db()

def category_management_page():
    # 页面标题
    st.header("分类管理")

    # 获取所有分类数据
    categories = get_all_categories()
    if categories:
        category_data = [{"分类 ID": category.category_id, "名称": category.name, "备注": category.remark} for category in categories]
        df_categories = pd.DataFrame(category_data)
        st.dataframe(df_categories, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无分类数据。")

    # 侧边栏：添加分类
    with st.sidebar.expander("添加分类"):
        with st.form("add_category_form"):
            category_id = st.text_input("分类 ID（需唯一）")  # 新增输入框
            name = st.text_input("分类名称")
            remark = st.text_input("备注（可选）", "")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    if not category_id:
                        st.toast("分类 ID 不能为空！", icon="❌")
                    else:
                        add_category(category_id=category_id, name=name, remark=remark)
                        st.toast("分类添加成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新分类
    if categories:
        with st.sidebar.expander("更新分类"):
            category_to_update = st.selectbox(
                "选择要更新的分类",
                [f"{category.name} ({category.category_id})" for category in categories],
                key="update_category_select"
            )
            category_id_to_update = categories[
                [f"{c.name} ({c.category_id})" for c in categories].index(category_to_update)
            ].category_id
            new_name = st.text_input("新分类名称")
            new_remark = st.text_input("新备注（可选）", "")
            if st.button("更新分类"):
                try:
                    update_category(category_id=category_id_to_update, name=new_name, remark=new_remark)
                    st.toast("分类更新成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除分类
    if categories:
        with st.sidebar.expander("删除分类"):
            category_to_delete = st.selectbox(
                "选择要删除的分类",
                [f"{category.name} ({category.category_id})" for category in categories],
                key="delete_category_select"
            )
            category_id_to_delete = categories[
                [f"{c.name} ({c.category_id})" for c in categories].index(category_to_delete)
            ].category_id
            if st.button("删除分类"):
                try:
                    delete_category(category_id=category_id_to_delete)
                    st.toast("分类删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")