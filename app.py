from dash import Dash, dcc, html, dash_table, Input, Output, State, callback

import base64
import datetime
import io

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

@app.callback(Output('output-data-upload','children'),
            [Input('upload-data','contents'),
             Input('upload-data','filename')])
def get_data(contents,filename):
    print(filename)
    #print(contents)
    try:
        encoded_content=contents[0].split(',')[1]
        pdf_buffer=io.BytesIO(base64.b64decode(encoded_content))
        #loader = PyPDFLoader(pdf_buffer)
        reader = PdfReader(pdf_buffer)
        #
        #print(dir(reader))
        page = reader.pages[20]
        print(reader.get_num_pages())
        #print(page.extract_text())

        #in case to save pdf file into assets
        #with open(f'assets/{filename[0]}','wb') as pdfile:
        #    pdfile.write(base64.b64decode(encoded_content))
        #loader = PyPDFLoader(f'assets/{filename[0]}')
        #docs=loader.load_and_split()
        #print(docs[20])


        
    except Exception as e:
        print(e)




    
    

    return ''

if __name__ == '__main__':
    app.run(debug=True)

