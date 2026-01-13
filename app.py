from shiny import App, reactive, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

try:
    import japanize_matplotlib
except ImportError:
    plt.rcParams['font.sans-serif'] = [
        'Hiragino Sans', 'Yu Gothic', 'Meiryo',
        'MS Gothic', 'Arial Unicode MS', 'sans-serif'
    ]
    plt.rcParams['axes.unicode_minus'] = False


# -----------------------------
# 市町村マッピング
# -----------------------------
municipalities_mapping = {
    "oosk": "大阪市", "ski": "堺市", "tynk": "豊中市", "suita": "吹田市",
    "tktk": "高槻市", "hrkt": "枚方市", "yo": "八尾市", "nygw": "寝屋川市",
    "hoska": "東大阪市", "kswd": "岸和田市"
}


# -----------------------------
# データ読み込み
# -----------------------------
def load_csv_data(code, vote_type):
    base_dir = Path(__file__).parent
    path = base_dir / "data" / "merged_output" / f"{code}_{vote_type}_merged.csv"
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def process_dataframe(df):
    if df is None:
        return None

    df = df.rename(columns={
        "投票日": "vote_date",
        "投票率": "turnout_rate",
        "有権者数": "total_voters",
        "男性": "male_voters",
        "女性": "female_voters",
        "定数/候補者数": "seats_candidates"
    })

    df["vote_date"] = pd.to_datetime(df["vote_date"], errors="coerce")
    df["year"] = df["vote_date"].dt.year

    for c in ["turnout_rate", "total_voters", "male_voters", "female_voters"]:
        if c in df.columns:
            df[c] = (
                df[c].astype(str)
                .str.replace("%", "")
                .str.replace(",", "")
                .astype(float)
            )

    if "seats_candidates" in df.columns:
        s = df["seats_candidates"].astype(str).str.split("/", expand=True)
        df["fixed_seats"] = pd.to_numeric(s[0], errors="coerce")
        df["candidate_count"] = pd.to_numeric(s[1], errors="coerce")
        df["candidate_ratio"] = df["fixed_seats"] / df["candidate_count"]

    return df


def generate_sample_data(start, end):
    years = np.arange(start, end + 1)
    return pd.DataFrame({
        "year": years,
        "turnout_rate": np.random.uniform(40, 65, len(years)),
        "total_voters": np.random.randint(50000, 120000, len(years)),
        "male_voters": np.random.randint(24000, 58000, len(years)),
        "female_voters": np.random.randint(26000, 62000, len(years)),
        "candidate_count": np.random.randint(20, 30, len(years)),
        "fixed_seats": np.random.randint(15, 25, len(years))
    })


# -----------------------------
# UI
# -----------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("表示設定"),
        ui.input_selectize(
            "selention_pre",
            "市町村（最大2つ）",
            municipalities_mapping,
            multiple=True,
            options={"maxItems": 2}
        ),
        ui.input_select(
            "vote_type", "選挙種別",
            {"a": "首長選挙", "b": "議員選挙"}
        ),
        ui.input_slider(
            "year_range", "年度範囲",
            min=1990, max=2030,
            value=[2000, 2025], sep=""
        ),
        ui.input_checkbox_group(
            "selected_metrics",
            "表示項目",
            {
                "turnout_rate": "投票率",
                "total_voters": "有権者数",
                "male_voters": "男性",
                "female_voters": "女性",
                "candidate_ratio": "定数/候補者数"
            },
            selected=["turnout_rate"]
        )
    ),
    ui.card(
        ui.card_header("市町村別 統計推移"),
        ui.output_plot("statistics_plot")
    )
)


# -----------------------------
# server
# -----------------------------
def server(input, output, session):

    @reactive.calc
    def data_all():
        results = {}
        for code in input.selention_pre():
            df = load_csv_data(code, input.vote_type())
            if df is None:
                y0, y1 = input.year_range()
                df = generate_sample_data(y0, y1)
                real = False
            else:
                df = process_dataframe(df)
                real = True

            df = df[(df["year"] >= input.year_range()[0]) &
                    (df["year"] <= input.year_range()[1])]
            results[code] = (df, real)
        return results

    @render.plot
    def statistics_plot():
        candidate_bar_colors = {
            "candidate_count": "#60a5fa",  # 青（水色系）
            "fixed_seats": "#9ca3af"       # グレー
        }
        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax2 = ax1.twinx()

        metric_colors = {
            "turnout_rate": "#2563eb",
            "total_voters": "#dc2626",
            "male_voters": "#059669",
            "female_voters": "#7c3aed",
            "candidate_ratio": "#ea580c"
        }

        styles = [
            {"alpha": 1.0, "linestyle": "-",  "marker": "o", "offset": -0.2},
            {"alpha": 0.5, "linestyle": "--", "marker": "s", "offset": 0.2}
        ]

        for i, (code, (df, _)) in enumerate(data_all().items()):
            style = styles[i]
            name = municipalities_mapping.get(code, code)

            for metric in input.selected_metrics():
                if metric == "turnout_rate":
                    ax1.plot(
                        df["year"], df[metric],
                        color=metric_colors[metric],
                        linestyle=style["linestyle"],
                        alpha=style["alpha"],
                        marker=style["marker"],
                        linewidth=2.5,
                        label=f"{name}：投票率"
                    )

                elif metric == "candidate_ratio":
                    years = df["year"] + style["offset"]
                    ax2.bar(
                        years, df["candidate_count"],
                        width=0.35,
                        color=candidate_bar_colors["candidate_count"],
                        alpha=0.3 * style["alpha"],
                        label=f"{name}：候補者数"
                    )
                    ax2.bar(
                        years, df["fixed_seats"],
                        width=0.35,
                        color=candidate_bar_colors["fixed_seats"],
                        alpha=0.7 * style["alpha"],
                        label=f"{name}：定数"
                    )

                else:
                    ax2.plot(
                        df["year"], df[metric],
                        color=metric_colors[metric],
                        linestyle=style["linestyle"],
                        alpha=style["alpha"],
                        marker=style["marker"],
                        linewidth=2.5,
                        label=f"{name}：{metric}"
                    )

        ax1.set_xlabel("年")
        ax1.set_ylabel("投票率 (%)")
        ax2.set_ylabel("人数")

        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

        ax1.set_ylim(20, 80)
        start, end = input.year_range()
        ax1.set_xlim(start - 0.5, end + 0.5)

        return fig


app = App(app_ui, server)
