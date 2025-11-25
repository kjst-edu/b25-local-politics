import requests
from pathlib import Path
from io import StringIO
import pandas as pd

def get_data(url, name):
    # utf-8でHTMLを取得
    response = requests.get(url)
    response.encoding = 'utf-8'

    # pandasでテーブルを読み込みリストに格納
    tables = pd.read_html(StringIO(response.text))

    # テーブルリストからデータフレームを取得
    df = tables[0]
    # csvファイルに出力
    df.to_csv(Path(__file__).parent / f"data/{name}", index=False)


    return df