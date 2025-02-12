import streamlit as st
import pandas as pd
from models.item_model import add_item, get_all_items, update_item, delete_item, get_item_by_id
from models.category_model import get_all_categories

# 初始化数据库
from models.database import init_db
init_db()

def item_management_page():
    # 页面标题
    st.header("项目管理")

    # 获取所有分类数据（用于下拉列表）
    categories = get_all_categories()
    category_options = {category.name: category.category_id for category in categories} if categories else {}

    # 获取所有项目数据
    items = get_all_items()
    if items:
        item_data = [
            {
                "项目 ID": item.item_id,
                "名称": item.name,
                "所属分类": next((c.name for c in categories if c.category_id == item.category_id), "未知分类"),
                "备注": item.remark
            }
            for item in items
        ]
        df_items = pd.DataFrame(item_data)
        st.dataframe(df_items, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
    else:
        st.info("暂无项目数据。")

    # 侧边栏：添加项目
    with st.sidebar.expander("添加项目"):
        with st.form("add_item_form"):
            name = st.text_input("项目名称")
            category_name = st.selectbox("所属分类", list(category_options.keys())) if categories else None
            remark = st.text_input("备注（可选）", "")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    if not categories:
                        st.toast("请先添加分类！", icon="❌")
                    else:
                        category_id = category_options[category_name]
                        add_item(category_id=category_id, name=name, remark=remark)
                        st.toast("项目添加成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：更新项目
    if items and categories:
        with st.sidebar.expander("更新项目"):
            item_to_update = st.selectbox(
                "选择要更新的项目",
                [f"{item.name} ({item.item_id})" for item in items],
                key="update_item_select"
            )
            item_id_to_update = items[
                [f"{i.name} ({i.item_id})" for i in items].index(item_to_update)
            ].item_id
            new_name = st.text_input("新项目名称")
            new_category_name = st.selectbox("新所属分类", list(category_options.keys()))
            new_remark = st.text_input("新备注（可选）", "")
            if st.button("更新项目"):
                try:
                    new_category_id = category_options[new_category_name]
                    update_item(item_id=item_id_to_update, name=new_name, remark=new_remark)
                    st.toast("项目更新成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"更新失败: {str(e)}", icon="❌")

    # 侧边栏：删除项目
    if items:
        with st.sidebar.expander("删除项目"):
            item_to_delete = st.selectbox(
                "选择要删除的项目",
                [f"{item.name} ({item.item_id})" for item in items],
                key="delete_item_select"
            )
            item_id_to_delete = items[
                [f"{i.name} ({i.item_id})" for i in items].index(item_to_delete)
            ].item_id
            if st.button("删除项目"):
                try:
                    delete_item(item_id=item_id_to_delete)
                    st.toast("项目删除成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"删除失败: {str(e)}", icon="❌")