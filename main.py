import streamlit as st
import pandas as pd

st.title("📈 국가 간 MBTI 비교 도구")

data = {
    "country": ["한국", "미국", "일본", "독일"],
    "I (%)": [54, 45, 60, 48],
    "E (%)": [46, 55, 40, 52],
}

df = pd.DataFrame(data).set_index("country")

col1, col2 = st.columns(2)

with col1:
    country1 = st.selectbox("나라 1 선택", df.index, key="c1")
with col2:
    country2 = st.selectbox("나라 2 선택", df.index, key="c2")

st.write("---")

st.subheader(f"🔍 {country1} vs {country2} MBTI 비교")

compare_df = df.loc[[country1, country2]]
st.bar_chart(compare_df)
