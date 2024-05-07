import pandas as pd
import numpy as np
import os
import streamlit as st

st.title("FM分割")

# ファイルアップロードウィジェットを表示し、ファイルをアップロード
uploaded_PLfiles = st.file_uploader("P/Lファイルを複数アップロードしてください", type=['xlsx'], accept_multiple_files=True)
uploaded_Withfiles = st.file_uploader("引出金ファイルを複数アップロードしてください", type=['xlsx'], accept_multiple_files=True)

# ファイルがアップロードされた後、'OK'ボタンが押されるのを待つ
if uploaded_PLfiles is not None and uploaded_Withfiles is not None:
    if st.checkbox('Start'):
        # アップロードされた各P/Lファイルを処理
        for uploaded_file in uploaded_PLfiles:
            # UploadedFileオブジェクトから直接DataFrameを読み込む
            df = pd.read_excel(uploaded_file, header=6)  # headerを適切に設定
            store_code = uploaded_file.name.split('.')[0]  # ファイル名から店舗コードを取得

            # 辞書にDataFrameを店舗コードとともに格納
            dataframes[f"df_{store_code}"] = df
        print('done🎉')