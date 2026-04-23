import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="لوحة تحليل أسعار الدولار", page_icon="💵", layout="wide")

st.title("💵 لوحة تحليل أسعار الدولار")
st.write("ارفع ملف CSV أو Excel، فلتر البيانات، حللها، وارسمها، وخذ توقع بسيط.")

uploaded_file = st.file_uploader("ارفع ملف البيانات", type=["csv", "xlsx"])

df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("تم رفع الملف بنجاح")
    except Exception as e:
        st.error(f"صار خطأ بقراءة الملف: {e}")

if df is not None:
    st.subheader("📋 البيانات الأصلية")
    st.dataframe(df, use_container_width=True)

    all_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        date_column = st.selectbox(
            "اختر عمود التاريخ (اختياري)",
            ["بدون تاريخ"] + all_columns
        )

    with col2:
        if len(numeric_columns) == 0:
            st.error("ماكو أعمدة رقمية داخل الملف")
            st.stop()

        price_column = st.selectbox(
            "اختر عمود السعر",
            numeric_columns
        )

    filtered_df = df.copy()

    # تحويل التاريخ إذا اختار المستخدم عمود تاريخ
    if date_column != "بدون تاريخ":
        try:
            filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors="coerce")
            filtered_df = filtered_df.dropna(subset=[date_column])

            if not filtered_df.empty:
                min_date = filtered_df[date_column].min().date()
                max_date = filtered_df[date_column].max().date()

                st.subheader("📅 فلترة حسب التاريخ")
                start_date, end_date = st.date_input(
                    "اختر المدة الزمنية",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

                if start_date and end_date:
                    filtered_df = filtered_df[
                        (filtered_df[date_column].dt.date >= start_date) &
                        (filtered_df[date_column].dt.date <= end_date)
                    ]
        except Exception as e:
            st.warning(f"تعذر التعامل مع عمود التاريخ: {e}")

    st.subheader("📌 البيانات بعد الفلترة")
    st.dataframe(filtered_df, use_container_width=True)

    if filtered_df.empty:
        st.warning("لا توجد بيانات بعد الفلترة")
        st.stop()

    st.subheader("📊 الإحصائيات")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("عدد السجلات", int(filtered_df[price_column].count()))
    c2.metric("المتوسط", f"{filtered_df[price_column].mean():.2f}")
    c3.metric("أعلى سعر", f"{filtered_df[price_column].max():.2f}")
    c4.metric("أقل سعر", f"{filtered_df[price_column].min():.2f}")

    st.subheader("📈 الرسم البياني")

    chart_df = filtered_df[[price_column]].dropna().reset_index(drop=True)

    if date_column != "بدون تاريخ" and date_column in filtered_df.columns:
        chart_data = filtered_df[[date_column, price_column]].dropna().sort_values(by=date_column)

        fig, ax = plt.subplots()
        ax.plot(chart_data[date_column], chart_data[price_column], marker="o")
        ax.set_xlabel("التاريخ")
        ax.set_ylabel(price_column)
        ax.set_title(f"تغير {price_column} عبر الزمن")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        chart_df["index"] = range(1, len(chart_df) + 1)

        fig, ax = plt.subplots()
        ax.plot(chart_df["index"], chart_df[price_column], marker="o")
        ax.set_xlabel("رقم السجل")
        ax.set_ylabel(price_column)
        ax.set_title(f"تغير {price_column}")
        st.pyplot(fig)

    st.subheader("🤖 التوقع البسيط")

    prediction_df = filtered_df[[price_column]].dropna().reset_index(drop=True)
    prediction_df["index"] = range(1, len(prediction_df) + 1)

    if len(prediction_df) >= 2:
        X = prediction_df[["index"]]
        y = prediction_df[price_column]

        model = LinearRegression()
        model.fit(X, y)

        next_index = [[len(prediction_df) + 1]]
        prediction = model.predict(next_index)[0]

        st.success(f"التوقع للسجل القادم: {prediction:.2f}")

        future_x = pd.DataFrame({"index": range(1, len(prediction_df) + 2)})
        future_pred = model.predict(future_x)

        fig2, ax2 = plt.subplots()
        ax2.plot(prediction_df["index"], y, marker="o", label="الحقيقي")
        ax2.plot(future_x["index"], future_pred, marker="x", linestyle="--", label="التوقع")
        ax2.set_xlabel("رقم السجل")
        ax2.set_ylabel(price_column)
        ax2.set_title("مقارنة الحقيقي مع التوقع")
        ax2.legend()
        st.pyplot(fig2)
    else:
        st.info("لازم يكون عندك سجلين أو أكثر حتى يظهر التوقع")

    st.subheader("⬇️ تحميل البيانات بعد الفلترة")
    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="تحميل البيانات المفلترة CSV",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )
else:
    st.info("ارفع ملف CSV أو Excel حتى تبدأ")
