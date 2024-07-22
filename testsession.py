from dash import Dash, dcc, html, dash_table, Input, Output, State, callback,ctx
from dash_extensions.enrich import Trigger, FileSystemCache

import time
import base64
import datetime
import io
import uuid

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
   
    session_id = str(uuid.uuid4())

    fsc = FileSystemCache(f"{session_id}_cache_dir")
    fsc1= FileSystemCache(f"{session_id}_cache_tools")
    fsc.set("progress", '0')
    fsc1.set("tools",'idle')
    return html.Div([
    html.Div(session_id, id='session-id', style={'display': 'none'}),
    html.Div(dcc.Input(id="input_session_id",type="text",value=session_id))
    ])
app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=True)