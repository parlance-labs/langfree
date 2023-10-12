from shiny import App, ui, reactive, render
import shiny.experimental as x
from langfree.shiny import render_input_chat, render_llm_output
from langfree.transform import RunData

index = 0 
runs = [RunData.from_run_id('59080971-8786-4849-be88-898d3ffc2b45'), 
        RunData.from_run_id('59080971-8786-4849-be88-898d3ffc2b45')]

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
            ui.input_action_button("reject", label="Back", class_='btn-secondary', width="20%"),
        )
    ),
)

def server(input, output, session):
    current_run = reactive.Value(runs[index])

    @output
    @render.ui
    def llm_input():
        return render_input_chat(current_run())
    
    @output
    @render.ui
    def llm_output():
        return render_llm_output(current_run())

app = App(app_ui, server)