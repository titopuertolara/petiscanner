from dash import Dash, html, Input, Output, callback_context,dcc
from dash_extensions.enrich import Trigger, FileSystemCache
import uuid

# Layout

def serve_layout(session_id):

    
    

    fsc = FileSystemCache(f"Cache/{session_id}_cache_dir")
    fsc1= FileSystemCache(f"Cache/{session_id}_cache_tools")
    fsc.set(f"{session_id}_progress", '0')
    fsc1.set(f"{session_id}_tools",'idle')
    layout =  html.Div(
        style={
            "fontFamily": "Arial, sans-serif",
            "backgroundColor": "#FF5A36",  # Background color
            "color": "#FFFFFF",  # White text
            "padding": "2rem",
            "textAlign": "center",
        },
        children=[
            html.Div(
                style={
                    "backgroundColor": "#FFFFFF",  # White container
                    "color": "#FF5A36",  # Text color
                    "borderRadius": "10px",
                    "padding": "2rem",
                    "maxWidth": "1200px",  # Wider box
                    "margin": "0 auto",
                },
                children=[
                    # Header with FAQ and GitHub link
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "marginBottom": "1rem",
                        },
                        children=[
                            html.Div("FAQ", style={"fontSize": "1.2rem", "fontWeight": "bold"}),
                            html.A(
                                "Join the GitHub community",
                                href="https://github.com/titopuertolara/petiscanner",
                                target="_blank",
                                style={
                                    "fontSize": "1.2rem",
                                    "fontWeight": "bold",
                                    "color": "#FF5A36",
                                    "textDecoration": "none",
                                },
                            ),
                        ],
                    ),
                    html.H1(
                        "OSV Scanner",
                        style={
                            "fontSize": "4rem",  # Larger font size
                            "marginBottom": "1rem",
                            "fontWeight": "bold",
                            "textAlign": "left",  # Align the title to the left
                        },
                    ),
                    html.P(
                        id="descriptions-div",
                        children=[
                            "The OSV Scanner is a simple online tool that helps identify vulnerabilities in "
                            "documents like Policy Papers, contracts, and IT plans. Linked to the US National "
                            "Vulnerability Database, it scans PDF documents to flag potential risks. Open-source "
                            "and non-intrusive, the OSV Scanner does not require system access, is easy to deploy "
                            "and does not collect user data. Upload your PDF to get started."
                        ],
                        style={"fontSize": "1rem", "lineHeight": "1.5rem", "marginBottom": "2rem"},
                    ),
                    # Buttons
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(4, 1fr)",
                            "gap": "1rem",
                            "marginBottom": "2rem",
                            "width": "100%",  # Ensure full width of container
                        },
                        children=[
                            html.Div(
                                id="btn-upload",
                                n_clicks=0,
                                children="Upload your document",
                                style={
                                    "backgroundColor": "#FFFFFF",
                                    "color": "#FF5A36",
                                    "borderRadius": "10px",
                                    "padding": "1.5rem",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "border": "2px solid #FF5A36",
                                    "fontSize": "1.2rem",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                },
                            ),
                            html.Div(
                                id="btn-how",
                                n_clicks=0,
                                children="How does it work?",
                                style={
                                    "backgroundColor": "#FFFFFF",
                                    "color": "#FF5A36",
                                    "borderRadius": "10px",
                                    "padding": "1.5rem",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "border": "2px solid #FF5A36",
                                    "fontSize": "1.2rem",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                },
                            ),
                            html.Div(
                                id="btn-who",
                                n_clicks=0,
                                children="Who is it for?",
                                style={
                                    "backgroundColor": "#FFFFFF",
                                    "color": "#FF5A36",
                                    "borderRadius": "10px",
                                    "padding": "1.5rem",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "border": "2px solid #FF5A36",
                                    "fontSize": "1.2rem",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                },
                            ),
                            html.Div(
                                id="btn-info",
                                n_clicks=0,
                                children="More info",
                                style={
                                    "backgroundColor": "#FFFFFF",
                                    "color": "#FF5A36",
                                    "borderRadius": "10px",
                                    "padding": "1.5rem",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "border": "2px solid #FF5A36",
                                    "fontSize": "1.2rem",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                },
                            ),
                        ],
                    ),
                    # Upload Section
                    dcc.Upload(
                        id='upload-section',
                        children=html.Div(
                            [
                                "Drag and Drop or ",
                                html.A("Select Files", style={"color": "#FF5A36", "textDecoration": "underline"})
                            ],
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "marginBottom": "2rem",
                                "borderColor": "#FF5A36",
                                "color": "#FF5A36",
                                "cursor": "pointer",
                            },
                        ),
                        multiple=False,
                        accept=".pdf",
                    ),
                    html.Button("Scan Document", id='scanner-button', style={
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
                    }),
                    html.Progress(id='loadbar', max=100),
                    html.Div(id='output-data-upload'),
                    html.Div(id='msg-div'),
                    html.Div(id='tool-div'),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "1rem",
                            "marginTop": "2rem"
                        },
                        children=[
                            html.Div(id='wordcloud-image', style={"backgroundColor": "#FFFFFF", "padding": "1rem", "borderRadius": "10px", "flex": "1"}),
                            html.Div(id='pie-chart-div', style={"backgroundColor": "#FFFFFF", "padding": "1rem", "borderRadius": "10px", "flex": "1", "width": "100%"})
                            
                        ]
                    ),
                    html.Div(
                        style={
                            "marginTop": "1rem"
                        },
                        children=[
                            html.Div(id='normalized-barplot-div', style={"backgroundColor": "#FFFFFF", "padding": "1rem", "borderRadius": "10px", "marginBottom": "1rem"}),
                            html.Div(id='vulnerabilities-div', style={"backgroundColor": "#FFFFFF", "padding": "1rem", "borderRadius": "10px"})
                        ] 
                    )

                ],
            ),
            html.Div(
                "powered by the Edgelands Institute",
                style={"marginTop": "2rem", "fontSize": "0.9rem", "color": "#FFFFFF"},
            ),
            dcc.Store(id='session-id',data=[session_id]),
            dcc.Store(id='pdf_content'),            
            html.Div(id='session-id-output-2'),            
            dcc.Interval(id='check-bar-interval', interval=500, n_intervals=0),
        ],
    )

    return layout

