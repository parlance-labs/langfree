from shiny import App, ui, reactive, render
import shiny.experimental as x
from langfree.shiny import render_input_chat, render_llm_output
import pandas as pd
from langfree.experimental import ChatRecordSet

FILENAME = "_data/sample_data.pkl"
cursor = 0 
df = pd.read_pickle(FILENAME)

def save(df): df.to_csv(FILENAME)

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
    current_row = reactive.Value(df.loc[cursor].child_run)

    @output
    @render.ui
    def llm_input():
        return render_input_chat(current_row())
    
    @output
    @render.ui
    def llm_output():
        return render_llm_output(current_row())
    
    # @reactive.Effect
    # @reactive.event(input.reject)
    # def reject():
    #     global df
    #     df.loc[cursor, 'reject'] = 1
    #     df.loc[cursor, 'accept'] = 0
    #     save(df)
    #     go_next(df)

    # @reactive.Effect
    # @reactive.event(input.accept)
    # def accept():
    #     global df
    #     df.loc[cursor, 'accept'] = 1
    #     df.loc[cursor, 'reject'] = 0
    #     child_run = df.loc[cursor, 'child_run']
    #     child_run.output = input.json_out()
    #     df.loc[cursor, 'child_run'] = child_run
    #     save(df)
    #     go_next(df)

    # def modal():
    #     m = ui.modal(
    #         "You are done!",
    #         title="Done",
    #         easy_close=True,
    #         footer=None,
    #     )
    #     ui.modal_show(m)

    # def go_next(df):
    #     global cursor
    #     if cursor + 1 < len(df):
    #         cursor += 1
    #         current_row.set(df.loc[cursor])
    #     else: modal()


app = App(app_ui, server)