from dash import Dash, dcc, html, dash_table, Input, Output, State, callback,ctx
from dash_extensions.enrich import Trigger, FileSystemCache

import base64
import datetime
import io

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader
from utils import *
from tqdm import tqdm

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
ref_tools=pd.read_csv('reference_tools.csv')
tools_list=ref_tools['software'].to_list()
fsc = FileSystemCache("cache_dir")
fsc1= FileSystemCache("cache_tools")
fsc.set("progress", '0')
fsc1.set("tools",'idle')
#print(tools_list)
'''
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
                
    ),
    html.Div(id='output-data-upload'),
    html.Progress(id='loadbar',max=100),
    html.Br(),
    html.Button('Scan',id='scanner-button',n_clicks=0),
    html.Div(id='msg-div'),
    html.Div(id='tool-div'),
    html.Div(id='vulnerabilities-div'),
    dcc.Store(id='pdf_content'),
    dcc.Interval(id='check-bar-interval',interval=500,n_intervals=0)
])
'''

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Vulnerability Scanner", style={'textAlign': 'center', 'color': '#2C3E50'}),
        html.Hr()
    ], style={'padding': '10px', 'backgroundColor': '#ECF0F1'}),

    # File Upload Section
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arrastre aquí el PDF o  ',
                html.A('Seleccione', style={'color': '#3498DB', 'textDecoration': 'underline'})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '20px 0',
                'backgroundColor': '#F2F3F4',
                'cursor': 'pointer'
            }
        )
    ], style={'textAlign': 'center'}),

    # Output Section
    html.Div(id='output-data-upload', style={'margin': '20px 0'}),

    # Progress Bar
    html.Div([
        html.Progress(id='loadbar', max=100, style={'width': '100%', 'margin': '10px 0'}),
        html.Br(),
        html.Button('Escanear', id='scanner-button', n_clicks=0, style={
            'width': '100%',
            'backgroundColor': '#3498DB',
            'color': 'white',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'fontSize': '16px'
        })
    ], style={'textAlign': 'center'}),

    # Message and Tool Sections
    html.Div(id='msg-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': '#F2F3F4', 'borderRadius': '5px'}),
    html.Div(id='tool-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': '#F2F3F4', 'borderRadius': '5px'}),
    html.Img(id='wordcloud-image'),
    html.Div(id='vulnerabilities-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': '#F2F3F4', 'borderRadius': '5px'}),

    # Hidden Storage and Interval Component
    dcc.Store(id='pdf_content'),
    dcc.Interval(id='check-bar-interval', interval=500, n_intervals=0)
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ECF0F1', 'padding': '20px'})

#this callback tracks which tool is being scanned during the process
@app.callback(Output('tool-div','children'),
              [Input('check-bar-interval','n_intervals')])
def check_tool_progress(n):
    value=fsc1.get('tools')
    if value is None:
        value='idle'
    return value
#this callback tracks the progress bar
@app.callback(Output('loadbar','value'),
              Output('loadbar','title'),
             [Input('check-bar-interval','n_intervals')])
def check_loadbar(n):
    value=fsc.get("progress")
    if value is None:
        value='0'
    
    return value,f'{round(float(value),0)} %'

# this callback is the pdf loading process, all the pdf contents are loaded to a dcc.Store
@app.callback(Output('output-data-upload','children'),
              Output('pdf_content','data'),
            [Input('upload-data','contents'),
             Input('upload-data','filename')])
def get_data(contents,filename):
    print(filename)
    #print(contents)
    try:
        
        return filename,contents


        
    except Exception as e:
        print(e)
 

    return '',[]
# this callback is the main process
@app.callback(Output('msg-div','children'),
              Output('vulnerabilities-div','children'),
              [Input('scanner-button','n_clicks'),
               State('pdf_content','data')])
def scan_doc(nclicks,pdfdata):
    
    if ctx.triggered_id=='scanner-button':
        fsc.set("progress", '0')
        try:
            encoded_content=pdfdata.split(',')[1]
        except:
            return '',''
        pdf_buffer=io.BytesIO(base64.b64decode(encoded_content))
        
        #loader = PyPDFLoader(pdf_buffer)
        reader = PdfReader(pdf_buffer)
        #
        #print(dir(reader))
        #page = reader.pages[20]
        total_pages=reader.get_num_pages()
        
        print(f'Searching in {total_pages}')
        big_str=''
        print('Loading pdf file')
        for n in tqdm(range(total_pages)):
            #print(f'page {n+1}')
            page=reader.pages[n]
            page_text=page.extract_text()
            big_str+=' '+page_text.lower()
            progress=n*100/total_pages
            
            fsc.set("progress", f'{progress}')
        fsc.set("progress", '100')
        print('loaded')
        print('looking for tools')
        tools_found=[]
        for word in tqdm(tools_list):
            status=word_finder(word,big_str)
            if status:
                tools_found.append(word)
        tools_found=list(set(tools_found))
        print(tools_found)
        
        vulnerabilities_list=[]
        for tool in tools_found:
            fsc1.set("tools",f'Escaneando {tool} ..')
           
            df=get_vulnerability_dataframe(tool)
            if df.shape[0]>0:
                vulnerabilities_list.append(df)
            else:
                fsc1.set("tools",f'Hubo un problema escaneando {tool} ..')

        fsc1.set("tools","Análisis Finalizado") 
        if len(vulnerabilities_list)>0:   
            all_vulnerabilities_df=pd.concat(vulnerabilities_list,ignore_index=True)
            vul_data_table=create_datatable(all_vulnerabilities_df)
            wordcloud_text=' '.join(all_vulnerabilities_df['Descripción'].to_list())
            wordcloud_image=get_wordcloud(wordcloud_text)
        else:
            vul_data_table=''

        
        



        

        #in case to save pdf file into assets
        #with open(f'assets/{filename[0]}','wb') as pdfile:
        #    pdfile.write(base64.b64decode(encoded_content))
        #loader = PyPDFLoader(f'assets/{filename[0]}')
        #docs=loader.load_and_split()
        #print(docs[20])
        return 'Documento cargado',vul_data_table
    return '',''
if __name__ == '__main__':
    app.run(debug=True)

