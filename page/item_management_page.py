import streamlit as st
import pandas as pd
from models.account_model import Item, create_item, get_items_by_category, delete_item
from models.account_crud import get_all_categories
from models.database import init_db

# 初始化数据库
init_db()

def item_management_page():
    # 获取所有分类和项目数据
    categories = get_all_categories()
    category_options = {category.name: category.category_id for category in categories} if categories else {}

    # 页面标题
    st.header("项目管理")

    # 显示项目列表
    if categories:
        selected_category = st.selectbox("选择分类", list(category_options.keys()))
        items = get_items_by_category(category_id=category_options[selected_category])
        if items:
            item_data = [{"项目ID": item.item_id, "名称": item.name, "备注": item.remark} for item in items]
            df_items = pd.DataFrame(item_data)
            st.dataframe(df_items, use_container_width=True, hide_index=True)  # 使用 DataFrame 显示，隐藏索引
        else:
            st.info("该分类下暂无项目数据。")
    else:
        st.info("暂无分类数据，请先添加分类。")

    # 侧边栏：添加项目
    with st.sidebar.expander("添加项目"):
        with st.form("add_item_form"):
            item_id = st.text_input("项目ID（唯一标识）")
            category = st.selectbox("所属分类", list(category_options.keys()))
            name = st.text_input("项目名称")
            remark = st.text_input("备注（可选）")
            submitted = st.form_submit_button("提交")
            if submitted:
                try:
                    create_item(item_id=item_id, category_id=category_options[category], name=name, remark=remark)
                    st.toast("项目添加成功！", icon="✅")
                    st.rerun()  # 自动刷新页面
                except Exception as e:
                    st.toast(f"添加失败: {str(e)}", icon="❌")

    # 侧边栏：删除项目
    if categories:
        with st.sidebar.expander("删除项目"):
            selected_category = st.selectbox("选择分类", list(category_options.keys()), key="delete_item_category_select")
            items = get_items_by_category(category_id=category_options[selected_category])
            if items:
                item_to_delete = st.selectbox("选择要删除的项目", [item.name for item in items], key="delete_item_select")
                selected_item = next((i for i in items if i.name == item_to_delete), None)
                if st.button("删除项目"):
                    try:
                        delete_item(item_id=selected_item.item_id)
                        st.toast("项目删除成功！", icon="✅")
                        st.rerun()  # 自动刷新页面
                    except Exception as e:
                        st.toast(f"删除失败: {str(e)}", icon="❌")