from dash import Dash, html, Input, Output, callback_context

app = Dash(__name__)

# Layout
app.layout = html.Div(
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
                    (
                        "The OSV Scanner is a simple online tool that helps identify vulnerabilities in "
                        "documents like Policy Papers, contracts, and IT plans. Linked to the US National "
                        "Vulnerability Database, it scans PDF documents to flag potential risks. Open-source "
                        "and non-intrusive, the OSV Scanner does not require system access, is easy to deploy "
                        "and does not collect user data. Upload your PDF to get started."
                    ),
                    style={"fontSize": "1rem", "lineHeight": "1.5rem", "marginBottom": "2rem"},
                ),
                # Buttons
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "1rem",
                        "marginBottom": "2rem",
                    },
                    children=[
                        html.Div(
                            id="btn-upload",
                            n_clicks=0,
                            children="Upload your document",
                            style={
                                "backgroundColor": "#FFFFFF",
                                "color": "#FF5A36",
                                "borderRadius": "5px",
                                "padding": "1rem",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "cursor": "pointer",
                                "border": "2px solid #FF5A36",
                                "fontSize": "1rem",  # Set same font size
                                "maxWidth": "200px",  # Set consistent width
                                "margin": "0 auto",
                            },
                        ),
                        html.Div(
                            id="btn-how",
                            n_clicks=0,
                            children="How does it work?",
                            style={
                                "backgroundColor": "#FFFFFF",
                                "color": "#FF5A36",
                                "borderRadius": "5px",
                                "padding": "1rem",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "cursor": "pointer",
                                "border": "2px solid #FF5A36",
                                "fontSize": "1rem",  # Set same font size
                                "maxWidth": "200px",  # Set consistent width
                                "margin": "0 auto",
                            },
                        ),
                        html.Div(
                            id="btn-who",
                            n_clicks=0,
                            children="Who is it for?",
                            style={
                                "backgroundColor": "#FFFFFF",
                                "color": "#FF5A36",
                                "borderRadius": "5px",
                                "padding": "1rem",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "cursor": "pointer",
                                "border": "2px solid #FF5A36",
                                "fontSize": "1rem",  # Set same font size
                                "maxWidth": "200px",  # Set consistent width
                                "margin": "0 auto",
                            },
                        ),
                        html.Div(
                            id="btn-info",
                            n_clicks=0,
                            children="More info",
                            style={
                                "backgroundColor": "#FFFFFF",
                                "color": "#FF5A36",
                                "borderRadius": "5px",
                                "padding": "1rem",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "cursor": "pointer",
                                "border": "2px solid #FF5A36",
                                "fontSize": "1rem",  # Set same font size
                                "maxWidth": "200px",  # Set consistent width
                                "margin": "0 auto",
                            },
                        ),
                    ],
                ),
                # Upload Section
                html.Div(
                    id="upload-section",
                    style={"display": "none"},
                    children=html.Div(
                        "Upload the document here",
                        style={
                            "backgroundColor": "#FF5A36",
                            "color": "#FFFFFF",
                            "borderRadius": "5px",
                            "padding": "1rem",
                            "fontWeight": "bold",
                            "cursor": "pointer",
                            "maxWidth": "200px",
                            "margin": "0 auto",
                        },
                    ),
                ),
            ],
        ),
        html.Div(
            "powered by the Edgelands Institute",
            style={"marginTop": "2rem", "fontSize": "0.9rem", "color": "#FFFFFF"},
        ),
    ],
)

# Callbacks
@app.callback(
    [
        Output("upload-section", "style"),
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
        return {"display": "none"}, *([{"backgroundColor": "#FFFFFF", "color": "#FF5A36", "border": "2px solid #FF5A36"}] * 4)

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Default styles for all buttons
    default_style = {"backgroundColor": "#FFFFFF", "color": "#FF5A36", "border": "2px solid #FF5A36"}
    selected_style = {"backgroundColor": "#FF5A36", "color": "#FFFFFF", "border": "2px solid #FF5A36"}

    # Logic for each button
    if button_id == "btn-upload":
        return {"display": "block"}, selected_style, default_style, default_style, default_style
    elif button_id == "btn-how":
        return {"display": "none"}, default_style, selected_style, default_style, default_style
    elif button_id == "btn-who":
        return {"display": "none"}, default_style, default_style, selected_style, default_style
    elif button_id == "btn-info":
        return {"display": "none"}, default_style, default_style, default_style, selected_style
    else:
        return {"display": "none"}, *([default_style] * 4)


if __name__ == "__main__":
    app.run_server(debug=True)
