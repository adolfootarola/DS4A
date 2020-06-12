

import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from dash.dependencies import Input, Output

app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])

df=pd.read_csv('data.csv')
df['created']=pd.to_datetime(df['created'])
df['month_created']=df.created.dt.strftime(' %Y-%m')
best5_1=df.groupby(['mesoregion'])['sla_compliant'].mean().sort_values(ascending=False).reset_index()
best5_2=best5_1[best5_1.sla_compliant<1]
best5=best5_1[best5_1.sla_compliant<1].head(5)#Some values were omitted
best5_1 = best5_2[best5_2.sla_compliant>0.4]
worst5=df.groupby(['mesoregion'])['sla_compliant'].mean().sort_values(ascending=True).reset_index()
worst5=worst5[worst5.sla_compliant>0.4].head(5)#Some values were omitted
#Some values were omitted
best5.sla_compliant,worst5.sla_compliant=round(100*best5.sla_compliant,1),round(100*worst5.sla_compliant,1)

# print(best5_1[:5])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#243442",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

mini_container = {
  'border-radius': '5px',
  'background-color': '#788B9D',
  'color': '#2C3F51',
  'margin': '10px',
  'padding': '15px',
  'position': 'relative',
  'box-shadow': '2px 2px 2px darkgrey'
}

container_display = {
  'display': 'flex'
}

sidebar = html.Div(
    [

        html.Img(id="logo", src=app.get_asset_url("logo01.png"), title="Loggi", width="100%"),
        html.Hr(),
        html.P(
            "Menu", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Stats", href="/page-1", id="page-1-link"),
                dbc.NavLink("Best/Worst", href="/page-2", id="page-2-link"),
                dbc.NavLink("Map", href="/page-3", id="page-3-link"),
                dbc.NavLink("Meet the Team", href="/page-4", id="page-4-link")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(
    [Output(component_id='my_histogram', component_property='figure'),
    Output(component_id='my_gauge', component_property='figure'),
    Output(component_id='my_scatter', component_property='figure'),
    Output(component_id='bsla1', component_property='children'),
    Output(component_id='wsla1', component_property='children')
     ],
    [Input(component_id='select_region', component_property='value')]
)
def update_graph(option_selected):
    #print(option_selected)
    #print(type(option_selected))

    df_hist= df.copy()
    #Histogram filters the outliers, as precalculated
    df_hist = df_hist[(df_hist["mesoregion"] == option_selected)&(~df_hist.is_outlier)]
    df_meso= df_hist[(df_hist["mesoregion"] == option_selected)]
    df_sla_ev=df_meso.groupby(['month_created'])['sla_compliant'].mean().reset_index()

    print(df_meso.head(5))
    print("----")
    print(df_hist.head(5))
    print("----")
    print(df_sla_ev.head(10))
    print("----")
    temp01 = df_hist.groupby(['elapsed_time']).count()
    print(temp01['package_id'].count())
    print("----")
    temp02 = df_hist.groupby(['elapsed_time']).max()
    print(temp02.max())
    print("----")
    print(round(100*df_sla_ev['sla_compliant'].max(),2))

    bsla1 = round(100*df_sla_ev['sla_compliant'].max(),2)
    wsla1 = round(100*df_sla_ev['sla_compliant'].min(),2)

    if len(df_meso)!=0:
        SLA=round(100*len(df_meso[df.sla_compliant==True])/len(df_meso),1)
    else:
        SLA=None

    fig1 = px.histogram(
        data_frame=df_hist,
        x='elapsed_time',
        labels={'elapsed_time': 'Service Time, Minutes','count':'# of Packages delivered'},
        title='# Packages Sent',
        template='xgridoff'
    )

    fig1.update_layout(paper_bgcolor='rgb(120,139,157)', plot_bgcolor='rgba(0,0,0,0)')

    fig2= go.Figure(go.Indicator(
        mode = "gauge+number",
        value = SLA,
        title = {'text': "SLA"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#5052f9'},
            'bar':{'color': "#336699"},
            'steps': [
                {'range': [0, 95], 'color': '#e8e8e8'},
                {'range': [95, 100], 'color': '#336699'}]}
    ))
    fig2.update_layout(paper_bgcolor = 'rgb(120,139,157)', plot_bgcolor='rgba(0,0,0,0)')

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_sla_ev.month_created,
                    y=round(100*df_sla_ev.sla_compliant,2),
                    mode='markers+lines',
                    line = dict(color='#336699', width=3))
                    )
    fig3.update_layout(title_text='SLA Monthly Evolution', paper_bgcolor='rgb(120,139,157)', plot_bgcolor='rgba(0,0,0,0)')

    return fig1,fig2,fig3,bsla1,wsla1


@app.callback(
    [Output(component_id='worst5', component_property='figure'),
    Output(component_id='best5', component_property='figure'),
    Output('best5_1', 'children')
     ],
    [Input(component_id='select_region2', component_property='value')])

def update_graph2(option_selected):

    reds=5*['lightsalmon']
    greens=5*['lightgreen']


    fig4=go.Figure(data=[go.Bar(x=worst5.mesoregion,y=worst5.sla_compliant,marker_color=reds)])
    fig4.update_layout(title_text='Worst 5 Mesoregions', paper_bgcolor='rgb(120,139,157)', plot_bgcolor='rgba(0,0,0,0)')

    fig5=go.Figure(data=[go.Bar(x=best5.mesoregion,y=best5.sla_compliant,marker_color=greens)])
    fig5.update_layout(title_text='Best 5 Mesoregions', paper_bgcolor='rgb(120,139,157)', plot_bgcolor='rgba(0,0,0,0)')

    fig6 = dash_table.DataTable(
        id='best5_1',
        data= best5_1.to_dict('records'),
        columns=[{"name": i, "id": i} for i in best5_1.columns],
        style_header={
            'backgroundColor': 'Black',
            'fontWeight': 'bold'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
            }
        )


    return fig4,fig5, fig6







@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.Div([

            html.H1("Statistics", style={'text-align': 'center'}),

            dbc.Row([
                dbc.Col(html.Div(
                    dcc.Dropdown(id="select_region",
                                 options=[
                                    #{"label":"Americana", "value":"Americana"},
                                    {"label":"Baixada Santista", "value":"Baixada Santista"},
                                    {"label":"Belo Horizonte", "value":"Belo Horizonte"},
                                    {"label":"Brasília","value":"Brasília"},
                                    {"label":"Campinas","value":"Campinas"},
                                    {"label":"Cubatão","value":"Cubatão"},
                                    {"label":"Curitiba","value":"Curitiba"},
                                    {"label":"Florianópolis","value":"Florianópolis"},
                                    {"label":"Fortaleza","value":"Fortaleza"},
                                    {"label":"Goiânia","value":"Goiânia"},
                                    #{"label":"Indaiatuba","value":"Indaiatuba"},
                                    #{"label":"Itaquaquecetuba","value":"Itaquaquecetuba"},
                                    {"label":"Joinville","value":"Joinville"},
                                    #{"label":"Limeira","value":"Limeira"},
                                    #{"label":"Manaus","value":"Mana us"},
                                    {"label":"Piracicaba","value":"Piracicaba"},
                                    {"label":"Porto Alegre","value":"Porto Alegre"},
                                    {"label":"Recife","value":"Recife"},
                                    #{"label":"Ribeirão Pires","value":"Ribeirão Pires"},
                                    {"label":"Ribeirão Preto","value":"Ribeirão Preto"},
                                    {"label":"Rio de Janeiro","value":"Rio de Janeiro"},
                                    {"label":"Salvador","value":"Salvador"},
                                    {"label":"Sorocaba","value":"Sorocaba"},
                                    #{"label":"Suzano","value":"Suzano"},
                                    {"label":"São José do Rio Preto","value":"São José do Rio Preto"},
                                    {"label":"São José dos Campos","value":"São José dos Campos"},
                                    {"label":"São Paulo","value":"São Paulo"},
                                    {"label":"Uberlândia","value":"Uberlândia"},
                                    {"label":"Vitória", "value":"Vitória"}],
                                 multi=False,
                                 value="Rio de Janeiro",
                                 style={'color': "Black", 'background': '#ABBED0'}
                                 )
                ), width=4)
            ],
            justify="start"),


            #html.Div(id='output_container', children=[]),
            html.Br(),
            dbc.Row([
                dbc.Col(
                            [
                                html.Div(
                                    [html.H6(id="bsla"), html.P("Best SLA"),
                                    html.Div(
                                        id="bsla1",
                                        style = {'font-size':'xx-large', 'font-weight': 'bold', 'text-align': 'right'}
                                        )
                                ], style=mini_container)
                            ], width=2),
                dbc.Col([
                                html.Div(
                                    [html.H6(id="wsla"), html.P("Worst SLA"),
                                    html.Div(
                                        id="wsla1",
                                        style = {'font-size':'xx-large', 'font-weight': 'bold', 'text-align': 'right'}
                                        )
                                ], style=mini_container),
                            ], width=2)

                            ],
                            justify="end"

            ),
            dbc.Row([
                dbc.Col(html.Div(dcc.Graph(id='my_histogram',style={'width': 450}))),
                dbc.Col(html.Div(dcc.Graph(id='my_gauge',style={'width': 450}))),
                dbc.Col(html.Div(dcc.Graph(id='my_scatter',style={'width': 450})))
            ],
            justify="center")
            ])
    elif pathname == "/page-2":
        return html.Div([

            html.H1("Best / Worst Mesoregions", style={'text-align': 'center'}),
            dcc.Dropdown(id="select_region2",
                         options=[
                            #{"label":"Americana", "value":"Americana"},
                            {"label":"Baixada Santista", "value":"Baixada Santista"},
                            {"label":"Belo Horizonte", "value":"Belo Horizonte"},
                            {"label":"Brasília","value":"Brasília"},
                            {"label":"Campinas","value":"Campinas"},
                            {"label":"Cubatão","value":"Cubatão"},
                            {"label":"Curitiba","value":"Curitiba"},
                            {"label":"Florianópolis","value":"Florianópolis"},
                            {"label":"Fortaleza","value":"Fortaleza"},
                            {"label":"Goiânia","value":"Goiânia"},
                            #{"label":"Indaiatuba","value":"Indaiatuba"},
                            #{"label":"Itaquaquecetuba","value":"Itaquaquecetuba"},
                            {"label":"Joinville","value":"Joinville"},
                            #{"label":"Limeira","value":"Limeira"},
                            #{"label":"Manaus","value":"Mana us"},
                            {"label":"Piracicaba","value":"Piracicaba"},
                            {"label":"Porto Alegre","value":"Porto Alegre"},
                            {"label":"Recife","value":"Recife"},
                            #{"label":"Ribeirão Pires","value":"Ribeirão Pires"},
                            {"label":"Ribeirão Preto","value":"Ribeirão Preto"},
                            {"label":"Rio de Janeiro","value":"Rio de Janeiro"},
                            {"label":"Salvador","value":"Salvador"},
                            {"label":"Sorocaba","value":"Sorocaba"},
                            #{"label":"Suzano","value":"Suzano"},
                            {"label":"São José do Rio Preto","value":"São José do Rio Preto"},
                            {"label":"São José dos Campos","value":"São José dos Campos"},
                            {"label":"São Paulo","value":"São Paulo"},
                            {"label":"Uberlândia","value":"Uberlândia"},
                            {"label":"Vitória", "value":"Vitória"}],
                         multi=False,
                         value="Rio de Janeiro",
                         style={'width': "40%", 'color': "Black", 'visibility': "hidden"}
                         ),

            dbc.Row([
                dbc.Col(html.Div(dcc.Graph(id='worst5')), width=4) ,
                dbc.Col(html.Div(dcc.Graph(id='best5')), width=4)
            ], justify="around"),
            html.Br(),
            dbc.Row([
                dbc.Col(html.Div(id='best5_1'), width=4)
            ], justify="center")
            ])

    elif pathname == "/page-3":
        return html.Div([
            dbc.Row([
                dbc.Col(html.H1("Map Indicator"), width=4)], justify="center"),
            dbc.Row([
                dbc.Col(html.Iframe(id='map',srcDoc=open('delay_map.html','r').read(),width=600,height=600), width=4)
                ], justify="center")
            ])
    elif pathname == "/page-4":
        return html.Div([
                html.Center(html.H1("Meet the Team")),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.Div(html.Center([html.Img(id="img1", src=app.get_asset_url("photo011.png"), title="Martin Rios"), html.Div("Martín Ríos"), html.Div("Software Engineer")]))),
                    dbc.Col(html.Div(html.Center([html.Img(id="img2", src=app.get_asset_url("photo021.png"), title="German Goñi"), html.Div("Germán Goñi"), html.Div("Industrial Engineer")]))),
                    dbc.Col(html.Div(html.Center([html.Img(id="img3", src=app.get_asset_url("photo031.png"), title="Adolfo Otarola"), html.Div("Adolfo Otárola"), html.Div("Software Engineer")]))),
                    dbc.Col(html.Div(html.Center([html.Img(id="img4", src=app.get_asset_url("photo041.png"), title="David Oliveros"), html.Div("David Oliveros"), html.Div("Software Engineer")]))),
                    dbc.Col(html.Div(html.Center([html.Img(id="img5", src=app.get_asset_url("photo051.png"), title="Andro Lindsay"), html.Div("Andro Lindsay"), html.Div("Industrial Engineer")])))
                ], no_gutters = False),
                html.Br(),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([html.P("Teamwork is the ability to work together toward a common vision. The ability to direct individual accomplishments toward organizational objectives. It is the fuel that allows common people to attain uncommon results.", style={'font-style': 'italic', 'align':'center', 'font-family': 'Georgia, serif'}),
                            html.P("Andrew Carnegie, business magnate and philanthropist", style={'align':'right'})], width=4)
                ],
                justify="end")

                ])
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8888)
