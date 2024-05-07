import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import streamlit as st
from io import BytesIO
import zipfile


#引出金の処理
def withdraw_preparing(withdraw_path):
	#folder_path = r'C:\Users\inagaki23\Desktop\FamilyMart\Fm_Withdrawals'
	# 辞書を用いて店舗番号に基づいたDataFrameを格納
	dataframes_with = {}

	# フォルダ内の全てのExcelファイルをループ処理
	excel_files_with = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
	for file_name in tqdm(excel_files_with, desc="引出金データ取得中"):
	    file_path = os.path.join(folder_path, file_name)
	    
	    df = pd.read_excel(file_path, usecols=[2], nrows=6)
	    store_withdraw = str(df.iloc[3, 0])
	    
	    # 引出金データを含むDataFrameを読み込む
	    df_with = pd.read_excel(file_path, header=6, nrows=15)
	    
	    # 辞書にDataFrameを店舗コードとともに格納
	    dataframes_with[f"df_{store_withdraw}"] = df_with
	    
	st.write("引出金読み取り完了🎉")
	return dataframes_with

# 既存のdataframes_with辞書から各DataFrameを処理
def withdraw_mapping(dataframes_with):
	for store_withdraw, df_with in tqdm(dataframes_with.items(), desc= '引出金データ作成中'):
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
	        print(f"店舗コード {store_withdraw}: 必要な列が見つかりません。")

	print("処理完了🌸")
	return dataframes_with