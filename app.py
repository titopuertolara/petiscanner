from dash_extensions.enrich import Trigger, FileSystemCache

import time
import base64
import datetime
import io
from dash import Dash, html, Input, Output, callback_context, dcc, ctx, State
import pandas as pd
from pypdf import PdfReader
from utils import *
from tqdm import tqdm
import plotly.graph_objects as go 
import plotly.express as px
import uuid
from src.layout import serve_layout
from src.page_texts import text_pages

# Function to generate the layout with a unique session ID

def generate_layout():
    session_id = str(uuid.uuid4())
    return serve_layout(session_id)

# Initialize the Dash app

app = Dash(__name__ , suppress_callback_exceptions=True)
app.title = "OSV scanner"

# Initialize file system caches

fsc = FileSystemCache("Cache/cache_dir")
fsc1 = FileSystemCache("Cache/cache_tools")

# Load reference tools data from a CSV file
ref_tools = pd.read_csv('reference_tools.csv')

# Convert the 'software' column to a list
tools_list = ref_tools['software'].to_list()

# Load stopwords from a text file
with open("stopwords-en.txt", "r") as sfile:
    stopwords = sfile.readlines()
# Remove newline characters from stopwords
stopwords = [i.replace('\n', '') for i in stopwords]

# Define colors for pie chart
colors_piechart = px.colors.qualitative.D3

# Load page texts function
page_texts = text_pages()

# Set the layout of the app
app.layout = generate_layout  



# This callback is used to check the progress of the tools scanning process


@app.callback(Output('tool-div','children'),
              [Input('check-bar-interval','n_intervals'),
              Input('session-id','data')])
def check_tool_progress(n,session_id):
    
    value = fsc1.get(f'{session_id[0]}_tools')
    if value is None:
        value = 'idle'
    return value

# this callback is used to check the progress of the pdf loading process

@app.callback(Output('loadbar', 'value'), 
             [Input('check-bar-interval','n_intervals'),
              Input('session-id', 'data')])
def check_loadbar(n,session_id):
    
    value = fsc.get(f'{session_id[0]}_progress')
    if value is None:
        value = '0'
    return value
    
# Callbacks


# this callback is the pdf loading process, all the pdf contents are loaded to a dcc.Store

@app.callback(Output('output-data-upload', 'children'),
              Output('pdf_content', 'data'),
                            
            [Input('upload-section', 'contents'),
             Input('upload-section', 'filename'),
             Input('session-id', 'data')
             ])
def get_data(contents, filename, session_id):

    print(filename)

    #print(contents)
    #in case to save pdf file into assets
    #with open(f'assets/{filename[0]}','wb') as pdfile:
    #    pdfile.write(base64.b64decode(encoded_content))
    #loader = PyPDFLoader(f'assets/{filename[0]}')
    #docs=loader.load_and_split()    
    
    try:
        fsc.set(f"{session_id[0]}_progress", '0')
        encoded_content = contents.split(',')[1]
        pdf_buffer = io.BytesIO(base64.b64decode(encoded_content))
        reader = PdfReader(pdf_buffer)
        total_pages = reader.get_num_pages()
        print(f'Searching in {total_pages}')
        big_str = ''
        print('Loading pdf file')
        for n in tqdm(range(total_pages)):
            #print(f'page {n+1}')
            page = reader.pages[n]
            page_text = page.extract_text()
            big_str += ' '+page_text.lower()
            progress = n*100/total_pages
            
            fsc.set(f"{session_id[0]}_progress", f'{progress}')
            
        fsc.set(f"{session_id[0]}_progress", '100')
        fsc1.set(f'{session_id[0]}_tools', f"Document ready.")
        print('loaded')
        return filename, [big_str]
    except Exception as e:
        print(e)
 

    return '',[]

# this callback is used to change the style of the buttons
@app.callback(
    [   Output("descriptions-div", "children"),
        Output("upload-section", "style"),
        Output("loadbar", "style"),
        Output("scanner-button", "style"),
        Output("btn-upload", "style"),
        Output("btn-how", "style"),
        Output("btn-who", "style"),
        Output("btn-info", "style"),
        Output("output-data-upload", "style"),
        Output("msg-div", "style"),
        Output("vulnerabilities-div", "style"),
        Output("wordcloud-image", "style"),
        Output("pie-chart-div", "style"),
        Output("normalized-barplot-div", "style")
        
    ],
    [Input("btn-upload", "n_clicks"), Input("btn-how", "n_clicks"),
     Input("btn-who", "n_clicks"), Input("btn-info", "n_clicks")],
)
def handle_button_click(n_upload, n_how, n_who, n_info):
    ctx = callback_context
    if not ctx.triggered:
        return page_texts["upload document"],{"display": "none"}, {"display": "none"}, {"display": "none"}, *([{
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
        }] * 4), *([{"display": "none"}] * 6)

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

    button_style={
            "backgroundColor": "#FF5A36",
            "color": "#FFFFFF",
            "borderRadius": "10px",
            "padding": "1rem",
            "fontWeight": "bold",
            "cursor": "pointer",
            "width": "100%",
            "boxSizing": "border-box",
            "marginBottom": "2rem",
            "border": "2px solid #FFFFFF",
            "fontSize": "1.2rem",
            "transition": "background-color 0.3s, color 0.3s",
            "display": "none",
    }

    # Logic for each button
    text=""
    
    if button_id == "btn-upload":
        button_style["display"] = "block"
        
        return page_texts["upload document"], {"display": "block"}, {"display": "block"}, button_style, selected_style, default_style, default_style, default_style, *([{"display": "block"}] * 6)
    elif button_id == "btn-how":
        
        return page_texts["How does it work"], {"display": "none"}, {"display": "none"}, button_style, default_style, selected_style, default_style, default_style, *([{"display": "none"}] * 6)
    elif button_id == "btn-who":
        return page_texts["Who is it for"], {"display": "none"}, {"display": "none"}, button_style, default_style, default_style, selected_style, default_style, *([{"display": "none"}] * 6)
    elif button_id == "btn-info":
        return page_texts["More info"], {"display": "none"}, {"display": "none"}, button_style, default_style, default_style, default_style, selected_style, *([{"display": "none"}] * 6)
    else:
        return text, {"display": "none"}, {"display": "none"}, button_style,  default_style, default_style, default_style, selected_style, *([{"display": "none"}] * 6)
    


# this callback is used to scan the document and find tools and vulnerabilities

@app.callback(Output('msg-div','children'),
              Output('vulnerabilities-div','children'),
              Output('wordcloud-image','children'),
              Output('pie-chart-div','children'),
              Output('normalized-barplot-div','children'),
              [Input('scanner-button','n_clicks'),
               State('pdf_content','data'),
               Input('session-id','data')])
def scan_doc(nclicks, big_str, session_id):
    fsc1.set(f'{session_id[0]}_tools',"idle")
    if ctx.triggered_id == 'scanner-button':
        progress_value = fsc.get(f"{session_id[0]}_progress")
        if float(progress_value)<100:
            fsc1.set(f'{session_id[0]}_tools', f"Document has not been loaded yet.")
            return '', '', '', '', ''
    
        print('looking for tools')
        tools_found = []
        for word in tqdm(tools_list):
            status = word_finder(word, big_str[0])
            if status:
                tools_found.append(word)
        tools_found = list(set(tools_found))
        print(tools_found)
        
        vulnerabilities_list = []
        
        true_counts = 0
        for k ,tool in enumerate(tools_found):
            fsc1.set(f'{session_id[0]}_tools',f'Querying {tool} ({k+1}/{len(tools_found)})..')
            df,msg = get_vulnerability_dataframe(tool.strip(),lang='en')
            time.sleep(6)
            print(tool, msg)
            if df.shape[0]>0:
                vulnerabilities_list.append(df)
                true_counts += 1
            if not msg:
                fsc1.set(f'{session_id[0]}_tools',f"There's an issue scanning {tool} from NVD (please search directly from main website)")
                time.sleep(1)
                
        if len(tools_found)>0:
            efficency = round(100*true_counts/len(tools_found),1)
            if efficency == 0:
                fsc1.set(f'{session_id[0]}_tools', f"API is unstable or there are not vulnerabilities for these tools in the last month, please try again later.")

            elif efficency < 50:
                fsc1.set(f'{session_id[0]}_tools', f"Just {efficency}% of requests were succesful, wait 2 minutes and try scanning again.")
            else: 
                fsc1.set(f'{session_id[0]}_tools', f"Finished with {efficency}% of succesful requests.")
        else:
            fsc1.set(f'{session_id[0]}_tools', "Not tools found inside this document.")

        if len(vulnerabilities_list)>0:
           
            all_vulnerabilities_df = pd.concat(vulnerabilities_list, ignore_index=True)
            all_vulnerabilities_df = all_vulnerabilities_df.rename(columns={'Fecha': 'Date', 'Autor': 'Contributor', \
                                                                         'Vulnerabilidad': 'Vulnerability', \
                                                                         'Herramienta': 'Tool', \
                                                                         'Severidad': 'Severity'})
            vul_data_table = create_datatable(all_vulnerabilities_df)
            wordcloud_text = ' '.join(all_vulnerabilities_df['Vulnerability'].to_list()).lower()
            
            wordcloud_text = remove_stopwords(wordcloud_text,stopwords)
            wordcloud_image = get_wordcloud(wordcloud_text)
            wordcloud_plot = html.Img(src=wordcloud_image)
            print('pie chart')
            tools_count = pd.DataFrame(all_vulnerabilities_df['Tool'].value_counts())
            pie_fig = go.Figure()
            pie_fig.add_trace(go.Pie(labels=tools_count.index, values=tools_count['count'].values))
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
            pie_chart = dcc.Graph(figure=pie_fig)

            # severity plot
            
            severity_df = all_vulnerabilities_df.copy()
            severity_df['Severity'] = severity_df['Severity'].fillna('NOT SPECIFIED')
            severity_df = severity_df[severity_df['Tool'].isin(tools_found)]
                      
            a = severity_df.groupby(['Tool', 'Severity']).count()[['Id']].reset_index()
            a = a.rename(columns={'Id': 'Totalind'})
            b = a.groupby(['Tool']).sum()[['Totalind']].reset_index()
            b = b.rename(columns={'Totalind': 'Total'})
            a = a.merge(b, how='inner', on='Tool')
            a['perc'] = 100*a['Totalind']/a['Total']
            a['perc'] = a['perc'].apply(lambda x: round(x, 1))

            color_discrete_sequence = {'CRITICAL': '#FF6347', 'HIGH': '#FFA500', 'LOW': '#87CEEB', 'MEDIUM': '#005B96', 'NOT SPECIFIED': 'gray'}
            hist_fig = go.Figure()
            for sev in a['Severity'].unique():
                dummy = a[a['Severity'] == sev]

                hist_fig.add_trace(go.Bar(x=dummy['Tool'],\
                                    y=dummy['perc'],\
                                    name=sev, text=[f'{perc}% ({totalind})' for perc,totalind in zip(dummy['perc'],dummy['Totalind'])],\
                                    marker=dict(color=color_discrete_sequence[sev])))            
            
            hist_fig.update_layout(barmode="stack",yaxis_range=[0,110])
            hist_fig.update_yaxes(title="% of vulnerabilities")
            hist_fig.update_layout(title='Vulnerabilities Severity')
            
            hist_chart = dcc.Graph(figure=hist_fig)      

        else:
            vul_data_table = ''
            wordcloud_plot = ''
            pie_chart = ''
            hist_chart = ''
        
        if len(tools_found) > 0:
            final_msg = 'Tools Found: '+','.join(tools_found)
        else:
            final_msg = "No tools were found."



        

        
        return final_msg ,vul_data_table,wordcloud_plot,pie_chart,hist_chart
    return '', '', '', '', ''

if __name__ == "__main__":
    app.run_server(debug=True)
    
    #app.run(host="155.138.215.28",debug=False)
