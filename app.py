from shiny import App, reactive, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings

# matplotlibの警告を抑制
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# 日本語フォントの設定
try:
    import japanize_matplotlib
except ImportError:
    # japanize_matplotlibがない場合は手動でフォント設定
    # DejaVu Sansを除外し、日本語対応フォントのみを指定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'MS Gothic', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け対策

# 市町村データとコードのマッピング
municipalities_mapping = {
    "oosk": "大阪市", "ski": "堺市", "tynk": "豊中市", "suita": "吹田市", "tktk": "高槻市",
    "hrkt": "枚方市", "yo": "八尾市", "nygw": "寝屋川市", "hoska": "東大阪市", "kswd": "岸和田市",
    "ikd": "池田市", "izmot": "泉大津市", "kizk": "貝塚市", "mrgt": "守口市", "ibrk": "茨木市",
    "dit": "大東市", "izmi": "和泉市", "mno": "箕面市", "kswr": "柏原市", "hbkn": "羽曳野市",
    "kdma": "門真市", "stt": "摂津市", "tkis": "高石市", "fuji": "藤井寺市", "sennan": "泉南市",
    "sijo": "四條畷市", "kata": "交野市", "osksa": "大阪狭山市", "hannan": "阪南市", "izmsn": "泉佐野市",
    "tdbys": "富田林市", "kwtngn": "河内長野市", "mtbr": "松原市", "smam": "島本町", "tyn": "豊能町",
    "nose": "能勢町", "tdok": "忠岡町", "kuma": "熊取町", "tjr": "田尻町", "mski": "岬町",
    "tis": "太子町", "kanan": "河南町", "chyaksk": "千早赤阪村"
}

def load_csv_data(municipality_code, vote_type):
    """
    統合されたCSVファイルからデータを読み込む
    
    Parameters:
    -----------
    municipality_code : str
        市町村コード（例: "ski", "tis"）
    vote_type : str
        選挙種別（"a": 首長選挙, "b": 議員選挙）
    
    Returns:
    --------
    pandas.DataFrame or None
    """
    # app.pyの親ディレクトリ/data/merged_outputからファイルを読み込む
    base_dir = Path(__file__).parent
    csv_path = base_dir / "data" / "merged_output" / f"{municipality_code}_{vote_type}_merged.csv"
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ ファイル読み込み成功: {csv_path}")
        return df
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {csv_path}")
        return None
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return None

def process_dataframe(df):
    """
    データフレームを処理して必要な列を準備する
    CSVの列名を標準的な列名にマッピング
    """
    if df is None:
        return None
    
    # 列名のマッピング
    column_mapping = {
        '投票日': 'vote_date',
        '告示日': 'announcement_date',
        '投票率': 'turnout_rate',
        '定数/候補者数': 'seats_candidates',
        '有権者数': 'total_voters',
        '男性': 'male_voters',
        '女性': 'female_voters',
        '前回より': 'change_from_previous'
    }
    
    # 列名を変換
    df = df.rename(columns=column_mapping)
    
    # 投票日からyear列を作成
    if 'vote_date' in df.columns:
        try:
            df['vote_date'] = pd.to_datetime(df['vote_date'], errors='coerce')
            df['year'] = df['vote_date'].dt.year
        except:
            # 日付変換に失敗した場合、文字列から年を抽出
            try:
                df['year'] = df['vote_date'].astype(str).str.extract(r'(\d{4})')[0].astype(float)
            except:
                pass
    
    # 数値列の処理（パーセント記号やカンマを削除して数値に変換）
    numeric_columns = ['turnout_rate', 'total_voters', 'male_voters', 'female_voters']
    
    for col in numeric_columns:
        if col in df.columns:
            try:
                # %記号、カンマ、全角数字などを処理
                df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '').str.replace('，', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass
    
    # 定数/候補者数の処理
    if 'seats_candidates' in df.columns:
        try:
            # "20/25" のような形式を分割
            split_data = df['seats_candidates'].astype(str).str.split('/', expand=True)
            if len(split_data.columns) >= 2:
                df['fixed_seats'] = pd.to_numeric(split_data[0], errors='coerce')
                df['candidate_count'] = pd.to_numeric(split_data[1], errors='coerce')
                # 候補者比率を計算
                df['candidate_ratio'] = df['fixed_seats'] / df['candidate_count']
        except:
            pass
    
    return df

def generate_sample_data(start_year, end_year):
    """サンプルデータ生成（データが見つからない場合のフォールバック）"""
    years = list(range(start_year, end_year + 1))
    np.random.seed(42)
    
    data = {
        'year': years,
        'turnout_rate': [45 + np.random.normal(0, 5) for _ in years],
        'total_voters': [80000 + i * 2000 + np.random.normal(0, 3000) for i in range(len(years))],
        'male_voters': [38000 + i * 1000 + np.random.normal(0, 1500) for i in range(len(years))],
        'female_voters': [42000 + i * 1000 + np.random.normal(0, 1500) for i in range(len(years))],
        'candidate_count': [25 + np.random.randint(-3, 4) for _ in years],
        'fixed_seats': [20 + np.random.randint(-1, 2) for _ in years]
    }
    
    data['candidate_ratio'] = [data['fixed_seats'][i] / data['candidate_count'][i] for i in range(len(years))]
    
    for key in ['turnout_rate', 'total_voters', 'male_voters', 'female_voters']:
        if key == 'turnout_rate':
            data[key] = [max(0, min(100, val)) for val in data[key]]
        else:
            data[key] = [max(0, int(val)) for val in data[key]]
    
    data['candidate_count'] = [max(1, val) for val in data['candidate_count']]
    data['fixed_seats'] = [max(1, min(val, data['candidate_count'][i])) for i, val in enumerate(data['fixed_seats'])]
    
    return pd.DataFrame(data)

# UIの定義
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("表示設定"),
        ui.input_selectize(
            "selention_pre",
            "市町村を選択",
            municipalities_mapping
        ),
        ui.input_select(
            "vote_type",
            "選挙の種類",
            {"a": "首長選挙", "b": "議員選挙"}
        ),
        ui.input_slider(
            "year_range",
            "表示年度範囲:",
            min=1990,
            max=2030,
            value=[2000, 2025],
            step=1,
            sep=""
        ),
        ui.br(),
        ui.input_checkbox_group(
            "selected_metrics",
            "表示する統計項目を選択してください:",
            choices={
                "turnout_rate": "投票率 (%)",
                "total_voters": "有権者数（合計）",
                "male_voters": "有権者数（男性）",
                "female_voters": "有権者数（女性）",
                "candidate_ratio": "定数/候補者数比率"
            },
            selected=["turnout_rate"]
        ),
        ui.br(),
        ui.p("※ 複数項目を選択すると、同じグラフ内に重ねて表示されます。"),
        ui.p("※ 定数/候補者数比率は棒グラフで表示されます（水色：候補者数、グレー：定数）。")
    ),
    ui.card(
        ui.card_header("統計データ推移グラフ"),
        ui.output_text("data_status"),
        ui.br(),
        ui.output_plot("statistics_plot")
    )
)

def server(input, output, session):
    
    @reactive.calc
    def load_data():
        """選択された市町村・選挙種別のデータを読み込む"""
        municipality_code = input.selention_pre()
        vote_type = input.vote_type()
        
        # 実データを読み込み試行
        df = load_csv_data(municipality_code, vote_type)
        
        if df is not None:
            df = process_dataframe(df)
            return df, True  # 実データ
        else:
            # サンプルデータを生成
            year_range = input.year_range()
            return generate_sample_data(year_range[0], year_range[1]), False  # サンプルデータ
    
    @reactive.calc
    def filtered_data():
        """年度範囲でフィルタリング"""
        df, is_real = load_data()
        year_range = input.year_range()
        
        if df is not None and 'year' in df.columns:
            df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
        
        return df, is_real
    
    @render.text
    def data_status():
        """データの読み込み状況を表示"""
        _, is_real = filtered_data()
        municipality_code = input.selention_pre()
        municipality_name = municipalities_mapping.get(municipality_code, municipality_code)
        vote_type = input.vote_type()
        vote_type_name = "首長選挙" if vote_type == "a" else "議員選挙"
        
        if is_real:
            return f"✅ {municipality_name} - {vote_type_name}の実データを表示中"
        else:
            return f"⚠️ {municipality_name} - {vote_type_name}のデータが見つかりません。サンプルデータを表示中"
    
    @render.plot
    def statistics_plot():
        selected_metrics = input.selected_metrics()
        data, is_real = filtered_data()
        
        if data is None or len(data) == 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'データがありません', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16, color='red')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        if not selected_metrics:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, '表示項目を選択してください', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        # メトリクス名とラベルのマッピング
        metric_labels = {
            "turnout_rate": "投票率 (%)",
            "total_voters": "有権者数（合計）",
            "male_voters": "有権者数（男性）",
            "female_voters": "有権者数（女性）",
            "candidate_ratio": "定数/候補者数比率"
        }
        
        colors = ['#2563eb', '#dc2626', '#059669', '#7c3aed', '#ea580c']
        markers = ['o', 's', '^', 'D', 'v']
        
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # 左軸用の項目（投票率のみ）
        left_axis_metrics = [m for m in selected_metrics if m in ['turnout_rate']]
        
        # 右軸用の項目（有権者数、定数/候補者数比率）
        right_axis_metrics = [m for m in selected_metrics if m in ['total_voters', 'male_voters', 'female_voters', 'candidate_ratio']]
        
        # 左軸にプロット（投票率）
        lines1 = []
        labels1 = []
        
        for i, metric in enumerate(left_axis_metrics):
            if metric in data.columns:
                line = ax1.plot(data['year'], data[metric], 
                               marker=markers[i % len(markers)], linewidth=2.5, markersize=7,
                               color=colors[i % len(colors)], label=metric_labels[metric])
                lines1.extend(line)
                labels1.append(metric_labels[metric])
        
        # 左軸の設定
        if left_axis_metrics:
            ax1.set_xlabel('年', fontsize=12)
            ax1.set_ylabel('投票率 (%)', fontsize=12, color=colors[0])
            ax1.set_ylim(20, 80)  # 投票率の縦軸を20-80%に固定
            ax1.tick_params(axis='y', labelcolor=colors[0])
        else:
            # 投票率がない場合でも軸のラベルは設定
            ax1.set_xlabel('年', fontsize=12)
        
        # 右軸の設定
        lines2 = []
        labels2 = []
        if right_axis_metrics:
            ax2 = ax1.twinx()
            
            bar_width = 0.6
            has_bar_chart = False
            
            for i, metric in enumerate(right_axis_metrics):
                if metric == 'candidate_ratio':
                    if 'candidate_count' in data.columns and 'fixed_seats' in data.columns:
                        # 棒グラフで表示
                        bars1 = ax2.bar(data['year'], data['candidate_count'], 
                                      width=bar_width, alpha=0.6, color='#87ceeb', label='候補者数')
                        bars2 = ax2.bar(data['year'], data['fixed_seats'], 
                                      width=bar_width, alpha=0.8, color='#808080', label='定数')
                        lines2.extend([bars1, bars2])
                        labels2.extend(['候補者数', '定数'])
                        has_bar_chart = True
                elif metric in data.columns:
                    # 線グラフで表示
                    color_idx = len(left_axis_metrics) + i
                    line = ax2.plot(data['year'], data[metric], 
                                   marker=markers[color_idx % len(markers)], linewidth=2.5, markersize=7,
                                   color=colors[color_idx % len(colors)], label=metric_labels[metric])
                    lines2.extend(line)
                    labels2.append(metric_labels[metric])
            
            # 右軸のラベル設定
            if has_bar_chart and len(right_axis_metrics) == 1:
                ax2.set_ylabel('人数', fontsize=12, color='#808080')
            else:
                ax2.set_ylabel('有権者数 (人)', fontsize=12, color=colors[len(left_axis_metrics)])
            
            ax2.tick_params(axis='y')
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        # タイトル設定
        year_range = input.year_range()
        municipality_code = input.selention_pre()
        municipality_name = municipalities_mapping.get(municipality_code, municipality_code)
        vote_type = input.vote_type()
        vote_type_name = "首長選挙" if vote_type == "a" else "議員選挙"
        
        title = f"{municipality_name} - {vote_type_name} 統計項目の推移 ({year_range[0]}年 - {year_range[1]}年)"
        if not is_real:
            title += " [サンプルデータ]"
        ax1.set_title(title, fontsize=14, fontweight='bold', pad=30)
        
        # 凡例の位置を調整
        all_lines = lines1 + lines2
        all_labels = labels1 + labels2
        if all_lines:
            ax1.legend(all_lines, all_labels, loc='upper left', bbox_to_anchor=(0.02, 0.95))
        
        # グリッド
        ax1.grid(True, alpha=0.3)
        
        # X軸の年表示を調整（year_rangeで固定）
        year_range_values = input.year_range()
        ax1.set_xlim(year_range_values[0] - 0.5, year_range_values[1] + 0.5)
        
        # レイアウトの調整
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.85)
        
        return fig

app = App(app_ui, server)