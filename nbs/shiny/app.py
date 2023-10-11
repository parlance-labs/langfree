from shiny import App, ui
from langfree.shiny import chat_server, input_ui, output_ui
from langfree.transform import RunData

_run = RunData.from_run_id('59080971-8786-4849-be88-898d3ffc2b45')

app_ui = ui.page_fluid(
    input_ui("chat"),
    output_ui("chat"),
)

def server(input, output, session):
    chat_server("chat", run=_run)

app = App(app_ui, server)