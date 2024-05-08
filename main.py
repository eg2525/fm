import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import streamlit as st
from io import BytesIO
import zipfile
from PL import PL_road, initialize_output_dataframes, mapping_preparing
from withdraw import withdraw_preparing, withdraw_mapping
from tax import tax_mapping, tax_adjustment
from PL_process import mapping_df, PL_mapping, adjustment_df, dropping_df

st.title('FM自動仕訳生成')

st.markdown('''
    ### 手順
    1. P/Lデータを分割→Acrobatでexcel化→アップロード
    2. 引出金データを分割→Acrobatでexcel化→アップロード
    3. 消費税データcsvをアップロード
	''')

uploaded_files = st.file_uploader("P/Lファイルを全てアップロードしてください", type=['xlsx'], accept_multiple_files=True)
withdraw_path = st.file_uploader("引出金ファイルを全てアップロードしてください", type=['xlsx'], accept_multiple_files=True)
tax_data_path = 'tax_data_R4.csv'
df_tax_info = st.file_uploader("消費税データをアップロードしてください", type=['csv'])

# ファイルがアップロードされた後、'OK'ボタンが押されるのを待つ

if uploaded_files and withdraw_path and df_tax_info:
    if st.button('Start and Download ZIP'):
        dataframes = PL_road(uploaded_files)
        output_dataframes = initialize_output_dataframes(dataframes)
        output_dataframes = mapping_df(dataframes, output_dataframes)
        output_dataframes = tax_mapping('tax_data_R4.csv', output_dataframes)
        dataframes_with = withdraw_preparing(withdraw_path)
        dataframes_with = withdraw_mapping(dataframes_with)
        output_dataframes = mapping_preparing(dataframes_with, output_dataframes)
        output_dataframes = PL_mapping(dataframes_with, output_dataframes)
        output_dataframes = tax_adjustment(df_tax_info, output_dataframes)
        output_dataframes = adjustment_df(output_dataframes)
        output_dataframes = dropping_df(output_dataframes)

        # メモリストリームを用いたZIPファイルの作成
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for key, output_df in output_dataframes.items():
                csv_buffer = BytesIO()
                output_df.to_csv(csv_buffer, encoding='cp932', index=False, float_format='%.0f')
                csv_buffer.seek(0)
                zip_file.writestr(f"{key}.csv", csv_buffer.getvalue())
        zip_buffer.seek(0)
        st.download_button(
            label="Download CSV Files as ZIP",
            data=zip_buffer,
            file_name="output_files.zip",
            mime="application/zip"
        )   

_ = '''
# ドロップダウンメニューからデータフレームを選択
file_name_to_view = st.selectbox("データフレームを選択してください", list(output_dataframes.keys()))

# 選択されたデータフレームを表示
if file_name_to_view:
    st.dataframe(output_dataframes[file_name_to_view])
'''