
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback,ctx
import requests
from datetime import datetime,timedelta,date
import pandas as pd
from dash import dash_table
from PIL import Image
from wordcloud import WordCloud,ImageColorGenerator
from io import BytesIO
import base64
import re

def word_finder(word,text):

    idx=text.find(word)
    if idx!=-1:
        return True
    else:
        return False
    
#def get_vulnerability(match_word,date_ini,date_end):
    
    
#    date_string=f"pubStartDate={date_ini}&pubEndDate={date_end}"
#    page_string="startIndex=0"
#    url=f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={match_word}&{page_string}&{date_string}"
    
#    try:
#        res2=requests.get(url).json()
        #print(res2)
#        output=[{'contributor':vulnerability['cve']['sourceIdentifier'],\
#                'description':vulnerability['cve']['descriptions'],\
#                'date':vulnerability['cve']['published']} for vulnerability in res2['vulnerabilities']]
#        msg=True
#    except:
#        output=[]
#        msg=False    
#    return output,msg

def get_vulnerability(match_word,date_ini,date_end):
    
    
    date_string=f"pubStartDate={date_ini}&pubEndDate={date_end}"
    page_string="startIndex=0"
    url=f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={match_word}&{page_string}&{date_string}"
    header={'apiKey':'54e6cdc7-00cc-4b17-937e-8282ab701f29'}
    msg=False
    try:
        res2=requests.get(url,headers=header).json()
        #print(res2)
        output=[]
        for vulnerability in res2['vulnerabilities']:
            #if 
            outdict={}
            vulkeys=vulnerability['cve']['metrics'].keys()


            if len(vulkeys)>0:
                mkey=list(vulnerability['cve']['metrics'].keys())[0]
                severity=vulnerability['cve']['metrics'][mkey][0]['cvssData']['baseSeverity']
            else:
                severity=None
            outdict={
                    'id': vulnerability['cve']['id'],\
                    'contributor':vulnerability['cve']['sourceIdentifier'],\
                    'description':vulnerability['cve']['descriptions'],\
                    'date':vulnerability['cve']['published'],\
                    'severity':severity
                    }
            output.append(outdict)
            

        msg=True
    except:
        output=[]
        msg=False    
    return output,msg



def get_vulnerability_dataframe(keyword,lang='es'):
    today=date.today().isoformat()
    one_month_ago=(date.today() - timedelta(days=30)).isoformat()
    date_ini=one_month_ago+'T00:00:00.000'
    date_end=today+'T00:00:00.000'
    print(f'From {date_ini} to {date_end}')
    vul,msg=get_vulnerability(keyword,date_ini,date_end)
    if len(vul)>0:
        vul=vul[::-1]
        vuln_df=pd.DataFrame()
        for i,v in enumerate(vul):
            for des in v['description']:
                if des['lang']==lang:
                    final_des=des['value']
                    break
                final_des=des['value']
            vuln_df.loc[i,'Id']=v['id']
            vuln_df.loc[i,'Fecha']=v['date']
            vuln_df.loc[i,'Autor']=v['contributor']
            vuln_df.loc[i,'Vulnerabilidad']=final_des
            vuln_df.loc[i,'Severidad']=v['severity']
        vuln_df['Herramienta']=keyword
        return vuln_df,msg
    else:
        return pd.DataFrame(),msg



def create_datatable(df):

    datatable= dash_table.DataTable(
        id='comments-table',
        style_table={'height':'400px','overflowY':'auto','overflowX':'auto','width':'auto'},
        style_header={'backgroundColor': '#393F56','fontWeight': 'bold','color':'white'},
        export_format='xlsx',
        page_size=20,
        style_cell={'textAlign': 'left','font-family': 'Arial,Helvetica,sans-serif',
                    'textOverflow': 'ellipsis',
                    'overflow': 'hidden',
                    'maxWidth': 0
                    },
        row_selectable="single",
        columns=[{'name':i,'id':i} for i in df.columns],
        filter_action="native",
        tooltip_data=[
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in df.to_dict('records')
    ],
        data=df.to_dict('records')

        
    )

    return datatable

def get_wordcloud(text):
    wordcloud = WordCloud(background_color="white",colormap='Oranges',width=640,height=480).generate(text)
    img=wordcloud.to_image()
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_object='data:image/png;base64,{}'.format(base64.b64encode(img_bytes.getvalue()).decode())
    return img_object

def remove_stopwords(main_text,stopwords):
    main_text = re.sub(r'[^\w\s]', '', main_text)
    words_list=main_text.split()
    words_list=[i.strip() for i in words_list]
    return ' '.join([i for i in words_list if i not in stopwords ])
    
    


        
        




