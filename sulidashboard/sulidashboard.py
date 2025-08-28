import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
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

st.set_page_config(layout='wide')
st.title('Dashboard Distributor Suli 5 Tangerang Selatan')
st_autorefresh(interval=5*1000)

@st.cache_data
def get_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_serviece_account"],
        scopes = scope
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open("Transaksi Masuk")
    sheet = spreadsheet.get_worksheet(0)
    data = sheet. get_all_values()