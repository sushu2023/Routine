import altair as alt
import pandas as pd
import streamlit as st

source = pd.DataFrame({
    "YearMonth": ["2024/01", "2024/02", "2024/03", "2024/04", "2024/05"],
    "Days": [7, 15, 16, 18, 19],  # 健身天数
})

chart = (
    alt.Chart(source).mark_bar().encode(
    x='YearMonth',
    y='Days'
)
)

st.altair_chart(chart)