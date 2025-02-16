import streamlit as st
import altair as alt
import pandas as pd

# 创建一个新的数据源：包含年月、收入和支出的数据
data = {
    "YearMonth": ["2024/01", "2024/02", "2024/03", "2024/04", "2024/05"],
    "Income": [7000, 5200, 6000, 8000, 9000],  # 收入金额
    "Expense": [5000, 6000, 4000, 7000, 10000]  # 支出金额
}

# 将数据转换为 Pandas DataFrame
source = pd.DataFrame(data)

# 数据预处理：计算每个年月的最大值和最小值
source["Max"] = source[["Income", "Expense"]].max(axis=1)  # 最大值
source["Min"] = source[["Income", "Expense"]].min(axis=1)  # 最小值
source["Type"] = source.apply(
    lambda row: "Income" if row["Income"] > row["Expense"] else "Expense", axis=1
)  # 确定哪个是最大值类型

# 将数据从宽格式转换为长格式
source_long = pd.melt(
    source,
    id_vars=["YearMonth", "Type"],
    value_vars=["Max", "Min"],
    var_name="ValueType",
    value_name="Amount"
)

# 创建堆叠条形图
chart = alt.Chart(source_long).mark_bar().encode(
    x=alt.X('YearMonth:O', title="年月"),       # 横坐标是年月
    y=alt.Y('Amount:Q', title="金额"),         # 纵坐标是金额
    color=alt.Color('ValueType:N', title="类型", scale=alt.Scale(scheme="category10")),  # 根据类型着色
    order=alt.Order('ValueType:N', sort='descending')  # 控制堆叠顺序
)

# 在 Streamlit 中显示图表
st.altair_chart(chart, use_container_width=True)