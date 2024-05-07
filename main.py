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

		output_dataframes = mapping_df(dataframes, output_dataframes)

		
		# ドロップダウンメニューからデータフレームを選択
		file_name_to_view = st.selectbox("データフレームを選択してください", list(output_dataframes.keys()))

		# 選択されたデータフレームを表示
		if file_name_to_view:
		    st.dataframe(output_dataframes[file_name_to_view])
