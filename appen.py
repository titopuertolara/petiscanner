from dash import Dash, dcc, html, dash_table, Input, Output, State, callback,ctx
from dash_extensions.enrich import Trigger, FileSystemCache
import time
import base64
import datetime
import io

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader
from utils import *
from tqdm import tqdm
import plotly.graph_objects as go 
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
ref_tools=pd.read_csv('reference_tools.csv')
tools_list=ref_tools['software'].to_list()
fsc = FileSystemCache("cache_dir")
fsc1= FileSystemCache("cache_tools")
fsc.set("progress", '0')
fsc1.set("tools",'idle')
colors_piechart=px.colors.qualitative.D3
#print(tools_list)

with open("stopwords-en.txt","r") as sfile:
    stopwords=sfile.readlines()
stopwords=[i.replace('\n','') for i in stopwords]
#stopwords.append('el')
#stopwords.append('la')
#stopwords.append('los')
#stopwords.append('en')
#print(stopwords)

colors = {
    'background': '#73D0B3',
    'header_background': '#00B08B',
    'header_text': 'white',
    'text': '#2C3E50',
    'link': 'white',
    'link2': '#00B08B',
    'upload_background': 'white',
    'button_background': '#FF3843',
    'button_text': 'white',
    'div_background': 'white',
    'progress_bar': '#00B08B'
}

app.layout = html.Div([
    # Header
    html.Div([
        
        html.Div([
        html.Div([
            html.H1("OSV Scanner", style={'color': colors['header_text'], 'marginRight': '10px', 'display': 'inline-block'}),
            html.P("powered by"),
            html.Img(src='/assets/logo.png', style={'height': '60px', 'verticalAlign': 'middle'})
        ], style={'display': 'flex', 'alignItems': 'center','justifyContent': 'center',}),
        html.Hr()
    ], style={'padding': '10px', 'backgroundColor': colors['header_background']}),
        
        html.H5(id='header-1',children=[
            "This App uses the ",
            html.A('National Vulnerability Database API', href='https://nvd.nist.gov/',target='_blank', style={'color': colors['link']}),
            
        ], style={'textAlign': 'center', 'color': colors['header_text']}),
        html.P("The main purpose of this tool is to help local governments to identify digital infrastructure vulnerabilities trough their official docs. ", style={'textAlign': 'center', 'color': colors['header_text']}),
        html.Hr()
    ], style={'padding': '10px', 'backgroundColor': colors['header_background']}),

    # File Upload Section
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and drop PDF or ',
                html.A('Select', style={'color': colors['link2'], 'textDecoration': 'underline'})
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
                'backgroundColor': colors['upload_background'],
                'cursor': 'pointer'
            }
        )
    ], style={'textAlign': 'center'}),

    # Output Section
    html.Div(id='output-data-upload', style={'margin': '20px 0'}),

    # Progress Bar and Scan Button
    html.Div([
        html.Progress(id='loadbar', max=100, style={'width': '100%', 'margin': '10px 0', 'color': colors['progress_bar']}),
        html.Br(),
        html.Button('Scan', id='scanner-button', n_clicks=0, style={
            'width': '100%',
            
            'backgroundColor': colors['button_background'],
            'color': colors['button_text'],
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'fontSize': '16px'
        })
    ], style={'textAlign': 'center'}),

    # Message and Tool Sections
    html.Div(id='msg-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px'}),
    html.Div(id='tool-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px'}),

    # Row for Word Cloud and Pie Chart Divs
    dcc.Loading(id='loading1',type='circle',
    children=[
        html.Div([
            html.Div(id='wordcloud-image', style={'flex': '1', 'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px', 'margin': '10px'}),
            html.Div(id='pie-chart-div', style={'flex': '1', 'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px', 'margin': '10px'})
        ], style={'display': 'flex', 'flexDirection': 'row'}),
        #Normalized barplot
        html.Div(id='normalized-barplot-div',style={'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px', 'margin': '10px'}),
        # Vulnerabilities Div
        html.Div(id='vulnerabilities-div', style={'margin': '20px 0', 'padding': '10px', 'backgroundColor': colors['div_background'], 'borderRadius': '5px'}),
    ]),
    # Hidden Storage and Interval Component
    dcc.Store(id='pdf_content'),
    dcc.Interval(id='check-bar-interval', interval=500, n_intervals=0)
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': colors['background'], 'padding': '20px'})

#callbacks for translation

#@app.callback()

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
    #in case to save pdf file into assets
    #with open(f'assets/{filename[0]}','wb') as pdfile:
    #    pdfile.write(base64.b64decode(encoded_content))
    #loader = PyPDFLoader(f'assets/{filename[0]}')
    #docs=loader.load_and_split()
    
    try:
        fsc.set("progress", '0')
        encoded_content=contents.split(',')[1]
        pdf_buffer=io.BytesIO(base64.b64decode(encoded_content))
        reader = PdfReader(pdf_buffer)
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
        fsc1.set("tools",f"Document ready.")
        print('loaded')
        return filename,[big_str]


        
    except Exception as e:
        print(e)
 

    return '',[]
# this callback is the main process
@app.callback(Output('msg-div','children'),
              Output('vulnerabilities-div','children'),
              Output('wordcloud-image','children'),
              Output('pie-chart-div','children'),
               Output('normalized-barplot-div','children'),
              [Input('scanner-button','n_clicks'),
               State('pdf_content','data')])
def scan_doc(nclicks,big_str):
    fsc1.set("tools","idle")
    if ctx.triggered_id=='scanner-button':
        progress_value=fsc.get("progress")
        if float(progress_value)<100:
            fsc1.set("tools",f"Document has not been loaded yet.")
            return '','','',''
    
            

        
        
        
        #loader = PyPDFLoader(pdf_buffer)
        
        #
        #print(dir(reader))
        #page = reader.pages[20]
        
        #print(big_str)
        
        print('looking for tools')
        tools_found=[]
        for word in tqdm(tools_list):
            status=word_finder(word,big_str[0])
            if status:
                tools_found.append(word)
        tools_found=list(set(tools_found))
        print(tools_found)
        
        vulnerabilities_list=[]
        
        true_counts=0
        for k ,tool in enumerate(tools_found):
            fsc1.set("tools",f'Querying {tool} ({k+1}/{len(tools_found)})..')
            df,msg=get_vulnerability_dataframe(tool.strip(),lang='en')
            print(tool,msg)
            if df.shape[0]>0:
                vulnerabilities_list.append(df)
                true_counts+=1
            if not msg:
                fsc1.set("tools",f"There's an issue scanning {tool} from NVD (please search directly from main website)")
                time.sleep(1)
                
        if len(tools_found)>0:
            efficency=round(100*true_counts/len(tools_found),1)
            if efficency==0:
                fsc1.set("tools",f"API is unstable or there are not vulnerabilities for these tools in the last month, please try again later.")

            elif efficency<50:
                fsc1.set("tools",f"Just {efficency}% of requests were succesful, wait 2 minutes and try scanning again.")
            else: 
                fsc1.set("tools",f"Finished with {efficency}% of succesful requests.")
        else:
            fsc1.set("tools",f"Not tools found inside this document.")


        if len(vulnerabilities_list)>0:
            all_vulnerabilities_df=pd.DataFrame()
            all_vulnerabilities_df=pd.concat(vulnerabilities_list,ignore_index=True)
            all_vulnerabilities_df=all_vulnerabilities_df.rename(columns={'Fecha':'Date','Autor':'Contributor',\
                                                                         'Vulnerabilidad':'Vulnerability',\
                                                                         'Herramienta':'Tool',\
                                                                         'Severidad':'Severity'})
            vul_data_table=create_datatable(all_vulnerabilities_df)
            wordcloud_text=' '.join(all_vulnerabilities_df['Vulnerability'].to_list()).lower()
            
            wordcloud_text=remove_stopwords(wordcloud_text,stopwords)
            wordcloud_image=get_wordcloud(wordcloud_text)
            wordcloud_plot=html.Img(src=wordcloud_image)
            print('pie chart')
            tools_count=pd.DataFrame(all_vulnerabilities_df['Tool'].value_counts())
            pie_fig=go.Figure()
            pie_fig.add_trace(go.Pie(labels=tools_count.index,values=tools_count['count'].values))
            pie_fig.update_traces(marker=dict(colors=colors_piechart))
            pie_fig.update_layout(
                    title="% of Vulnerabilities found in the last month.",
                    title_x=0.5,
                    legend=dict(
                        yanchor='top',
                        y=0.99,
                        xanchor='right',
                        x=0.95


                    ))
            pie_chart=dcc.Graph(figure=pie_fig)

            # severity plot
            #severity_df=all_vulnerabilities_df[~all_vulnerabilities_df['Severity'].isnull()]
            severity_df=all_vulnerabilities_df.copy()
            severity_df['Severity']=severity_df['Severity'].fillna('NOT SPECIFIED')
            severity_df=severity_df[severity_df['Tool'].isin(tools_found)]
            #print(severity_df['Tool'].value_counts())
            

            # this kind of plot creates a bug where previous x axes is saved and plot isnot reseted
            #category_orders = {
            #    'Severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            #}
            
            #hist_fig=go.Figure()
            #hist_fig=px.histogram(severity_df,x='Tool',\
            #     y=severity_df.index,\
            #     color='Severity',\
            #     barnorm='percent',text_auto=True,\
            #     #color_discrete_sequence=px.colors.qualitative.G10)
            #     color_discrete_sequence=['#FF6347', '#FFA500',  '#005B96','#87CEEB'],
            #     category_orders=category_orders)
            #hist_fig.update_traces(texttemplate='%{y:.2f}%')
            #hist_fig.update_yaxes(title="% of vulnerabilities")
            #hist_fig.update_layout(title='Vulnerabilities Severity',xaxis={'categoryorder':'total descending'})

            # TRYING TO FIX A BUGGED PLOT
            
            
            a=severity_df.groupby(['Tool','Severity']).count()[['Id']].reset_index()
            a=a.rename(columns={'Id':'Totalind'})
            b=a.groupby(['Tool']).sum()[['Totalind']].reset_index()
            b=b.rename(columns={'Totalind':'Total'})
            a=a.merge(b,how='inner',on='Tool')
            a['perc']=100*a['Totalind']/a['Total']
            a['perc']=a['perc'].apply(lambda x: round(x,1))

            color_discrete_sequence={'CRITICAL':'#FF6347','HIGH':'#FFA500','LOW':'#87CEEB','MEDIUM':'#005B96','NOT SPECIFIED':'gray'}
            hist_fig=go.Figure()
            for sev in a['Severity'].unique():
                dummy=a[a['Severity']==sev]

                hist_fig.add_trace(go.Bar(x=dummy['Tool'],\
                                    y=dummy['perc'],\
                                    name=sev,text=[f'{perc}% ({totalind})' for perc,totalind in zip(dummy['perc'],dummy['Totalind'])],\
                                    marker=dict(color=color_discrete_sequence[sev])))
            
            
            hist_fig.update_layout(barmode="stack",yaxis_range=[0,110])
            hist_fig.update_yaxes(title="% of vulnerabilities")
            hist_fig.update_layout(title='Vulnerabilities Severity')
            

            
            hist_chart=dcc.Graph(figure=hist_fig)
            

            
            


        else:
            vul_data_table=''
            wordcloud_plot=''
            pie_chart=''
            hist_chart=''

        
        if len(tools_found)>0:
            final_msg='Tools Found: '+','.join(tools_found)
        else:
            final_msg="No tools were found."



        

        
        return final_msg ,vul_data_table,wordcloud_plot,pie_chart,hist_chart
    return '','','','',''
if __name__ == '__main__':
    app.run(debug=True)

