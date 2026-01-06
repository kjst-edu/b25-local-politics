import seaborn as sns

# Import data from shared.py
#from shared import df

from shiny import App, render, ui

#頭文字検索参考例
from shiny import App, reactive, render, ui
import pandas as pd

from shiny import App, reactive, render, ui
import pandas as pd

# 大阪府の市町村データ,ここに市町村ごとのデータをどうにか結びつける必要あり
#結びつけるうえ、それがどの項目に当てはまるのかの分類も加える必要がある
municipalities_data = [
   #区
    {"name": "都島区", "reading": "みやこじまく", "type": "区", "parent": "大阪市"},
    {"name": "福島区", "reading": "ふくしまく", "type": "区", "parent": "大阪市"},
    {"name": "此花区", "reading": "このはなく", "type": "区", "parent": "大阪市"},
    {"name": "西区", "reading": "にしく", "type": "区", "parent": "大阪市"},
    {"name": "港区", "reading": "みなとく", "type": "区", "parent": "大阪市"},
    {"name": "大正区", "reading": "たいしょうく", "type": "区", "parent": "大阪市"},
    {"name": "天王寺区", "reading": "てんのうじく", "type": "区", "parent": "大阪市"},
    {"name": "浪速区", "reading": "なにわく", "type": "区", "parent": "大阪市"},
    {"name": "西淀川区", "reading": "にしよどがわく", "type": "区", "parent": "大阪市"},
    {"name": "東淀川区", "reading": "ひがしよどがわく", "type": "区", "parent": "大阪市"},
    {"name": "東成区", "reading": "ひがしなりく", "type": "区", "parent": "大阪市"},
    {"name": "生野区", "reading": "いくのく", "type": "区", "parent": "大阪市"},
    {"name": "旭区", "reading": "あさひく", "type": "区", "parent": "大阪市"},
    {"name": "城東区", "reading": "じょうとうく", "type": "区", "parent": "大阪市"},
    {"name": "阿倍野区", "reading": "あべのく", "type": "区", "parent": "大阪市"},
    {"name": "住吉区", "reading": "すみよしく", "type": "区", "parent": "大阪市"},
    {"name": "東住吉区", "reading": "ひがしすみよしく", "type": "区", "parent": "大阪市"},
    {"name": "西成区", "reading": "にしなりく", "type": "区", "parent": "大阪市"},
    {"name": "淀川区", "reading": "よどがわく", "type": "区", "parent": "大阪市"},
    {"name": "鶴見区", "reading": "つるみく", "type": "区", "parent": "大阪市"},
    {"name": "住之江区", "reading": "すみのえく", "type": "区", "parent": "大阪市"},
    {"name": "平野区", "reading": "ひらのく", "type": "区", "parent": "大阪市"},
    {"name": "北区", "reading": "きたく", "type": "区", "parent": "大阪市"},
    {"name": "中央区", "reading": "ちゅうおうく", "type": "区", "parent": "大阪市"},
    

    # 市
    {"name": "大阪市", "reading": "おおさかし", "type": "市"},
    {"name": "堺市", "reading": "さかいし", "type": "市"},
    {"name": "豊中市", "reading": "とよなかし", "type": "市"},
    {"name": "吹田市", "reading": "すいたし", "type": "市"},
    {"name": "高槻市", "reading": "たかつきし", "type": "市"},
    {"name": "枚方市", "reading": "ひらかたし", "type": "市"},
    {"name": "八尾市", "reading": "やおし", "type": "市"},
    {"name": "寝屋川市", "reading": "ねやがわし", "type": "市"},
    {"name": "東大阪市", "reading": "ひがしおおさかし", "type": "市"},
    {"name": "岸和田市", "reading": "きしわだし", "type": "市"},
    {"name": "池田市", "reading": "いけだし", "type": "市"},
    {"name": "泉大津市", "reading": "いずみおおつし", "type": "市"},
    {"name": "貝塚市", "reading": "かいづかし", "type": "市"},
    {"name": "守口市", "reading": "もりぐちし", "type": "市"},
    {"name": "茨木市", "reading": "いばらきし", "type": "市"},
    {"name": "大東市", "reading": "だいとうし", "type": "市"},
    {"name": "和泉市", "reading": "いずみし", "type": "市"},
    {"name": "箕面市", "reading": "みのおし", "type": "市"},
    {"name": "柏原市", "reading": "かしわらし", "type": "市"},
    {"name": "羽曳野市", "reading": "はびきのし", "type": "市"},
    {"name": "門真市", "reading": "かどまし", "type": "市"},
    {"name": "摂津市", "reading": "せっつし", "type": "市"},
    {"name": "高石市", "reading": "たかいしし", "type": "市"},
    {"name": "藤井寺市", "reading": "ふじいでらし", "type": "市"},
    {"name": "泉南市", "reading": "せんなんし", "type": "市"},
    {"name": "四條畷市", "reading": "しじょうなわてし", "type": "市"},
    {"name": "交野市", "reading": "かたのし", "type": "市"},
    {"name": "大阪狭山市", "reading": "おおさかさやまし", "type": "市"},
    {"name": "阪南市", "reading": "はんなんし", "type": "市"},
    {"name": "泉佐野市", "reading": "いずみさのし", "type": "市"},
    {"name": "富田林市", "reading": "とんだばやしし", "type": "市"},
    {"name": "河内長野市", "reading": "かわちながのし", "type": "市"},
    {"name": "松原市", "reading": "まつばらし", "type": "市"},
    
    # 町村
    {"name": "島本町", "reading": "しまもとちょう", "type": "町"},
    {"name": "豊能町", "reading": "とよのちょう", "type": "町"},
    {"name": "能勢町", "reading": "のせちょう", "type": "町"},
    {"name": "忠岡町", "reading": "ただおかちょう", "type": "町"},
    {"name": "熊取町", "reading": "くまとりちょう", "type": "町"},
    {"name": "田尻町", "reading": "たじりちょう", "type": "町"},
    {"name": "岬町", "reading": "みさきちょう", "type": "町"},
    {"name": "太子町", "reading": "たいしちょう", "type": "町"},
    {"name": "河南町", "reading": "かなんちょう", "type": "町"},
    {"name": "千早赤阪村", "reading": "ちはやあかさかむら", "type": "村"},
]

municipalities_df = pd.DataFrame(municipalities_data)

#今のところこの上下の機能は連結していません。
#表示項目
from shiny import App, reactive, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 一時的にsampleデータが入ってます
def generate_sample_data(start_year, end_year):
    """指定された年度範囲でサンプル統計データを生成"""
    years = list(range(start_year, end_year + 1))
    np.random.seed(42)  # 再現可能な結果のため
    
    data = {
        'year': years,
        'turnout_rate': [45 + np.random.normal(0, 5) for _ in years],
        'total_voters': [80000 + i * 2000 + np.random.normal(0, 3000) for i in range(len(years))],
        'male_voters': [38000 + i * 1000 + np.random.normal(0, 1500) for i in range(len(years))],
        'female_voters': [42000 + i * 1000 + np.random.normal(0, 1500) for i in range(len(years))]
    }
    
    # 候補者数と定数のデータを生成
    data['candidate_count'] = [25 + np.random.randint(-3, 4) for _ in years]  # 候補者数
    data['fixed_seats'] = [20 + np.random.randint(-1, 2) for _ in years]  # 定数（候補者数より少ない）
    
    # 定数比候補者数の計算（定数/候補者数）
    data['candidate_ratio'] = [data['fixed_seats'][i] / data['candidate_count'][i] for i in range(len(years))]
    
    # 負の値を防ぐ
    for key in ['turnout_rate', 'total_voters', 'male_voters', 'female_voters']:
        if key == 'turnout_rate':
            data[key] = [max(0, min(100, val)) for val in data[key]]  # 0-100%の範囲
        else:
            data[key] = [max(0, int(val)) for val in data[key]]  # 負の値を防ぐ
    
    # 候補者数と定数も負の値を防ぐ
    data['candidate_count'] = [max(1, val) for val in data['candidate_count']]
    data['fixed_seats'] = [max(1, min(val, data['candidate_count'][i])) for i, val in enumerate(data['fixed_seats'])]
    
    return pd.DataFrame(data)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("表示設定"),
        ui.input_selectize(
            "selention_area",
            "市町村を選択",
            ["大阪市", "堺市",  "豊中市", "吹田市",  "高槻市",  "枚方市", "八尾市",  "寝屋川市", "東大阪市",  "岸和田市", "池田市",  "泉大津市",  "貝塚市",  "守口市",  "茨木市",  "大東市", "和泉市",  "箕面市",  "柏原市",  "羽曳野市",  "門真市",  "摂津市",  "高石市",  "藤井寺市",  "泉南市",  "四條畷市",  "交野市",  "大阪狭山市", "阪南市",  "泉佐野市",  "富田林市",  "河内長野市",  "松原市",  "島本町",  "豊能町",  "能勢町",  "忠岡町",  "熊取町",  "田尻町", "岬町",  "太子町", "河南町", "千早赤阪村"]
            ),
        ui.input_slider(
            "year_range",
            "表示年度範囲:",
            min=2000,
            max=2020,
            value=[2010, 2020],
            step=1,
            sep=""
        ),
        ui.br(),
        ui.input_checkbox_group(
            "selected_metrics",
            "表示する統計項目を選択してください:",
            choices={
                "turnout_rate": "投票率 (%)",
                "total_voters": "有権者数 (人)",
                "candidate_ratio": "定数比候補者数",
                "male_voters": "有権者数（男性）",
                "female_voters": "有権者数（女性）"
            },
            selected=["turnout_rate"]
        ),
        ui.br(),
        ui.p("※ 複数項目を選択すると、同じグラフ内に重ねて表示されます。"),
        ui.p("※ 定数比候補者数は棒グラフで表示されます（水色：候補者数、グレー：定数）。"),
        ui.p("※ データはサンプルデータです。")
    ),
    ui.card(
        ui.card_header("統計データ推移グラフ"),
        ui.output_plot("statistics_plot")
    )
)

def server(input, output, session):
    
    @reactive.calc
    def filtered_data():
        """選択された年度範囲に基づいてデータを生成・フィルタリング"""
        year_range = input.year_range()
        start_year, end_year = year_range[0], year_range[1]
        return generate_sample_data(start_year, end_year)
    
    @render.plot
    def statistics_plot():
        selected_metrics = input.selected_metrics()
        data = filtered_data()
        
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
            "total_voters": "有権者数 (人)",
            "candidate_ratio": "定数比候補者数",
            "male_voters": "有権者数（男性）",
            "female_voters": "有権者数（女性）"
        }
        
        colors = ['#2563eb', '#dc2626', '#059669', '#7c3aed', '#ea580c']
        markers = ['o', 's', '^', 'D', 'v']
        
        # フィギュアサイズを調整し、上部マージンを確保
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # 左軸用の項目（投票率、候補者比率）
        left_axis_metrics = [m for m in selected_metrics if m in ['turnout_rate', 'candidate_ratio']]
        
        # 右軸用の項目（有権者数関連）
        right_axis_metrics = [m for m in selected_metrics if m in ['total_voters', 'male_voters', 'female_voters']]
        
        # 左軸にプロット
        lines1 = []
        labels1 = []
        bar_width = 0.6  # 棒グラフの幅
        
        for i, metric in enumerate(left_axis_metrics):
            if metric == 'candidate_ratio':
                # 候補者数を水色で表示（背景）
                bars1 = ax1.bar(data['year'], data['candidate_count'], 
                              width=bar_width,
                              alpha=0.6,
                              color='#87ceeb',  # 水色
                              label='候補者数')
                
                # 定数をグレーで表示（前景、重ね合わせ）
                bars2 = ax1.bar(data['year'], data['fixed_seats'], 
                              width=bar_width,
                              alpha=0.8,
                              color='#808080',  # グレー
                              label='定数')
                
                lines1.extend([bars1, bars2])
                labels1.extend(['候補者数', '定数'])
            else:
                # その他は線グラフで表示
                line = ax1.plot(data['year'], data[metric], 
                               marker=markers[i % len(markers)], 
                               linewidth=2.5, 
                               markersize=7,
                               color=colors[i % len(colors)], 
                               label=metric_labels[metric])
                lines1.extend(line)
                labels1.append(metric_labels[metric])
        
        # 左軸の設定
        if left_axis_metrics:
            ax1.set_xlabel('年', fontsize=12)
            if 'turnout_rate' in left_axis_metrics and 'candidate_ratio' in left_axis_metrics:
                ax1.set_ylabel('投票率 (%) / 人数', fontsize=12, color=colors[0])
            elif 'turnout_rate' in left_axis_metrics:
                ax1.set_ylabel('投票率 (%)', fontsize=12, color=colors[0])
            elif 'candidate_ratio' in left_axis_metrics:
                ax1.set_ylabel('人数', fontsize=12, color=colors[0])
            ax1.tick_params(axis='y', labelcolor=colors[0])
        
        # 右軸の設定
        lines2 = []
        labels2 = []
        if right_axis_metrics:
            ax2 = ax1.twinx()
            
            for i, metric in enumerate(right_axis_metrics):
                color_idx = len(left_axis_metrics) + i
                line = ax2.plot(data['year'], data[metric], 
                               marker=markers[color_idx % len(markers)], 
                               linewidth=2.5, 
                               markersize=7,
                               color=colors[color_idx % len(colors)], 
                               label=metric_labels[metric])
                lines2.extend(line)
                labels2.append(metric_labels[metric])
            
            ax2.set_ylabel('有権者数 (人)', fontsize=12, color=colors[len(left_axis_metrics)])
            ax2.tick_params(axis='y', labelcolor=colors[len(left_axis_metrics)])
            # Y軸の値をフォーマット（カンマ区切り）
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        # タイトル設定（padを大きく設定）
        year_range = input.year_range()
        title = f"選択された統計項目の推移 ({year_range[0]}年 - {year_range[1]}年)"
        ax1.set_title(title, fontsize=14, fontweight='bold', pad=30)
        
        # 凡例の位置を調整（少し下に移動）
        all_lines = lines1 + lines2
        all_labels = labels1 + labels2
        if all_lines:
            ax1.legend(all_lines, all_labels, loc='upper left', bbox_to_anchor=(0.02, 0.95))
        
        # グリッド
        ax1.grid(True, alpha=0.3)
        
        # X軸の年表示を調整
        ax1.set_xlim(data['year'].min() - 0.5, data['year'].max() + 0.5)
        
        # レイアウトの調整（右側マージンを拡大）
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.85)
        
        return fig

app = App(app_ui, server)