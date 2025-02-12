import streamlit as st

# 设置页面配置，默认展开侧边栏
st.set_page_config(initial_sidebar_state="expanded")

# 导入页面逻辑（注意路径改为 "page"）
from page.user_management import user_management_page
from page.fitness_management import fitness_management_page

# 定义页面
pages = {
    "图表": [
        st.Page(lambda: st.write("图表功能待开发"), title="图表分析"),
    ],
    "数据": [
        st.Page(user_management_page, title="用户管理"),
        st.Page(fitness_management_page, title="健身记录管理"),
    ],
}

# 创建导航
pg = st.navigation(pages)
selected_page = pg.run()

# 渲染选中的页面
if selected_page:
    selected_page.run()