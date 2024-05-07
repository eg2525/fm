import pandas as pd
import numpy as np
from tqdm import tqdm
import os

#消費税計算の処理
def tax_mapping(tax_data_path, output_dataframes):
    # tax_data.csvを読み込む
    tax_data = pd.read_csv(tax_data_path, encoding = 'cp932')

    # dataframes および output_dataframes のデータを更新
    for key, output_df in output_dataframes.items():
        # '借方勘定科目'を照合して、'借方税区分'を更新
        # output_df の '借方科目' と tax_data の '科目' を照合
        for idx, row in output_df.iterrows():
            subject = row['借方科目']
            tax_info = tax_data[tax_data['科目'] == subject]
            if not tax_info.empty:
                output_df.at[idx, '借方消費税コード'] = tax_info['借方税区分'].values[0]
                output_df.at[idx, '借方消費税税率'] = tax_info['借方税率'].values[0]
        # 更新されたDataFrameを保存
        output_dataframes[key] = output_df

        for idx, row in output_df.iterrows():
            subject = row['貸方科目']
            tax_info = tax_data[tax_data['科目'] == subject]
            if not tax_info.empty:
                output_df.at[idx, '貸方消費税コード'] = tax_info['貸方税区分'].values[0]
                output_df.at[idx, '貸方消費税税率'] = tax_info['貸方税率'].values[0]
        # 更新されたDataFrameを保存
        output_dataframes[key] = output_df    
        
    print("消費税転記が完了🎉")
    return output_dataframes


#仮払仮受消費税処理
def tax_adjustment(df_tax,output_dataframes):
    #df_tax = pd.read_csv(r'C:\Users\inagaki23\Desktop\FamilyMart\tax_info.csv', header=1, encoding='cp932')

    condition = df_tax['税・売上仕入種別'].isin(['１０％課税', '＊８％課税', '旧８％課税'])
    df_tax_provi = df_tax[condition]
    df_tax_provi = df_tax_provi.reset_index(drop=True)
    df_tax_provi = df_tax_provi.drop(columns=['会社コード', '会社名称', 'ディストリクトコード', 'ディストリクト名称', '営業所コード', '営業所名称',
                                             '指定年月','計上年月日','伝票No','税率','非課税/売上額（円）','非課税/仕入額（円）','免税/売上額（円）',
                                              '免税/仕入額（円）','不課税/売上額（円）','不課税/仕入額（円）',
    ])

    # 各outputデータフレームに4行追加
    for key, output_df in output_dataframes.items():
        additional_rows = pd.DataFrame(np.nan, index=range(4), columns=output_df.columns)
        output_df = pd.concat([output_df, additional_rows], ignore_index=True)
        output_dataframes[key] = output_df

    # df_tax_proviからのデータ転記
    for key, output_df in tqdm(output_dataframes.items(), desc="10%消費税データ転記中..."):
        store_name = key.replace('df_', '').replace('_output', '')
        # 一致する店舗のデータを抽出
        store_data = df_tax_provi[df_tax_provi['店舗名称'] == store_name]
        
        # '10％課税'の行を処理
        tax_10_data = store_data[store_data['税・売上仕入種別'] == '１０％課税']
        for idx, row in tax_10_data.iterrows():
            target_index = output_df['貸方金額'].isna().idxmax()  # 最初のNaN行を見つける
            
            if pd.notna(target_index):
                output_df.at[target_index, '貸方金額'] = row['課税/預り消費税（円）Ａ']
                output_df.at[target_index, '借方金額'] = row['課税/支払い消費税（円）Ｂ']
                output_df.at[target_index, '摘要'] = '10%消費税'
                output_df.at[target_index, '形式'] = 3
                output_df.at[target_index, '借方消費税コード'] = 31
                output_df.at[target_index, '貸方消費税コード'] = 1
                output_df.at[target_index, '借方消費税税率'] = 10
                output_df.at[target_index, '貸方消費税税率'] = 10
                output_df.at[target_index, '借方科目'] = 158
                output_df.at[target_index, '貸方科目'] = 215

    for key, output_df in tqdm(output_dataframes.items(), desc="8%(軽)消費税データ転記中..."):
        store_name = key.replace('df_', '').replace('_output', '')
        # 一致する店舗のデータを抽出
        store_data = df_tax_provi[df_tax_provi['店舗名称'] == store_name]
        
        # '10％課税'の行を処理
        tax_10_data = store_data[store_data['税・売上仕入種別'] == '＊８％課税']
        for idx, row in tax_10_data.iterrows():
            target_index = output_df['貸方金額'].isna().idxmax()  # 最初のNaN行を見つける
            
            if pd.notna(target_index):
                output_df.at[target_index, '貸方金額'] = row['課税/預り消費税（円）Ａ']
                output_df.at[target_index, '借方金額'] = row['課税/支払い消費税（円）Ｂ']
                output_df.at[target_index, '摘要'] = '８％(軽)課税'
                output_df.at[target_index, '形式'] = 3
                output_df.at[target_index, '借方消費税コード'] = 31
                output_df.at[target_index, '貸方消費税コード'] = 1
                output_df.at[target_index, '借方消費税税率'] = 'K8'
                output_df.at[target_index, '貸方消費税税率'] = 'K8'
                output_df.at[target_index, '借方科目'] = 158
                output_df.at[target_index, '貸方科目'] = 215     
                
    for key, output_df in tqdm(output_dataframes.items(), desc="8%消費税データ転記中..."):
        store_name = key.replace('df_', '').replace('_output', '')
        # 一致する店舗のデータを抽出
        store_data = df_tax_provi[df_tax_provi['店舗名称'] == store_name]
        
        # '10％課税'の行を処理
        tax_10_data = store_data[store_data['税・売上仕入種別'] == '旧８％課税']
        for idx, row in tax_10_data.iterrows():
            target_index = output_df['貸方金額'].isna().idxmax()  # 最初のNaN行を見つける
            
            if pd.notna(target_index):
                output_df.at[target_index, '貸方金額'] = row['課税/支払い消費税（円）Ｂ']
                output_df.at[target_index, '借方金額'] = row['課税/支払い消費税（円）Ｂ']
                output_df.at[target_index, '摘要'] = '旧8％消費税'
                output_df.at[target_index, '形式'] = 3
                output_df.at[target_index, '借方消費税コード'] = 31
                output_df.at[target_index, '借方消費税税率'] = 10
                output_df.at[target_index, '借方科目'] = 158
                output_df.at[target_index, '貸方科目'] = 999     
                
    print('消費税データ転記完了🌟')
    return output_dataframes