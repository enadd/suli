import streamlit as st
import plotly.express as px
import pandas as pd
from pyvis.network import Network
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import io
from IPython.core.display import HTML
import sys
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import calendar
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

st_autorefresh(interval=60 * 1000)
st.set_page_config(layout="wide")
st.title('Dashboard Distributor Suli 5 Tangerang Selatan 2026')
# Refresh page every 60 seconds

@st.cache_data(ttl=60)
def get_data(nama_sheet):
    # Tentukan scope untuk mengakses Google Sheets dan Google Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autentikasi menggunakan secrets dari Streamlit Cloud
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    
    client = gspread.authorize(credentials)

    # Akses Google Spreadsheet
    spreadsheet = client.open("Transaksi Masuk")
    sheet = spreadsheet.worksheet(nama_sheet)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# df_SL = pd.read_excel('Form Capaian PRSDI.xlsx', sheet_name='SL')
# dfl_SL = get_data()
try:
    df_revenue = get_data("Trans_Penjualan")
    df_expense = get_data("Expense")

    # Cek hasil
    st.success("Data berhasil dimuat!")
    st.subheader("Data Penjualan")
    
except Exception as e:
    st.error(f"Gagal mengambil data: {e}")


def calculate_total(df, column_name):
    if column_name in df.columns:
        series = df[column_name].astype(str)
        series = series.str.replace(r'[Rp.\s,]', '', regex=True)
        numeric_col = pd.to_numeric(series, errors='coerce')
        return numeric_col.fillna(0).sum()
    else:
        st.error(f"Kolom '{column_name}' tidak ada!")
        return 0

def calculate_groupby(df, group_column, target_column):
    if target_column in df.columns and group_column in df.columns:
        # 1. Bersihkan data (Sama seperti logika kamu)
        series = df[target_column].astype(str).str.replace(r'[Rp.\s,]', '', regex=True)
        
        # 2. Buat DataFrame sementara agar group_column dan target_column berada di satu wadah
        temp_df = df[[group_column]].copy() 
        temp_df[target_column] = pd.to_numeric(series, errors='coerce').fillna(0)
        
        # 3. Lakukan GroupBy
        return temp_df.groupby(group_column)[target_column].sum().reset_index()
    else:
        st.error(f"Kolom '{group_column}' atau '{target_column}' tidak ditemukan!")
        return pd.DataFrame() # Kembalikan DF kosong agar tidak error di UI

def calculate_monthly_item_sales(df, date_column, product_column, qty_column):
    if all(col in df.columns for col in [date_column, product_column, qty_column]):
        
        # 1. Pastikan tanggal dalam format datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # 2. Buat kolom Bulan
        df['Bulan'] = df[date_column].dt.to_period('M').astype(str)
        
        # 3. Pastikan Qty numerik
        df[qty_column] = pd.to_numeric(df[qty_column], errors='coerce').fillna(0)
        
        # 4. Group by Bulan & Produk
        grouped = df.groupby(['Bulan', product_column])[qty_column].sum().reset_index()
        
        # 5. Pivot supaya produk jadi kolom kanan
        pivot = grouped.pivot(index='Bulan', columns=product_column, values=qty_column).fillna(0)
        
        return pivot.reset_index()
    
    else:
        st.error("Kolom tidak ditemukan di DataFrame!")
        return pd.DataFrame()
        
#income
total_revenue = calculate_total(df_revenue, 'Revenue')
total_grossprofit = calculate_total(df_revenue, 'Gross Profit')

revenue_percustomer = (
    calculate_groupby(df_revenue, 'Nama Pelanggan', 'Revenue')
    .sort_values(by='Revenue', ascending=False)
    .head(5)
)

monthly_items = calculate_monthly_item_sales(
    df_revenue, 
    date_column='Tanggal Order', 
    product_column='Nama Produk', 
    qty_column='Qty'
)

monthly_revenue = calculate_monthly_item_sales(
    df_revenue, 
    date_column='Tanggal Order', 
    product_column='Nama Produk', 
    qty_column='Revenue'
)

#outcome
total_expense = calculate_total(df_expense, 'Jumlah')

#evaluate
operating_margin = (total_revenue - total_expense) / total_revenue

# Streamlit App
def main():

    st.subheader("Top 5 Customer")
    st.dataframe(revenue_percustomer)

    st.subheader("Income")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue bulan ini", f"Rp {total_revenue:,.0f}", delta=f"{total_revenue:,.0f}")
    with col2:
        st.metric("Total Gross Profit bulan ini", f"Rp {total_grossprofit:,.0f}", delta=f"{total_grossprofit:,.0f}")

    st.markdown("####Item terjual")
    st.dataframe(monthly_items)

    st.markdown("###Revenue per item")
    st.dataframe(monthly_revenue)

    st.subheader("Expense")
    st.metric("Total Expense bulan ini", f"Rp {total_expense:,.0f}", delta=f"{total_expense:,.0f}")
   
    st.subheader("Evaluate Metrics")
    st.metric(
            label="Operating Margin Bulan Ini", 
            value=f"{operating_margin:.2%}", 
            delta=f"{operating_margin:,.0f}"
            )

if __name__ == "__main__":
    main()

