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
    df = pd.DataFrame(data[1:], columns=data[0])
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
    total = pd.to_numeric(df[column_name], errors='coerce').sum()
    return total
    
total_revenue = calculate_total(df_revenue, 'Omset')


# Streamlit App
def main():

    st.metric("Total Revenue", f"Rp {total_revenue:,.0f}", delta=f"{total_revenue:,.0f}")

if __name__ == "__main__":
    main()

