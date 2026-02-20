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
    st.write(df_revenue.head())
    
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
    
total_revenue = calculate_total(df_revenue, 'Omset')
total_grossprofit = calculate_total(df_revenue, 'Gross Profit')


# Streamlit App
def main():

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue bulan ini", f"Rp {total_revenue:,.0f}", delta=f"{total_revenue:,.0f}")
    with col2:
        st.metric("Total Gross Profit bulan ini", f"Rp {total_grossprofit:,.0f}", delta=f"{total_grossprofit:,.0f}")

if __name__ == "__main__":
    main()
