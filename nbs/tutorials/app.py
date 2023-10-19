import os
from shiny import App, ui, reactive, render
import shiny.experimental as x
from langfree.shiny import render_input_chat, render_llm_output
import pandas as pd


FILENAME = "_data/sample_data.pkl"
df = pd.read_pickle(FILENAME)
n_rows = len(df)
def save(df): df.to_pickle(FILENAME)

status_styles = {'Accepted': 'bg-success', 'Rejected': 'bg-danger','Pending': 'bg-warning'}
status_icons = {'Accepted': ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" class="bi bi-check-lg" viewBox="0 0 16 16" style="height:auto;width:100%;fill:currentColor;" aria-hidden="true" role="img"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/></svg>'), 
                'Rejected': ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" class="bi bi-x-lg" viewBox="0 0 16 16" style="height:auto;width:100%;fill:currentColor;" aria-hidden="true" role="img"><path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/></svg>'),
                'Pending': ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" class="bi bi-clock" viewBox="0 0 16 16" style="height:auto;width:100%;fill:currentColor;" aria-hidden="true" role="img"><path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/></svg>')
              }

app_ui = ui.page_fluid(
    ui.panel_title("Fine Tune Data Review"),
    ui.div(
        {"style": "position: absolute; top: 10px; right: 10px; font-size: 0.8em;"},
        ui.a("by Parlance Labs", href="https://parlance-labs.com/")
    ),
    x.ui.card(
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.output_ui("status_card"),
                ui.output_data_frame("stats"),
            ),
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
            ui.input_action_button("accept", label="Accept", class_='btn-success', width="10%",  style="margin-right: 10px;"),
            ui.input_action_button("reject", label="Reject", class_='btn-danger', width="10%",  style="margin-right: 50px;"),
            ui.input_action_button("back", label="Back", class_='btn-secondary', width="10%", style="margin-right: 10px;"),
            ui.input_action_button("reset", label="Reset", class_='btn-warning', width="10%", style="margin-right: 10px;"),
            ui.input_action_button("next", label="Next", class_='btn-secondary', width="10%", style="margin-right: 10px;"),
        )
    ),
)

def server(input, output, session):
    cursor = reactive.Value(0)
    status_trigger = reactive.Value(True)

    @reactive.Calc
    def current_run():
        _ = status_trigger()
        return df.loc[cursor(), 'child_run']

    @reactive.Calc
    def current_row(): 
        _ = status_trigger()
        return df.loc[cursor()]

    @reactive.Calc
    def progress(): return f"Record {cursor()+1} of {n_rows:,}"

    @output
    @render.ui
    def llm_input(): return render_input_chat(current_run())
    
    @output
    @render.ui
    def llm_output(): return render_llm_output(current_run())

    @output
    @render.data_frame
    def stats():
        _ = status_trigger()
        return df.groupby('status').count().reset_index().rename(columns={'child_run': 'Count', 'status': 'Status'})[['Status', 'Count']]

    @output
    @render.ui
    def status_card():
        status = current_row().status
        return x.ui.value_box(title=ui.h1(f'Status: {status}'), 
                              value=ui.h2(progress()), 
                              showcase=status_icons[status], 
                              class_=status_styles[status])
    
    @reactive.Effect
    @reactive.event(input.reset)
    def reset():
        update_status('Pending')
        save(df)

    @reactive.Effect
    @reactive.event(input.reject)
    def reject():
        update_status('Rejected')
        go_next()

    @reactive.Effect
    @reactive.event(input.accept)
    def accept():
        update_status('Accepted')
        current_row().child_run.output['content'] = input.llm_output()
        invoke_later(1, go_next)

    @reactive.Effect
    @reactive.event(input.back)
    def back(): 
        if cursor() > 0: cursor.set(cursor()-1)

    @reactive.Effect
    @reactive.event(input.next)
    def next(): go_next()

    def modal():
        m = ui.modal("You are done!", title="Done",easy_close=True,footer=None)
        ui.modal_show(m)

    def go_next():
        save(df)
        if cursor() + 1 < n_rows: cursor.set(cursor()+1)
        else: modal()

    def update_status(status):
        df.loc[cursor(), 'status'] = status
        status_trigger.set(not status_trigger())

abs_path = os.path.join(os.path.dirname(__file__), 'assets')
app = App(app_ui, server, static_assets=abs_path)