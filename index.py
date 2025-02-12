import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="Routine - 日常生活管理系统",  # 网页标题
    page_icon="📅",                          # 使用 Emoji 表情作为图标
    layout="wide",                           # 页面布局模式
    initial_sidebar_state="expanded"         # 侧边栏默认展开
)

# 导入页面逻辑（注意路径改为 "page"）
from page.routine_dashboard import routine_dashboard_page
from page.user_management import user_management_page
from page.fitness_management import fitness_management_page
from page.category_management import category_management_page
from page.item_management import item_management_page
from page.account_book_management import account_book_management_page

# 定义页面
pages = {
    "图表": [
        st.Page(routine_dashboard_page, title="图表分析"),
    ],
    "主数据": [
        st.Page(fitness_management_page, title="健身管理"),
        st.Page(account_book_management_page, title="账单管理"),
    ],
    "元数据": [
        st.Page(user_management_page, title="用户管理"),
        st.Page(category_management_page, title="分类管理"),
        st.Page(item_management_page, title="分类项目管理"),
    ],
}

# 创建导航
pg = st.navigation(pages)
selected_page = pg.run()

# 渲染选中的页面
if selected_page:
    selected_page.run()