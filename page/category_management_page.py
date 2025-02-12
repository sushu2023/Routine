import streamlit as st
import pandas as pd
from models.account_model import Category, create_category, get_all_categories, delete_category
from models.database import init_db

# 初始化数据库
init_db()

def category_management_page():
    # 获取所有分类数据
    categories = get_all_categories()
    
    # 页面标题
    st.header("分类管理")

    # 显示分类列表
    if categories:
        category_data = [{"分类ID": category.category_id, "名称": category.name, "备注": category.remark} for category in categories]
        df_categories = pd.DataFrame(category_data)
        st.dataframe(df_categories, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无分类数据。")

    # 侧边栏：添加分类
    with st.sidebar.expander("添加分类"):
        with st.form("add_category_form"):
            name = st.text_input("分类名称")
            remark = st.text_input("备注（可选）")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    create_category(name=name, remark=remark)
                    st.toast("分类添加成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新分类
    if categories:
        with st.sidebar.expander("更新分类"):
            category_to_update = st.selectbox("选择要更新的分类", [category.name for category in categories], key="update_category_select")
            selected_category = next((c for c in categories if c.name == category_to_update), None)
            new_name = st.text_input("新分类名称", value=selected_category.name)
            new_remark = st.text_input("新备注", value=selected_category.remark)
            if st.button("更新分类"):
                try:
                    update_category(category_id=selected_category.category_id, name=new_name, remark=new_remark)
                    st.toast("分类更新成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除分类
    if categories:
        with st.sidebar.expander("删除分类"):
            category_to_delete = st.selectbox("选择要删除的分类", [category.name for category in categories], key="delete_category_select")
            selected_category = next((c for c in categories if c.name == category_to_delete), None)
            if st.button("删除分类"):
                try:
                    delete_category(category_id=selected_category.category_id)
                    st.toast("分类删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")