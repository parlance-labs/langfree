from shiny import module, ui, render
import shiny.experimental as x
from langfree.transform import RunData

@module.server
def chat_server(input, output, session, run:RunData):
    "Provide components to render the llm inputs as `llm_inputs` and llm output as `llm_output`."

    @output
    @render.ui
    def llm_inputs():
        "Render the chat history, except for the last output as a list of cards."
        cards = []
        for m in run.inputs:
            content = str(m["content"] if 'content' in m else m["function_call"])
            cards.append(
                x.ui.card(
                    x.ui.card_header(ui.div(
                                       {"style": "font-weight: bold;"}, 
                                        m["role"].upper()
                                    )       
                    ),
                    x.ui.card_body(ui.markdown(content)),
                    fill=False,
                )
            )
        return ui.div(*cards)

    @output
    @render.ui
    def llm_output():
        "Render the LLM output as an editable text box."
        o = run.output
        return x.ui.card(
            x.ui.card_header(o["role"]),
            x.ui.card_body(ui.input_text_area('llm_output', label='LLM Output (Edit)', value=o['content'])),
        )

@module.ui
def input_ui(): return ui.output_ui('llm_inputs')
@module.ui
def output_ui(): return ui.output_ui('llm_output')
