import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import streamlit as st
from io import BytesIO
import zipfile

def mapping_df(dataframes, output_dataframes):
	# 転記するインデックスとターゲットインデックスのマッピング
	index_map = {
	    1: 0, 2: 1, 5: 2, 6: 3, 11: 4, 15: 5, 16: 6, 17: 7, 18: 8, 19: 9, 
	    23: 10, 24: 11, 25: 12, 26: 13, 27: 14, 30: 15, 31: 16, 32: 17, 
	    33: 18, 34: 19, 35: 20, 36: 21, 37: 22, 38: 23, 39: 24, 40: 25, 41: 26
	}
	# 科目マッピング
	account_mapping = {
	    0: (999, 810), 1: (999, 811), 2: (466, 140), 3: (461, 999), 4: (140, 466),
	    5: (512, 999), 6: (812, 999), 7: (812, 999), 8: (812, 999), 9: (812, 999),
	    10: (501, 999), 11: (504, 999), 12: (505, 999), 13: (508, 999), 14: (514, 999),
	    15: (515, 999), 16: (523, 999), 17: (526, 999), 18: (520, 999), 19: (537, 999),
	    20: (531, 999), 21: (525, 999), 22: (539, 999), 23: (610, 999), 24: (614, 999),
	    25: (600, 999), 26: (604, 999)
	}

	# dataframes および output_dataframes のデータを転記
	for key, df in tqdm(dataframes.items(), desc='インポートデータ作成中...'):
	    output_key = f"{key}_output"
	    if output_key in output_dataframes:
	        output_df = output_dataframes[output_key]

	        # 必要に応じて追加の行をDataFrameに追加
	        additional_rows_needed = max(0, 50 - len(output_df))
	        if additional_rows_needed > 0:
	            additional_df = pd.DataFrame(columns=output_df.columns, index=range(additional_rows_needed), data=np.nan)
	            output_df = pd.concat([output_df, additional_df], ignore_index=True)

	        # データ転記処理
	        for source_index, target_index in index_map.items():
	            if '実   績' in df.columns and source_index < len(df):
	                actual_value = df.at[source_index, '実   績']
	                try:
	                    converted_value = int(abs(float(actual_value)))
	                except ValueError:
	                    converted_value = 0

	                if converted_value != 0:
	                    if pd.isna(output_df.at[target_index, '借方金額']):
	                        output_df.at[target_index, '借方金額'] = converted_value
	                        output_df.at[target_index, '貸方金額'] = converted_value

	                        debit, credit = account_mapping[target_index]
	                        if float(actual_value) < 0:
	                            debit, credit = credit, debit
	                        output_df.at[target_index, '借方科目'] = debit
	                        output_df.at[target_index, '貸方科目'] = credit

	                        store_name = key.replace('df_', '')
	                        output_df.at[target_index, '摘要'] = store_name
	                        output_df.at[target_index, '形式'] = 3
	        # NaN行の削除（データ転記後のクリーニング）
	        output_df.dropna(how='all', inplace=True)
	        output_dataframes[output_key] = output_df  # 更新されたDataFrameを再格納

	print('done🎉')
	return output_dataframes


def PL_mapping(dataframes_with, output_dataframes):
	# データ転記処理
	for key, withdraw_df in tqdm(dataframes_with.items(), desc="データ転記中..."):
	    output_key = f"{key}_output"
	    output_df = output_dataframes[output_key]  # 一致する出力DataFrameを取得

	    start_index = output_df.last_valid_index() + 1 if output_df.last_valid_index() is not None else 0

	    # 転記する内容を探索し、適切な位置に挿入
	    for idx, row in withdraw_df.iterrows():
	        target_index = start_index + idx
	        content = row['内容']
	        amount = row['金    額  (円)']

	        # データ挿入
	        output_df.at[target_index, '摘要'] = content
	        output_df.at[target_index, '借方金額'] = amount
	        output_df.at[target_index, '貸方金額'] = amount

	        # 借方科目と貸方科目に特定の値を設定
	        output_df.at[target_index, '借方科目'] = 133
	        output_df.at[target_index, '貸方科目'] = 999
	        output_df.at[target_index, '形式'] = 3

	    output_dataframes[output_key] = output_df  # 更新されたDataFrameを再格納

	print('データ転記および科目設定完了🌟')
	return output_dataframes

#調整
def adjustment_df(output_dataframes):
	for key, output_df in output_dataframes.items():
	    # 借方金額と貸方金額の列を数値型に変換（非数値はNaNになる）
	    output_df['借方金額'] = pd.to_numeric(output_df['借方金額'], errors='coerce')
	    output_df['貸方金額'] = pd.to_numeric(output_df['貸方金額'], errors='coerce')

	    # 新しい行を追加
	    new_row = pd.DataFrame(np.nan, index=[len(output_df)], columns=output_df.columns)
	    output_df = pd.concat([output_df, new_row], ignore_index=True)
	    
	    # '借方金額' と '貸方金額' の合計を計算
	    total_debit = output_df['借方金額'].sum(min_count=1)
	    total_credit = output_df['貸方金額'].sum(min_count=1)
	    
	    # 差額を計算
	    difference = total_debit - total_credit

	    # 最終行のインデックス
	    last_index = len(output_df) - 1

	    # 差額の調整
	    if difference < 0:
	        # '借方金額'が少ない場合
	        output_df.at[last_index, '形式'] = 3
	        output_df.at[last_index, '借方科目'] = 133
	        output_df.at[last_index, '借方金額'] = -difference  # 差額を正の値に
	        output_df.at[last_index, '摘要'] = "差額FM勘定"
	    elif difference > 0:
	        # '貸方金額'が少ない場合
	        output_df.at[last_index, '形式'] = 3
	        output_df.at[last_index, '貸方科目'] = 133
	        output_df.at[last_index, '貸方金額'] = difference
	        output_df.at[last_index, '摘要'] = "差額FM勘定"

	    # DataFrameを更新
	    output_dataframes[key] = output_df

	print('差額調整完了🌟')
	return output_dataframes

#最終調整
def dropping_df(output_dataframes):
	for key, output_df in output_dataframes.items():
	    # 条件①: 借方科目が133で、貸方科目が999で、借方金額と貸方金額がともにNaNの行を削除
	    condition1 = (output_df['借方科目'] == 133) & (output_df['貸方科目'] == 999) & \
	                 output_df['借方金額'].isna() & output_df['貸方金額'].isna()
	    output_df = output_df[~condition1]

	    # 条件②: 借方金額と貸方金額がともに0.0の行を削除
	    condition2 = (output_df['借方金額'] == 0.0) & (output_df['貸方金額'] == 0.0)
	    output_df = output_df[~condition2]

	    # 条件③: 借方金額と貸方金額が空白の行を削除（すでに実装されている場合はこのステップをスキップ）
	    condition3 = (output_df['借方金額'].astype(str).str.strip() == '') & (output_df['貸方金額'].astype(str).str.strip() == '')
	    output_df = output_df[~condition3]

	    # 条件④: 借方金額と貸方金額が NaN でないが空白になっているような行を削除
	    condition4 = (output_df['借方金額'].replace(0, np.nan).isna()) & (output_df['貸方金額'].replace(0, np.nan).isna())
	    output_df = output_df[~condition4]

	    # 更新されたDataFrameを再格納
	    output_dataframes[key] = output_df

	print('不要行削除完了🌟')
	return output_dataframes

# アウトプット
def output_to_csv(output_dataframes):
    # メモリストリームを用いたZIPファイルの作成
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for key, output_df in output_dataframes.items():
            # メモリ内でCSVファイルを作成
            csv_buffer = BytesIO()
            output_df.to_csv(csv_buffer, encoding='utf-8-sig', index=False, float_format='%.0f')
            csv_buffer.seek(0)
            zip_file.writestr(f"{key}.csv", csv_buffer.getvalue())

    # ZIPファイル用のダウンロードリンクをStreamlitで提供
    zip_buffer.seek(0)
    st.download_button(
        label="Download CSV Files as ZIP",
        data=zip_buffer,
        file_name="output_files.zip",
        mime="application/zip"
    )

    if st.button('Create and Download ZIP'):
        output_to_csv(output_dataframes)
