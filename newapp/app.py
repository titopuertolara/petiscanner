from dash_extensions.enrich import Trigger, FileSystemCache

import time
import base64
import datetime
import io
from dash import Dash, html, Input, Output, callback_context
import pandas as pd
#from pypdf import PdfReader
from utils import *
from tqdm import tqdm
import plotly.graph_objects as go 
import plotly.express as px
import uuid
from layout import serve_layout

app = Dash(__name__ , suppress_callback_exceptions=True)

fsc = FileSystemCache("Cache/cache_dir")
fsc1 = FileSystemCache("Cache/cache_tools")

def generate_layout():
    session_id = str(uuid.uuid4())
    return serve_layout(session_id)


app.layout = generate_layout  



@app.callback(Output('loadbar', 'value'), 
             [Input('check-bar-interval','n_intervals'),
              Input('session-id', 'data')])
def show_session_id(n,session_id):
    print(session_id)
    value=fsc.get(f'{session_id[0]}_progress')
    print('valor',value)
    return value
# Callbacks

@app.callback(Output('session-id-output-2', 'children'), 
             [Input('session-id', 'data')])
def show_session_id(session_id):
    print(session_id)
    for i in range(100):
        fsc.set(f'{session_id[0]}_progress',f"{i}")
        time.sleep(0.5)
    
    return 'ok'

@app.callback(
    [
        Output("upload-section", "style"),
        Output("loadbar", "style"),
        Output("btn-upload", "style"),
        Output("btn-how", "style"),
        Output("btn-who", "style"),
        Output("btn-info", "style"),
    ],
    [Input("btn-upload", "n_clicks"), Input("btn-how", "n_clicks"),
     Input("btn-who", "n_clicks"), Input("btn-info", "n_clicks")],
)
def handle_button_click(n_upload, n_how, n_who, n_info):
    ctx = callback_context
    if not ctx.triggered:
        return {"display": "none"}, {"display": "none"}, *([{
            "backgroundColor": "#FFFFFF", 
            "color": "#FF5A36", 
            "border": "2px solid #FF5A36",
            "borderRadius": "10px",
            "padding": "1.5rem",
            "fontWeight": "bold",
            "textAlign": "center",
            "cursor": "pointer",
            "fontSize": "1.2rem",
            "width": "100%",
            "boxSizing": "border-box",
        }] * 4)

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Default and selected styles
    default_style = {
        "backgroundColor": "#FFFFFF", 
        "color": "#FF5A36", 
        "border": "2px solid #FF5A36",
        "borderRadius": "10px",
        "padding": "1.5rem",
        "fontWeight": "bold",
        "textAlign": "center",
        "cursor": "pointer",
        "fontSize": "1.2rem",
        "width": "100%",
        "boxSizing": "border-box",
    }
    selected_style = {
        **default_style,
        "backgroundColor": "#FF5A36", 
        "color": "#FFFFFF",
    }

    # Logic for each button
    if button_id == "btn-upload":
        return {"display": "block"}, {"display": "block"}, selected_style, default_style, default_style, default_style
    elif button_id == "btn-how":
        return {"display": "none"}, {"display": "none"}, default_style, selected_style, default_style, default_style
    elif button_id == "btn-who":
        return {"display": "none"}, {"display": "none"}, default_style, default_style, selected_style, default_style
    elif button_id == "btn-info":
        return {"display": "none"}, {"display": "none"}, default_style, default_style, default_style, selected_style
    else:
        return {"display": "none"}, {"display": "none"}, *([default_style] * 4)

if __name__ == "__main__":
    app.run_server(debug=True)