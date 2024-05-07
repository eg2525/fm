import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import streamlit as st
from io import BytesIO
import zipfile


#引出金の処理
def withdraw_preparing(uploaded_files):
    dataframes_with = {}

    # アップロードされたファイルのリストをループ処理
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        # 店舗コードを含むセルのデータを読み取り
        store_withdraw_df = pd.read_excel(uploaded_file, usecols=[2], nrows=6)
        store_withdraw = str(store_withdraw_df.iloc[3, 0])  # 4行目のデータをstore_withdrawとして取得

        # 引出金データ全体を読み込む
        df_with = pd.read_excel(uploaded_file, header=6, nrows=15)  # ファイルからDataFrameを読み込む
        dataframes_with[f"df_{store_withdraw}"] = df_with

    st.write("引出金読み取り完了🎉")
    return dataframes_with

# 既存のdataframes_with辞書から各DataFrameを処理
def withdraw_mapping(dataframes_with):
	for store_withdraw, df_with in dataframes_with.items():
	    # '日'列から'金額 (円)'の前までの列を特定
	    if "日" in df_with.columns and "金    額  (円)" in df_with.columns:
	        start_col = df_with.columns.get_loc("日") + 1
	        end_col = df_with.columns.get_loc("金    額  (円)")
	        
	        # 指定された範囲の列を連結して新しい列「内容」を作成
	        df_with['内容'] = df_with.iloc[:, start_col:end_col].apply(
	            lambda row: ''.join(row.dropna().astype(str)), axis=1
	        )
	        
	        # 更新されたDataFrameを辞書に再格納
	        dataframes_with[store_withdraw] = df_with
	    else:
	        st.write(f"店舗コード {store_withdraw}: 必要な列が見つかりません。")

	st.write("引出金転記準備が完了🌸")
	return dataframes_with