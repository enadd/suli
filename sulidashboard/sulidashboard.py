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
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

st.set_page_config(layout="wide")
st.title('Dashboard Distributor Suli 5 Tangerang Selatan')
# Refresh page every 60 seconds
st_autorefresh(interval=5 * 1000)

@st.cache_data
def get_data():
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
    sheet = spreadsheet.get_worksheet(0)
    data = sheet.get_all_values()
    df_PI = pd.DataFrame(data[1:], columns=data[0])
    return df_PI

# Sheets Publikasi Internasional
# df_PI = pd.read_excel('Form Capaian PRSDI.xlsx', sheet_name='PI')
# dfl_PI = get_data()
df_PI = get_data()

st.write(df_PI.columns)

st.write(df_PI.columns.tolist())
def plot_piechart(df_PI):
    # Hitung jumlah masing-masing barang
    count_df = df_PI['Nama_Barang'].value_counts().reset_index()
    count_df.columns = ['Nama_Barang', 'Jumlah']

    # Buat pie chart dengan Plotly
    fig = px.pie(count_df, names='Nama_Barang', values='Jumlah', hole=0.3)

    # Atur posisi teks label di luar batang
    fig.update_traces(textinfo='label+value+percent', textposition='inside')
    return fig


# Streamlit App
def main():
    """### **Data Publikasi Internasional**"""

    # Menampilkan Pie Chart dan Bar Chart
    fig1 = plot_piechart(df_PI)
    st.plotly_chart(fig1)
    
if __name__ == "__main__":
    main()






