from shiny import App, ui, reactive, render
import shiny.experimental as x
from langfree.shiny import render_input_chat, render_llm_output
import pandas as pd

FILENAME = "_data/sample_data.pkl"
df = pd.read_pickle(FILENAME)
n_rows = len(df)
def save(df): df.to_pickle(FILENAME)

app_ui = ui.page_fluid(
    ui.panel_title("LLM Review App"),
    x.ui.card(
        ui.layout_sidebar(
            ui.panel_sidebar(ui.markdown("Sidebar Placeholder")),
            ui.panel_main(
                ui.output_ui("llm_input"),
            ),
        ),
        max_height="900px",
    ),
    x.ui.card(
        x.ui.card_body(
            ui.output_ui("llm_output"),
        ),
        ui.div(
            {"style": "display: flex; justify-content:center;"},
            ui.input_action_button("accept", label="Accept", class_='btn-success', width="20%",  style="margin-right: 10px;"),
            ui.input_action_button("reject", label="Reject", class_='btn-danger', width="20%",  style="margin-right: 10px;"),
            ui.input_action_button("back", label="Back", class_='btn-secondary', width="20%"),
        )
    ),
)

def server(input, output, session):
    cursor = reactive.Value(0)

    @reactive.Calc
    def current_run(): return df.loc[cursor(), 'child_run']

    @reactive.Calc
    def current_row(): return df.loc[cursor()]

    @output
    @render.ui
    def llm_input(): return render_input_chat(current_run())
    
    @output
    @render.ui
    def llm_output(): return render_llm_output(current_run())
    
    @reactive.Effect
    @reactive.event(input.reject)
    def reject():
        current_row().accept = 0
        current_row().reject = 1
        go_next()

    @reactive.Effect
    @reactive.event(input.accept)
    def accept():
        current_row().accept = 1
        current_row().reject = 0
        current_row().child_run.output['content'] = input.llm_output()
        go_next()

    @reactive.Effect
    @reactive.event(input.back)
    def back(): 
        if cursor() > 0: cursor.set(cursor()-1)

    def modal():
        m = ui.modal("You are done!", title="Done",easy_close=True,footer=None)
        ui.modal_show(m)

    def go_next():
        save(df)
        if cursor() + 1 < n_rows: cursor.set(cursor()+1)
        else: modal()

app = App(app_ui, server)