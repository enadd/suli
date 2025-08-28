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
    df_pi = hapus_baris_kosong(df_pi, "In_Id")
    df_pi = hapus_baris_kosong(df_pi, "Tanggal_Pengiriman")
  #  df_pi = hapus_baris_kosong(df_pi, "JENJANG PENDIDIKAN DITEMPUH")
  #  df_pi = hapus_baris_kosong(df_pi, "STATUS")
    #df_pi['Periode Input'] = df_pi['Periode Input'].apply(convert_month)
    #df_pi['Periode Input'] = pd.to_datetime(df_pi['Periode Input'], format='%B %d, %Y', errors='coerce')
    df_pi['Kategori'] = df_pi['Kategori'].replace(r'^\s*$', None, regex=True)
    df_pi['Kategori'] = df_pi['Kategori'].fillna('Unknown')
    return df_pi

#Preprocessing Data
df_pi = preprocessing(df_PI)

def total_sales(df_pi):
    jumlah sales = 

# Fungsi pie_chart yang sudah Anda buat
def pie_chart(df_pi):
    # Group by 'JENIS' and 'STATUS', then count the occurrences
    jenis_status_counts = df_pi.groupby(['JENJANG PENDIDIKAN DITEMPUH', 'STATUS'])['NAMA SDM IPTEK'].count().reset_index(name='Count')

    # Create a list of unique statuses
    statuses = jenis_status_counts['STATUS'].unique()

    # Create a figure with the hole for the donut chart
    fig = px.pie(hole=0.3)  # Set the hole property here

    # Add traces for each status
    for status in statuses:
        filtered_data = jenis_status_counts[jenis_status_counts['STATUS'] == status]
        fig.add_trace(px.pie(filtered_data, values='Count', names='JENJANG PENDIDIKAN DITEMPUH', hole=0.3).data[0])

    # Add trace for all data
    all_data = df_pi.groupby('JENJANG PENDIDIKAN DITEMPUH')['NAMA SDM IPTEK'].count().reset_index(name='Count')
    fig.add_trace(px.pie(all_data, values='Count', names='JENJANG PENDIDIKAN DITEMPUH', hole=0.3).data[0])
    fig.update_traces(textinfo='label+value+percent', textposition='inside')

    # Update layout to include dropdown (remove 'hole' from here)
    fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": "All",
                        "method": "update",
                        "args": [{"visible": [True] + [False]*len(statuses)},
                                {"title": "Jumlah S2/S3 per Status - All"}]
                    }
                ] + [
                    {
                        "label": status,
                        "method": "update",
                        "args": [{"visible": [False] + [status == s for s in statuses]},
                                {"title": f"Jumlah S2/S3 per Status - {status}"}]
                    }
                    for status in statuses
                ],
                "direction": "down",
                "showactive": True,
                "x": 0.95,  # Position x
                "y": 0.98,  # Position y
                "xanchor": "right",
                "yanchor": "top"
            }
        ]
    )

    return fig

def selisih(target, hasil):
    """
    Fungsi untuk menghitung selisih antara target dan hasil.
    """
    return target - hasil

def filter_s2_s3(df_pi):
    """
    Fungsi untuk menampilkan Nama SDM IPTEK dan Jenjang Pendidikan Ditempuh
    yang memiliki jenjang pendidikan S2 atau S3.
    """
    # Filter data untuk jenjang pendidikan S2 atau S3
    filtered_df_pi = df_pi[(df_pi['JENJANG PENDIDIKAN DITEMPUH'] == 'S2') | 
                         (df_pi['JENJANG PENDIDIKAN DITEMPUH'] == 'S3')]
    
    # Hanya menampilkan kolom Nama SDM IPTEK dan Jenjang Pendidikan Ditempuh
    return filtered_df_pi[['NAMA SDM IPTEK', 'JENJANG PENDIDIKAN DITEMPUH']]

# Menggunakan fungsi untuk filter
filtered_df = filter_s2_s3(df_pi)
target = df_pi['NAMA SDM IPTEK'].dropna().nunique()
hasil = len(filtered_df)
selisih_value = selisih(target, hasil)

chart_data = pd.DataFrame({
    "Kategori": ["Target", "Hasil", "Selisih"],
    "Jumlah": [target, hasil, selisih_value]
})
fig = px.bar(chart_data, 
             x="Jumlah", 
             y="Kategori", 
             orientation='h',
             color="Kategori",  # Tambahkan parameter warna berdasarkan kategori
             color_discrete_map={
             "Target": "blue",       
             "Hasil": "lightblue",    
             "Selisih": "red"   
    })
fig.update_traces(textposition='outside')

def get_unknown_status(df_pi):
    """
    Filter data untuk mendapatkan nama-nama dengan status 'unknown' atau kosong.
    
    Parameters:
        data (pd.DataFrame): DataFrame berisi data yang akan difilter.
        
    Returns:
        pd.DataFrame: DataFrame berisi nama dan status yang tidak diketahui.
    """
    # Filter data untuk status 'unknown' atau kosong
    unknown_data = df_pi[
        df_pi["JENJANG PENDIDIKAN DITEMPUH"].isnull() | 
        (df_pi['JENJANG PENDIDIKAN DITEMPUH'] == 'Unknown')
    ]

    # Pilih kolom yang relevan untuk output
    return unknown_data[["NAMA SDM IPTEK", "JENJANG PENDIDIKAN DITEMPUH"]]
    
def bar_chart(df_pi):
    # Group by 'JENIS' and count the occurrences
    jenis_counts = df_pi.groupby('JENJANG PENDIDIKAN DITEMPUH')['NAMA SDM IPTEK'].count().reset_index(name='Count')

    # Create the bar chart using Plotly Express with color and text labels
    fig = px.bar(jenis_counts, x='JENJANG PENDIDIKAN DITEMPUH', y='Count',
                 labels={'JENJANG PENDIDIKAN DITEMPUH': 'Jenjang Pendidikan', 'Count': 'Jumlah'},
                 color='JENJANG PENDIDIKAN DITEMPUH', text='Count')  # Menambahkan parameter text untuk label

    # Atur posisi teks label di luar batang
    fig.update_traces(textposition='outside')

    return fig    

def plot_barchart(df, col):
    # Ganti string kosong atau whitespace dengan NaN
    df[col] = df[col].replace(r'^\s*$', None, regex=True)
    # Ganti nilai null dengan 'Unknown'
    df[col] = df[col].fillna('Unknown')

    # Hitung jumlah masing-masing kelompok
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, 'Jumlah']
    # Urutkan dari besar ke kecil
    count_df = count_df.sort_values(by='Jumlah', ascending=True)

    # Buat bar chart dengan Plotly
    fig = px.bar(count_df, x='Jumlah', y=col, color='Jumlah',
                 color_continuous_scale='Blues', text='Jumlah')

    # Atur posisi teks label di luar batang
    fig.update_traces(textposition='outside')

    return fig

def plot_piechart(df):
    # Hitung jumlah masing-masing kategori reputasi
    count_df = df['JENJANG PENDIDIKAN DITEMPUH'].value_counts().reset_index()
    count_df.columns = ['JENJANG PENDIDIKAN DITEMPUH', 'Jumlah']

    # Buat pie chart dengan Plotly
    fig = px.pie(count_df, names='JENJANG PENDIDIKAN DITEMPUH', values='Jumlah', hole=0.3)

    # Atur posisi teks label di luar batang
    fig.update_traces(textinfo='label+value+percent', textposition='inside')
    return fig

def plot_piechart(status):
    # Hitung jumlah masing-masing kategori reputasi
    count_status = status['STATUS'].value_counts().reset_index()
    count_status.columns = ['STATUS', 'Jumlah']

    # Buat pie chart dengan Plotly
    fig = px.pie(count_status, names='STATUS', values='Jumlah', hole=0.3)

     # Atur posisi teks label di luar batang
    fig.update_traces(textinfo='label+value+percent', textposition='inside')
    return fig

# Streamlit App
def main():
    """### **Data Publikasi Internasional**"""
    st.dataframe(df_pi)

    # Menampilkan Pie Chart dan Bar Chart
    
    fig_pie = pie_chart(df_pi)
    fig_bar = bar_chart(df_pi)
    fig_bar1 = plot_barchart(df_pi, 'NAMA UNIVERSITAS')
    fig_bar2 = plot_barchart(df_pi, 'JENJANG PENDIDIKAN DITEMPUH')
    fig_pie1 = plot_piechart(df_pi)
    fig_bar3 = plot_barchart(df_pi, 'STATUS')

    # Create two columns
    col1, col2 = st.columns(2)
    
    # Menampilkan hasil filter s2 dan s3
    with col1:
        st.subheader("Nama dan Pendidikan yang Ditempuh")
        st.dataframe(filtered_df)

    # Panggil fungsi dan tampilkan di Streamlit
    with col2:
        st.subheader("Nama-Nama yang Belum Melanjutkan Studi S2/S3")

    # Hasil filter data
        unknown_status_data = get_unknown_status(df_pi)
        st.dataframe(unknown_status_data)
    
    # Menampilkan bar chart target
    st.subheader("Perbandingan Target, Hasil, dan Selisih Pendidikan S2/S3")
    st.plotly_chart(fig)
    # Tampilkan target, hasil, dan selisih
    st.write(f"**Target**: {target}")
    st.write(f"**SDM yang sedang menempuh studi**: {hasil}")
    st.write(f"**SDM yang belum lanjut studi**: {selisih_value}")
    
    # Create two columns
    col1, col2 = st.columns(2)

    # Display pie chart in the first column
    with col1:
        st.subheader("Pie Chart Jenjang Pendidikan")
        st.plotly_chart(fig_pie)
    # Display bar chart in the second column
    with col2:
        st.subheader("Bar Chart Perbandingan Jenjang Pendidikan")
        st.plotly_chart(fig_bar)

    # Create two columns
    col1, col2= st.columns(2)

    # Display pie chart in the first column
    with col1:
        st.subheader("Pie Chart Status Pendidikan")
        st.plotly_chart(fig_pie1)
        
    # Display bar chart in the second column
    with col2:
        st.subheader("Status Pendidikan")
        st.plotly_chart(fig_bar3)
        
    #Bar Chart Kelompok Riset
    st.subheader("Bar Chart Nama Universitas")
    st.plotly_chart(fig_bar1)

    
if __name__ == "__main__":
    main()



