import streamlit as st

st.set_page_config(page_title="My Railway App", page_icon="🚀", layout="centered")

st.title("تطبيقي على Railway")
st.write("هذا تطبيق Streamlit شغال على Railway")

name = st.text_input("اكتب اسمك")

number = st.number_input("ادخل رقم", value=0.0)

if st.button("تشغيل"):
    if name.strip() == "":
        st.warning("رجاءً اكتب الاسم")
    else:
        result = number * 2
        st.success(f"هلا {name}")
        st.write(f"الناتج هو: {result}")
