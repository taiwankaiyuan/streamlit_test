import streamlit as st

with st.sidebar:
    name = st.text_input("請輸入姓名")
    if name:
        st.write(f"你好, {name}")

tab1, tab2, tab3 = st.tabs(["密碼", "聯繫方式", "喜好語言"])
with tab1:
    password = st.text_input("請輸入密碼", type= "password")
with tab2:
    paragraph = st.text_area("請輸入文字")
with tab3:
    st.number_input("請輸入年齡", value=30, min_value=18, max_value=99)


with st.expander("性別"):
    gender = st.radio("你的性別？", ["男性", "女性", "死人妖"])
    if gender:
        st.write(f"你是{gender}")

