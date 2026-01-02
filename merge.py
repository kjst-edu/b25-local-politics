import os
import pandas as pd
from pathlib import Path
import re
from datetime import datetime

def convert_japanese_date(date_str):
    """
    日本語形式の日付を標準形式（YYYY-MM-DD）に変換
    
    対応形式例:
    - "2025年1月2日" → "2025-01-02"
    - "2025/1/2" → "2025-01-02"
    - "2025-1-2" → "2025-01-02"
    - "2025年1月" → "2025-01-01" (日が無い場合は1日とする)
    """
    if pd.isna(date_str) or date_str == "":
        return None
    
    date_str = str(date_str).strip()
    
    # 西暦形式: "2025年1月2日"
    year_pattern = r'(\d{4})年(\d+)月(?:(\d+)日)?'
    match = re.match(year_pattern, date_str)
    if match:
        year, month, day = match.groups()
        year = int(year)
        month = int(month)
        day = int(day) if day else 1
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    # スラッシュ形式: "2025/1/2"
    slash_pattern = r'(\d{4})/(\d+)/(\d+)'
    match = re.match(slash_pattern, date_str)
    if match:
        year, month, day = match.groups()
        year = int(year)
        month = int(month)
        day = int(day)
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    # ハイフン形式: "2025-1-2" → "2025-01-02"
    hyphen_pattern = r'(\d{4})-(\d+)-(\d+)'
    match = re.match(hyphen_pattern, date_str)
    if match:
        year, month, day = match.groups()
        year = int(year)
        month = int(month)
        day = int(day)
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    # 変換できない場合は元の値を返す
    return date_str

def detect_date_columns(df):
    """
    データフレーム内の日付列を自動検出
    """
    date_columns = []
    
    for col in df.columns:
        # カラム名に「日付」「年月日」などが含まれる場合
        if any(keyword in str(col) for keyword in ['日付', '年月日', '日時', 'date', 'Date', 'DATE']):
            date_columns.append(col)
            continue
        
        # サンプル値を確認して日付形式かチェック
        sample = df[col].dropna().head(10)
        if len(sample) > 0:
            # 日本語の日付パターンが含まれるかチェック
            date_pattern = r'(\d{4}年|\d{4}/|\d{4}-)'
            if sample.astype(str).str.contains(date_pattern).any():
                date_columns.append(col)
    
    return date_columns

def merge_csv_files(directory_path, convert_dates=True, date_columns=None):
    """
    指定ディレクトリ内のCSVファイルを条件に従って統合する
    
    Parameters:
    -----------
    directory_path : str
        CSVファイルが格納されているディレクトリのパス
    convert_dates : bool
        日付変換を行うかどうか（デフォルト: True）
    date_columns : list or None
        変換対象の日付列名のリスト（Noneの場合は自動検出）
    """
    
    # ディレクトリ内のすべてのCSVファイルを取得
    csv_files = list(Path(directory_path).glob("*_cleaned.csv"))
    
    # ファイル情報を解析して辞書に格納
    file_info = []
    pattern = r"^(.+?)(\d{4})([a-z])_cleaned\.csv$"
    
    for file_path in csv_files:
        match = re.match(pattern, file_path.name)
        if match:
            city_code = match.group(1)  # 市町村名の略称
            year = int(match.group(2))   # 年号
            data_type = match.group(3)   # データ区別符号
            
            file_info.append({
                'path': file_path,
                'city_code': city_code,
                'year': year,
                'data_type': data_type,
                'filename': file_path.name
            })
    
    # city_code と data_type でグループ化
    groups = {}
    for info in file_info:
        key = (info['city_code'], info['data_type'])
        if key not in groups:
            groups[key] = []
        groups[key].append(info)
    
    # 各グループを年号順にソートして統合
    output_dir = Path(directory_path) / "merged_output"
    output_dir.mkdir(exist_ok=True)
    
    for (city_code, data_type), files in groups.items():
        # 年号順にソート
        files_sorted = sorted(files, key=lambda x: x['year'])
        
        # DataFrameを順番に結合
        dfs = []
        for file_info in files_sorted:
            df = pd.read_csv(file_info['path'])
            dfs.append(df)
            print(f"読み込み: {file_info['filename']} ({len(df)} 行)")
        
        # 縦に結合
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # 日付変換処理
        if convert_dates:
            # 日付列を自動検出または指定されたものを使用
            if date_columns is None:
                detected_columns = detect_date_columns(merged_df)
            else:
                detected_columns = [col for col in date_columns if col in merged_df.columns]
            
            if detected_columns:
                print(f"  日付変換対象列: {detected_columns}")
                
                for col in detected_columns:
                    print(f"  変換中: {col}")
                    merged_df[col] = merged_df[col].apply(convert_japanese_date)
                    
                    # datetime型に変換（エラーは無視）
                    try:
                        merged_df[col] = pd.to_datetime(merged_df[col], errors='coerce')
                    except:
                        pass
        
        # 出力ファイル名を生成
        output_filename = f"{city_code}_{data_type}_merged.csv"
        output_path = output_dir / output_filename
        
        # CSV出力
        merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✓ 統合完了: {output_filename} (合計 {len(merged_df)} 行)")
        print(f"  - 統合ファイル数: {len(files_sorted)}")
        print(f"  - 年号範囲: {files_sorted[0]['year']} - {files_sorted[-1]['year']}")
        print()

# 使用例
if __name__ == "__main__":
    # 処理対象のディレクトリパスを指定
    target_directory = Path(__file__).parent / "data"  # ここを実際のパスに変更してください
    
    # 日付列を自動検出して変換
    merge_csv_files(target_directory, convert_dates=True)
    
    print("すべての処理が完了しました！")