import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
from babel.numbers import format_currency
sns.set(style='dark')

# Menyiapkan data all_data
all_df = pd.read_csv('all_data.csv')

# Menyiapkan jumlah order harian
def create_daily_orders_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])  # Convert to datetime
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# Menyiapkan kategori produk yang paling banyak dan sedikit  
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")['product_id'].count().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Menyiapkan tingkat kepuasan customer terhadap layanan e-commerce
def create_byrating(df):
    rating_df = df['review_score'].value_counts().sort_values(ascending=False)
    max_count_rating = rating_df.idxmax()
    return (rating_df, max_count_rating)

# Menyiapkan kota yang memiliki customer paling banyak
def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.count().sort_values(ascending=False).reset_index()
    bycity_df.rename(columns={
        "customer_city": "City",
        "customer_id": "Total Customers"
    }, inplace=True)
    
    return bycity_df


rfm_df = pd.read_csv('rfm_df.csv')

# Menyiapkan filter
min_date = pd.to_datetime(all_df['order_approved_at']).dt.date.min()
max_date = pd.to_datetime(all_df['order_approved_at']).dt.date.max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/ec/Shopping-cart-white-icon.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value= min_date,
        max_value= max_date,
        value=[min_date, max_date]
    )

# Penyimpanan data yang telah difilter
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Memanggil helper function
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
rating_df,max_count_rating = create_byrating(main_df)
bycity_df = create_bycity_df(main_df)
rfm_df = create_rfm_df(main_df)

# Menyiapkan dashboard
st.header('E-commerce Dashboard :sparkles:')

# Jumlah order harian
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Kategori produk yang paling banyak dan sedikit  
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="product_id", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="product_id", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

# Membuat tingkat kepuasan pelanggan
st.header("E-Commerce Service Rating")

colors = ["#90CAF9" if score == max_count_rating else "#D3D3D3" for score in rating_df.index]

plt.figure(figsize=(10, 5))
sns.barplot(
            x=rating_df.index, 
            y=rating_df.values, 
            order=rating_df.index,
            palette=colors,
            )

plt.title("E-Commerce Service Rating", fontsize=30)
plt.xlabel("Rating", fontsize=15)
plt.ylabel("Customer", fontsize=15)
plt.xticks(fontsize=12)
st.pyplot(plt)

# Kota yang memiliki customer paling banyak
st.subheader("Customer Demographics")
top_city = bycity_df.head(5)
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="Total Customers", 
    y="City",
    data=top_city.sort_values(by="Total Customers", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by City", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# RFM
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(28, 14))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="Recency", x="Customer_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=20)
ax[0].tick_params(axis='x', labelsize=17)
ax[0].set_xticks([])
 
sns.barplot(y="Frequency", x="Customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=20)
ax[1].tick_params(axis='x', labelsize=17)
ax[1].set_xticks([])
 
sns.barplot(y="Monetary", x="Customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=20)
ax[2].tick_params(axis='x', labelsize=17)
ax[2].set_xticks([])
 
st.pyplot(fig)
 
st.caption('Copyright (c) Steven C Michael 2024')
