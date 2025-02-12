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

# 定义页面
pages = {
    "日常仪表盘": [
        st.Page(routine_dashboard_page, title="日常仪表盘"),
    ],
    "数据管理": [
        st.Page(user_management_page, title="用户管理"),
        st.Page(fitness_management_page, title="健身记录管理"),
        st.Page(lambda: st.write("消费记录功能待开发"), title="消费记录管理"),
    ],
}

# 创建导航
pg = st.navigation(pages)
selected_page = pg.run()

# 渲染选中的页面
if selected_page:
    selected_page.run()