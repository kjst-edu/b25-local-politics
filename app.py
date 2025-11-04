import seaborn as sns

# Import data from shared.py
from shared import df

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("graph_shapes", "グラフの種類", choices=["なめらか", "あらめ"]),
        ui.input_select(
            "val", "変数を選択", choices=["bill_length_mm", "body_mass_g", "island", "flipper_length_mm", "sex"], selected=None
        ),
        ui.input_switch("sex", "性別", value=True),
        ui.input_switch("show_rug", "Show Rug", value=False),
    ),
    ui.output_plot("histgram"),
    title="Hello sidebar!",
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


app = App(app_ui, server)
