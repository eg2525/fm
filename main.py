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
from PL_process import mapping_df, PL_mapping, adjustment_df, dropping_df, output_to_csv

uploaded_files = st.file_uploader("P/Lファイルを複数アップロードしてください", type=['xlsx'], accept_multiple_files=True)
uploaded_Withfiles = st.file_uploader("引出金ファイルを複数アップロードしてください", type=['xlsx'], accept_multiple_files=True)

# ファイルがアップロードされた後、'OK'ボタンが押されるのを待つ
if uploaded_files is not None and uploaded_Withfiles is not None:
	if st.checkbox('start'):
		dataframes = PL_road(uploaded_files)

		output_dataframes = initialize_output_dataframes(dataframes)

		# 特定のExcelファイル名を指定
		file_name_to_view = "エバーグリーン　PL2402-02"

		# ファイル名に "_output" を追加してキーを形成
		key_to_view = f"{file_name_to_view}_output"

		# Streamlitアプリケーションで指定ファイルのデータフレームを表示
		if key_to_view in output_dataframes:
		    st.write(f"データフレーム ({file_name_to_view}):")
		    st.dataframe(output_dataframes[key_to_view])
		else:
		    st.error(f"データフレーム '{file_name_to_view}' が見つかりません。")