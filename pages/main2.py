import streamlit as st


if "num" not in st.session_state:
    st.session_state.num = 0

clicked = st.button("+1")

if clicked:
    st.session_state.num += 1

st.write(st.session_state.num)
