import seaborn as sns

# Import data from shared.py
#from shared import df

from shiny import App, render, ui
"""""
#選択項目
app_ui = ui.page_sidebar(
    ui.sidebar(
        
        ui.input_select(
        "val", "1つ目の項目を選択:", choices=["投票率", "有権者数", "定数比", "有権者数（男女別）"], selected=None
        ),
        ui.input_select(
        "val", "2つ目の項目を選択:", choices=["投票率", "有権者数", "定数比", "有権者数（男女別）"], selected=None
        ),
    ),    
    ui.output_plot("histgram"),
    title="大阪の政治",
)

def server(input, output, session):
    @render.plot
    def histgram():
        hue = "sex" if input.sex() else None
        if input.graph_shapes()=="あらめ":
            sns.displot(df, x=input.val(), hue=hue)
        if input.graph_shapes()=="なめらか":
            sns.kdeplot(df, x=input.val(), hue=hue)
        if input.show_rug():
            sns.rugplot(df, x=input.val(), hue=hue, color="black", alpha=0.25)

app_ui = ui.page_fluid(
    ui.input_slider("slider", "Slider", min=0, max=100, value=[35, 65]),  
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return f"{input.slider()}"

app = App(app_ui, server)
"""""
#頭文字検索参考例
from shiny import App, reactive, render, ui
import pandas as pd

# 大阪府の市町村データ
municipalities_data = [
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
    {"name":"泉佐野市","reading":"いずみさのし","type":"市"},
    {"name":"富田林市","reading":"とんだばやしし","type":"市"},
    {"name":"河内長野市","reading":"かわちながのし","type":"市"},
    {"name":"松原市","reading":"まつばらし","type":"市"},
    
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
#以下検索欄（頭文字＋市町村＋自由検索）

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("検索条件"),
        ui.input_select(
            "initial_letter",
            "頭文字を選択:",
            choices={
                "": "すべて",
                "あ": "あ行",
                "か": "か行", 
                "さ": "さ行",
                "た": "た行",
                "な": "な行",
                "は": "は行",
                "ま": "ま行",
                "や": "や行",
                "ら": "ら行",
                "わ": "わ行",
            },
            selected=""
        ),
        ui.input_select(
            "municipality_type",
            "自治体種別:",
            choices={
                "": "すべて",
                "市": "市",
                "町": "町",
                "村": "村",
            },
            selected=""
        ),
        ui.input_text(
            "name_filter",
            "市町村名で絞り込み:",
            value="",
            placeholder="市町村名の一部を入力"
        ),
        ui.br(),
        ui.p(f"総登録数: {len(municipalities_df)}件")
    ),
    ui.card(
        ui.card_header("検索結果"),
        ui.output_data_frame("municipalities_table")
    ),
    ui.card(
        ui.card_header("選択した市町村"),
        ui.output_ui("selected_municipality_info")
    )
)

def server(input, output, session):
    @reactive.calc
    def filtered_municipalities():
        df = municipalities_df.copy()
        
        # 頭文字による絞り込み
        if input.initial_letter():
            # ひらがなの行による分類
            hiragana_ranges = {
                "あ": ["あ", "い", "う", "え", "お"],
                "か": ["か", "き", "く", "け", "こ", "が", "ぎ", "ぐ", "げ", "ご"],
                "さ": ["さ", "し", "す", "せ", "そ", "ざ", "じ", "ず", "ぜ", "ぞ"],
                "た": ["た", "ち", "つ", "て", "と", "だ", "ぢ", "づ", "で", "ど"],
                "な": ["な", "に", "ぬ", "ね", "の"],
                "は": ["は", "ひ", "ふ", "へ", "ほ", "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ"],
                "ま": ["ま", "み", "む", "め", "も"],
                "や": ["や", "ゆ", "よ"],
                "ら": ["ら", "り", "る", "れ", "ろ"],
                "わ": ["わ", "ゐ", "ゑ", "を", "ん"]
            }
            
            target_chars = hiragana_ranges.get(input.initial_letter(), [])
            df = df[df["reading"].str[0].isin(target_chars)]
        
        # 自治体種別による絞り込み
        if input.municipality_type():
            df = df[df["type"] == input.municipality_type()]
        
        # 名前による絞り込み
        if input.name_filter():
            df = df[df["name"].str.contains(input.name_filter(), na=False)]
        
        return df.sort_values("reading").reset_index(drop=True)
    
    @render.data_frame
    def municipalities_table():
        df = filtered_municipalities()
        
        # 表示用のデータフレームを作成
        display_df = df[["name", "type", "reading"]].copy()
        display_df.columns = ["市町村名", "種別", "読み方"]
        
        return render.DataTable(
            display_df,
            height="400px",
            summary=f"検索結果: {len(display_df)}件",
            selection_mode="row"  # 行選択を有効化
        )
    
    @render.ui
    def selected_municipality_info():
        # データテーブルの選択状態を取得
        try:
            selected_rows = input.municipalities_table_selected_rows()
            
            if not selected_rows or len(selected_rows) == 0:
                return ui.div(
                    ui.p("市町村を選択してください。"),
                    ui.p("表の行をクリックして選択できます。"),
                    style="color: #666; font-style: italic;"
                )
            
            # 選択された行のデータを取得
            filtered_df = filtered_municipalities()
            selected_idx = selected_rows[0]
            
            if selected_idx < len(filtered_df):
                selected_municipality = filtered_df.iloc[selected_idx]
                
                return ui.div(
                    ui.h4(f"📍 {selected_municipality['name']}", style="color: #2563eb;"),
                    ui.div(
                        ui.p(f"📋 種別: {selected_municipality['type']}"),
                        ui.p(f"🔤 読み方: {selected_municipality['reading']}"),
                        style="background-color: #f8fafc; padding: 15px; border-radius: 5px; margin-top: 10px;"
                    ),
                    ui.hr(),
                    ui.div(
                        ui.strong("✅ 選択完了"),
                        ui.p(f"「{selected_municipality['name']}」が選択されました。"),
                        style="color: #059669; background-color: #ecfdf5; padding: 10px; border-radius: 5px; border-left: 4px solid #10b981;"
                    )
                )
            else:
                return ui.p("選択データが見つかりません。")
        
        except Exception as e:
            return ui.p(f"エラーが発生しました: {str(e)}")

app = App(app_ui, server)
