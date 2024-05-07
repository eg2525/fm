import os
import pandas as pd
from tqdm import tqdm

def PL_road(folder_path):
    # フォルダ内の全てのExcelファイルをループ処理
    excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    dataframes = {}
    for file_name in tqdm(excel_files, desc="ファイルデータの取得中..."):
        file_path = os.path.join(folder_path, file_name)
        
        try:
            df = pd.read_excel(file_path, usecols=[1], nrows=2)
            store_code = str(df.iloc[1, 0])
            
            # P/Lデータを含むDataFrameを読み込む
            df_pl = pd.read_excel(file_path, header=6)
            
            # 辞書にDataFrameを店舗コードとともに格納
            dataframes[f"df_{store_code}"] = df_pl
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")

    print('P/Lデータの読み取り完了。🎉')
    return dataframes

def initialize_output_dataframes(dataframes):
    columns_op =[
        "月種別","種類","形式","作成方法","付箋","伝票日付","伝票番号","伝票摘要","枝番","借方部門","借方部門名","借方科目","借方科目名","借方補助","借方補助科目名","借方金額","借方消費税コード","借方消費税業種","借方消費税税率",
        "借方資金区分","借方任意項目１","借方任意項目２","借方インボイス情報","貸方部門","貸方部門名","貸方科目","貸方科目名","貸方補助","貸方補助科目名","貸方金額","貸方消費税コード","貸方消費税業種","貸方消費税税率",
        "貸方資金区分","貸方任意項目１","貸方任意項目２","貸方インボイス情報","摘要","期日","証番号","入力マシン","入力ユーザ","入力アプリ","入力会社","入力日付"
    ] 
    # 新しいDataFrameを格納する辞書
    output_dataframes = {}

    # dataframes 辞書内の各店舗DataFrameに対して処理を実行
    for store_code, df in tqdm(dataframes.items(), desc="店舗データ処理中..."):
        new_df = pd.DataFrame(columns=columns_op, index=range(27), data=np.nan)
        
        # 新しいDataFrameを辞書に格納
        output_dataframes[f"{store_code}_output"] = new_df

    print('出力用のデータフレーム作成完了🎉')
    return output_dataframes

def mapping_preparing(dataframes_with , output_dataframes):
    for key, withdraw_df in tqdm(dataframes_with.items(), desc="データ転記前の準備中..."):
        output_key = f"{key}_output"
        if output_key in output_dataframes:
            output_df = output_dataframes[output_key]

            # NaN行のクリーニング
            output_df.dropna(how='all', inplace=True)

            # 転記するデータの数に基づいて行を追加
            needed_rows = len(withdraw_df)
            current_rows = len(output_df)
            additional_rows = needed_rows - (current_rows - output_df.last_valid_index() - 1)

            if additional_rows > 0:
                new_rows = pd.DataFrame(np.nan, index=range(additional_rows), columns=output_df.columns)
                output_df = pd.concat([output_df, new_rows], ignore_index=True)
            
            output_dataframes[output_key] = output_df  # 更新されたDataFrameを再格納

        print('行追加完了🌟')