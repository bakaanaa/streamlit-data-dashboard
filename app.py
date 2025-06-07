import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io


st.subheader("Dash Board",divider="rainbow")
st.markdown("""
    This tool help you process and analyst data
""")

def uploadfile():
    uploaded_file = st.file_uploader("📁 Chọn file CSV", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Dữ liệu gốc")
        st.dataframe(df)
        return df
    return None  

def infomation(df):
    st.subheader("ℹ️ Thông tin (df.info())")

    info_df = pd.DataFrame({
        "Tên cột": df.columns,
        "Kiểu dữ liệu": df.dtypes.values,
        "Số giá trị không null": df.notnull().sum().values,
        "Số giá trị null": df.isnull().sum().values,
        "Tỷ lệ null (%)": (df.isnull().mean() * 100).round(2).values
    })

    st.dataframe(info_df)

    if df.isnull().values.any():
        st.warning("⚠️ Có giá trị null — tiến hành xử lý...")
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

        st.success("✅ Đã xử lý giá trị null")

       
        st.subheader("📌 df.info() sau xử lý null:")
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

    st.subheader("📊 Thống kê mô tả (df.describe())")
    st.dataframe(df.describe())

    st.subheader("🔗 Ma trận tương quan (df.corr())")
    st.dataframe(df.corr(numeric_only=True))




def side_bar(df):
    st.sidebar.header("🎛️ Bộ lọc dữ liệu")
    categorycolumn = df.select_dtypes(include=['object', 'category']).columns.tolist()
    selected_category = st.sidebar.multiselect("🗂️ Chọn cột phân loại (categorical)", categorycolumn)

    numericalcolumn = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    selected_numericals = st.sidebar.multiselect("🔢 Chọn cột số (numerical)", numericalcolumn)

    numerical_filters = {}
    if selected_numericals:
        st.sidebar.markdown("### 📉 Lọc theo khoảng giá trị")
        for col in selected_numericals:
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            step = (max_val - min_val) / 100 if max_val != min_val else 1.0
            selected_range = st.sidebar.slider(
                f"{col}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=step
            )
            numerical_filters[col] = selected_range

    filtered_df = df.copy()

    for col, (min_val, max_val) in numerical_filters.items():
        filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]

    st.subheader("📌 Dữ liệu sau khi lọc")
    columns_to_display = selected_category + selected_numericals
    if columns_to_display:
        filtered_df=filtered_df[columns_to_display]
        st.write("Dữ liệu lọc rồi")
        st.dataframe(filtered_df)
        return filtered_df
    
    st.write("Dữ liệu chưa lọc")
    st.dataframe(filtered_df)
    return filtered_df

def chartsection(filtered_df):
    st.subheader("Data Visuallize")
    st.sidebar.title('Visualize')
    chart_type=st.sidebar.selectbox("Choose Chart",
                         options=("Line Chart","Bar Chart","Pie Chart","Histogram","Boxplot Chart","Scatter plot"),
                          placeholder="Select contact method...",
                          index=None)
    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    category_cols= filtered_df.select_dtypes(include=['object', 'category']).columns.tolist()

    if chart_type in ["Line Chart", "Scatter plot","Boxplot Chart"]:
        if len(numeric_cols) < 2:
            st.warning("Cần ít nhất 2 cột số để vẽ biểu đồ.")
            return
        
        x_axis = st.selectbox("Chọn trục X", numeric_cols)
        y_axis = st.selectbox("Chọn trục Y", [col for col in numeric_cols if col != x_axis])

        if chart_type == "Line Chart":
            st.write("Bạn đã chọn biểu đồ:",chart_type)
            fig,ax=plt.subplots(figsize=(10, 5))
            ax.plot(filtered_df[x_axis],filtered_df[y_axis])
            plt.xlabel(str(x_axis))
            plt.ylabel(str(y_axis))
            st.pyplot(fig)
        
        elif chart_type=="Scatter plot":
            st.write("Bạn đã chọn biểu đồ:",chart_type)
            fig=plt.figure(figsize=(5,5))
            plt.scatter(filtered_df[x_axis],filtered_df[y_axis])
            st.pyplot(fig)
        elif chart_type=="Boxplot Chart":
            st.write("Bạn đã chọn biểu đồ:",chart_type)
            fig=plt.figure(figsize=(5,5))
            plt.boxplot([filtered_df[col] for col in numeric_cols],tick_labels=numeric_cols)
            plt.xticks(rotation=45)
            st.pyplot(fig)



df = uploadfile()
if df is not None:
    infomation(df)
    filtered_df=side_bar(df)
    chartsection(filtered_df)
else:
    st.info("📌 Vui lòng upload file CSV để bắt đầu.")