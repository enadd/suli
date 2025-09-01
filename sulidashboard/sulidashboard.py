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
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

st_autorefresh(interval=60 * 1000)
st.set_page_config(layout="wide")
st.title('Dashboard Distributor Suli 5 Tangerang Selatan')
# Refresh page every 60 seconds

@st.cache_data(ttl=60)
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
    df_SL = pd.DataFrame(data[1:], columns=data[0])
    return df_SL

# Sheets Publikasi Internasional
# df_SL = pd.read_excel('Form Capaian PRSDI.xlsx', sheet_name='SL')
# dfl_SL = get_data()
df_SL = get_data()

st.write(df_SL.columns)

st.write(df_SL.columns.tolist())

#Data Preprocessing
def hapus_baris_kosong(df, kolom):
    # Ganti string kosong atau whitespace dengan NaN
    df[kolom] = df[kolom].replace(r'^\s*$', None, regex=True)
    
    # Hapus baris yang memilisl nilai NaN pada kolom tertentu
    df_bersih = df.dropna(subset=[kolom])
    
    return df_bersih

# Menggunakan cache untuk data preprocessing
def preprocessing(df_SL):
    df_suli = hapus_baris_kosong(df_SL, "Nama Barang")
    return df_suli

#Preprocessing Data
df_sl = preprocessing(df_SL)

def tagihan(df_sl):
    df_sl['Omset'] = df_sl['Omset'].str.replace('Rp', '', regex=False)
    df_sl['Omset'] = df_sl['Omset'].str.replace(',', '', regex=False)
    df_sl['Omset'] = pd.to_numeric(df_sl['Omset'], errors='coerce')
    
    df_sl = df_sl[df_sl['Kategori'].isna() | (df_sl['Kategori'] != 'Sales')]
    
    df_sl = df_sl.dropna(subset=['Omset'])
    tagihan_counts = df_sl.groupby('Nama Customer')['Omset'].sum().reset_index(name='Count')
    return tagihan_counts

def total_sales(df_sl):
    # Pastikan kolom Tanggal Order dalam format datetime
    df_sl['Tanggal Order'] = pd.to_datetime(df_sl['Tanggal Order'], errors='coerce')

    # Filter data untuk bulan September
    september_data = df_sl[df_sl['Tanggal Order'].dt.month == 9]

    if not september_data.empty:
        # Hitung total omset (hilangkan 'Rp' dan koma agar bisa dijumlahkan)
        total = september_data['Omset'].sum()
        return total
    else:
        return 0

def jumlah_barang(df_sl):
    df_sl['Tanggal Order'] = pd.to_datetime(df_sl['Tanggal Order'], errors='coerce')
    filter_perbulan = df_sl[(df_sl['Tanggal Order'].dt.month == bulan) & (df_sl['Tanggal Order'].dt.year == tahun)]

    hasil = df_sl.groupby('Nama Barang')['Quantity'].sum().reset_index()
    return hasil

def pie_jumlahbarang(df_sl):
    # Konversi kolom Quantity ke numerik, paksa error jadi NaN
    df_sl['Quantity'] = pd.to_numeric(df_sl['Quantity'], errors='coerce')

    # Hapus baris yang Quantity-nya kosong atau bukan angka
    df_sl = df_sl.dropna(subset=['Quantity'])
    
    # Group by 'JENIS' and count the occurrences
    quantity_counts = df_sl.groupby('Nama Barang')['Quantity'].sum().reset_index(name='Count')

    # Create the bar chart using Plotly Express with color and text labels
    fig = px.pie(quantity_counts, names='Nama Barang', values='Count', hole=0.3)
                
    # Atur posisi teks label di luar batang
    fig.update_traces(textinfo='label+value+percent', textposition='inside')
   
    return fig

def bar_jumlahbarang(df_sl):
    # Konversi kolom Quantity ke numerik, paksa error jadi NaN
    df_sl['Quantity'] = pd.to_numeric(df_sl['Quantity'], errors='coerce')

    # Hapus baris yang Quantity-nya kosong atau bukan angka
    df_sl = df_sl.dropna(subset=['Quantity'])
    
    # Group by 'JENIS' and count the occurrences
    quantity_counts = df_sl.groupby('Nama Barang')['Quantity'].sum().reset_index(name='Count')

    # Create the bar chart using Plotly Express with color and text labels
    fig = px.bar(quantity_counts, x='Nama Barang', y='Count',
                 labels={'Nama Barang': 'Nama Barang', 'Count': 'Jumlah'},
                 color='Nama Barang', text='Count')  # Menambahkan parameter text untuk label
                
    # Atur posisi teks label di luar batang
    fig.update_traces(textposition='outside')
   
    return fig

# Streamlit App
def main():
    """### **Data Publikasi Internasional**"""

    df1 = tagihan(df_sl)
    df2 = jumlah_barang(df_sl)
    fig1 = pie_jumlahbarang(df_sl)
    fig2 = bar_jumlahbarang(df_sl)
    
    st.subheader("Tagihan Customer")
    st.dataframe(df1)

    st.subheader("Jumlah Barang per Bulan")
    st.dataframe(df2)
    
    st.markdown(
    f"<h2>Omset bulan ini: Rp{total_sales(df_sl):,.0f}</h2>",
    unsafe_allow_html=True
    )
             
    st.subheader("Barang Terjual")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1)
    with col2:
        st.plotly_chart(fig2)

    
if __name__ == "__main__":
    main()


















