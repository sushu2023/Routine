import streamlit as st
import altair as alt
import pandas as pd

# 设置页面标题
st.title("Vega-Altair 横向条形图示例")

# 创建示例数据
data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'],  # 类别
    'Values': [4, 7, 1, 8, 3]               # 值
})

# 使用 Altair 创建横向条形图
chart = alt.Chart(data).mark_bar().encode(
    y='Category',       # Y 轴为类别（横向排列）
    x='Values',         # X 轴为值
    color='Category',   # 根据类别着色
    tooltip=['Category', 'Values']  # 添加悬停提示
).properties(
    width=600,         # 设置图表宽度
    height=300         # 设置图表高度
)

# 使用 Streamlit 输出图表
st.altair_chart(chart, use_container_width=True)

# 显示原始数据
st.write("以下是使用的数据：")
st.dataframe(data)