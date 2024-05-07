import pandas as pd
import numpy as np
import os
import streamlit as st

st.title("FM分割")

# ファイルアップロードウィジェットを表示し、ファイルをアップロード
uploaded_PLfile = st.file_uploader("P/Lファイルをアップロードしてください", type=['xlsx'])
uploaded_Withfile = st.file_uploader("引出金ファイルをアップロードしてください", type=['xlsx'])


# ファイルがアップロードされた後、'OK'ボタンが押されるのを待つ
if uploaded_PLfile is not None and uploaded_Withfile is not None:
    if st.checkbox('Start'):
        # フォルダ内の全てのExcelファイルをループ処理
        excel_files = [f for f in os.listdir(uploaded_PLfile) if f.endswith('.xlsx')]
        for file_name in tqdm(excel_files, desc="ファイルデータの取得中..."):
            file_path = os.path.join(uploaded_PLfile, file_name)
            
            df = pd.read_excel(file_path, usecols=[1], nrows=2)
            store_code = str(df.iloc[1, 0])
            
            # P/Lデータを含むDataFrameを読み込む
            df_pl = pd.read_excel(file_path, header=6)
            
            # 辞書にDataFrameを店舗コードとともに格納
            dataframes[f"df_{store_code}"] = df_pl
        print('done🎉')