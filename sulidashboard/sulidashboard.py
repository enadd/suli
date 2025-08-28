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
st_autorefresh(interval=60 * 1000)

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
#Data Preprocessing
def hapus_baris_kosong(df, kolom):
    # Ganti string kosong atau whitespace dengan NaN
    df[kolom] = df[kolom].replace(r'^\s*$', None, regex=True)
    
    # Hapus baris yang memiliki nilai NaN pada kolom tertentu
    df_bersih = df.dropna(subset=[kolom])
    
    return df_bersih

def formatting_data(df_pi):
    df_PI.columns = df_PI.iloc[3]
    df_pi = df_PI.iloc[4:].reset_index(drop=True)
    df_pi.columns.name = None
    # df_pi['Periode Input'] = pd.to_datetime(df_pi['Periode Input'], format='%B %d, %Y', errors='coerce')
    return df_pi

def drop_data(df_pi):
    df_pi = df_pi.drop(df_pi.columns[26:31], axis=1)
    # Drop kolom pada indeks 25
    # df_pi = df_pi.iloc[:, :-1]
    
    # Hapus baris yang mengandung nilai null pada kolom 'Judul'
    df_pi = df_pi.dropna(how='all')  # Hapus baris dengan semua nilai null
    return df_pi

# Kamus bulan
bulan_dict = {
    'Januari': 'January', 'Februari': 'February', 'Maret': 'March',
    'April': 'April', 'Mei': 'May', 'Juni': 'June',
    'Juli': 'July', 'Agustus': 'August', 'September': 'September',
    'Oktober': 'October', 'November': 'November', 'Desember': 'December'
}

# Fungsi untuk mengonversi nama bulan
def convert_month(date_str):
    for id_ind, id_eng in bulan_dict.items():
        if id_ind in date_str:
            return date_str.replace(id_ind, id_eng)
    return date_str

# Menggunakan cache untuk data preprocessing
@st.cache_data
def preprocessing(df_PI):
    df_pi = formatting_data(df_PI)
  # df_pi = rename_columns(df_pi)
    df_pi = drop_data(df_pi)
    #df_pi = hapus_baris_kosong(df_pi, "In_Id")
    #df_pi = hapus_baris_kosong(df_pi, "Tanggal_Pengiriman")
  #  df_pi = hapus_baris_kosong(df_pi, "JENJANG PENDIDIKAN DITEMPUH")
  #  df_pi = hapus_baris_kosong(df_pi, "STATUS")
    #df_pi['Periode Input'] = df_pi['Periode Input'].apply(convert_month)
    #df_pi['Periode Input'] = pd.to_datetime(df_pi['Periode Input'], format='%B %d, %Y', errors='coerce')
    #df_pi['Kategori'] = df_pi['Kategori'].replace(r'^\s*$', None, regex=True)
    #df_pi['Kategori'] = df_pi['Kategori'].fillna('Unknown')
    return df_pi

#Preprocessing Data
df_pi = preprocessing(df_PI)

def plot_piechart(df_pi):
    # Hitung jumlah masing-masing barang
    count_df = df_pi['Nama_Barang'].value_counts().reset_index()
    count_df.columns = ['Nama_Barang', 'Quantity']

    # Buat pie chart dengan Plotly
    fig = px.pie(count_df, names='Nama_Barang', values='Jumlah', hole=0.3)

    # Atur posisi teks label di luar batang
    fig.update_traces(textinfo='label+value+percent', textposition='inside')
    return fig


# Streamlit App
def main():
    """### **Data Publikasi Internasional**"""

    # Menampilkan Pie Chart dan Bar Chart
    fig = plot_piechart(df_pi)
    st.plotchart(fig)
    
if __name__ == "__main__":
    main()


