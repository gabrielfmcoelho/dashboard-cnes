import dash
import dash.dcc as dcc
import dash.html as html
from dash.dependencies import Input, Output, ClientsideFunction

import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import datetime
from datetime import datetime as dt
import geopandas as gpd
from statistics import mean

import pathlib

import database.bigqueryconn as bqconn
from database import dfcontroller

TITLE = "Análise da Saude no Piauí"

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title=TITLE,
)

server = app.server
app.config.suppress_callback_exceptions = False

BASE_PATH = pathlib.Path(__file__).parent.resolve()

conn = bqconn.BigQueryConn('etl-cnes-a7a20431c4d7.json')
df_saude = conn.get_data_df('query_saude_score.txt')
controller = dfcontroller.DfController()
controller.update_df(df_saude)

INTRO_INFO = {"title": "Análise da Saúde no Piauí", "subtitle":"Conheça a Dashboard de Análise da Saúde no Piauí", "description": "Explore os dados de saúde e conheça mais sobre a situação em cada município."}

def description_card(dict_intro_info):
    """

    :return: Uma DIV que contem um titulo para a dashboard e uma breve descrição.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5(dict_intro_info["title"], className="card-title"),
            html.H3(dict_intro_info["subtitle"], className="card-subtitle"),
            html.Div(
                id="intro",
                children=dict_intro_info["description"],
            ),
        ],
    )

CONTROL_INFO = {"title_dropdown": "Selecione Município", "title_datepicker":"Selecione Intervalo de Tempo", "title_multidropdown": "Selecione Variáveis Avaliadas", "title_dropdown_2":"Selecione Tema do Mapa"}

lista_municipios = df_saude['Municipio'].unique().tolist()
lista_municipios.sort()
lista_municipios_c_todos = lista_municipios.copy()
lista_municipios_c_todos.append('Todos os Municípios')
lista_col_numericas = df_saude.select_dtypes(include=np.number).columns.tolist()
lista_col_numericas.remove('CO_MUNICIPIO_GESTOR')
lista_col = df_saude.columns.tolist()

CONTROL_DATA = {
    "dropdown":lista_municipios_c_todos,
    "dropdown_2":lista_col_numericas,
    "datepicker":{
        "start_date":dt(2022, 1, 1),
        "end_date":dt(2022, 12, 31),
        "min_date_allowed":dt(2018, 1, 1),
        "max_date_allowed":dt(2023, 12, 31),
        "initial_visible_month":dt(2022, 1, 1),
        "disabled":True,
    },
    "multidropdown":lista_col_numericas,
    }

def generate_control_card(dict_control_info, **control_data):
    """

    :return: Uma DIV que contem os controles da dashboard.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P(dict_control_info["title_dropdown"], className="control-card-title"),
            dcc.Dropdown(
                id="dropdown-select",
                options=[{"label": i, "value": i} for i in control_data["dropdown"]],
                value=control_data["dropdown"][-1],                
            ),
            html.Br(),
            html.P(dict_control_info["title_dropdown_2"], className="control-card-title"),
            dcc.Dropdown(
                id="dropdown-select-2",
                options=[{"label": i, "value": i} for i in control_data["dropdown_2"]],
                value=control_data["dropdown_2"][-1],
            ),
            html.Br(),
            html.P(dict_control_info["title_datepicker"], className="control-card-title"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=control_data["datepicker"]["start_date"],
                end_date=control_data["datepicker"]["end_date"],
                min_date_allowed=control_data["datepicker"]["min_date_allowed"],
                max_date_allowed=control_data["datepicker"]["max_date_allowed"],
                initial_visible_month=control_data["datepicker"]["initial_visible_month"],
                disabled=control_data["datepicker"]["disabled"],
            ),
            html.Br(),
            html.Br(),
            html.P(dict_control_info["title_multidropdown"], className="control-card-title"),
            dcc.Dropdown(
                id="multidropdown-select",
                options=[{"label": i, "value": i} for i in control_data["multidropdown"]],
                value=control_data["multidropdown"][:],
                multi=True,
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Resetar", n_clicks=0),
            ),
            html.Br(),
            html.Br(),
        ],
    )

PATH_GEOJSON = './municipios.geojson'

def grafico_mapa(df_i, tema, *zoom):
    """ Função para Gerar o Gráfico do Mapa"""
    muni = gpd.read_file(PATH_GEOJSON)
    df = df_i.copy()
    # Retirar o caractere mais a direita do código do município
    muni['code_muni'] = muni['code_muni'].astype(int)
    muni['code_muni'] = muni['code_muni'].astype(str)
    muni['code_muni'] = muni['code_muni'].str[:-1]
    muni['code_muni'] = muni['code_muni'].astype(float)
    all_muni = muni
    df['CO_MUNICIPIO_GESTOR'] = df['CO_MUNICIPIO_GESTOR'].astype(float)
    all_muni = all_muni.loc[all_muni['code_muni'].isin(list(df['CO_MUNICIPIO_GESTOR']))]
    all_muni = all_muni.rename(columns={'code_muni': 'CO_MUNICIPIO_GESTOR'})
    all_muni = pd.merge(all_muni, df, how='left', on = 'CO_MUNICIPIO_GESTOR')
    all_muni.index = list(all_muni['name_muni'])
    fig = px.choropleth_mapbox(all_muni,
        geojson=all_muni.geometry,
        locations=all_muni.index,
        color=tema,
        opacity=0.5,
        center={"lat": (((mean(list(all_muni.geometry.bounds.maxy))-mean(list(all_muni.geometry.bounds.miny)))/2)+mean(list(all_muni.geometry.bounds.miny)))
        , "lon": (((mean(list(all_muni.geometry.bounds.maxx))-mean(list(all_muni.geometry.bounds.minx)))/2)+mean(list(all_muni.geometry.bounds.minx)))},
        labels={'index':'name_muni'},
        mapbox_style="open-street-map",
        zoom=zoom[0] if zoom else 5.2,
    )
    fig.update_layout(
        dragmode=False,
        margin=dict(l=1, r=1, t=1, b=1),
        )
    return fig



# Função para gerar heatmap de correlação de variáveis
def grafico_correlacao(df):
    """ Função para gerar heatmap de correlação de variáveis"""
    fig = go.Figure(data=go.Heatmap(
        z=df.corr(),
        x=df.columns,
        y=df.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        colorbar=dict(
            title="Correlação",
            titleside="top",
            tickmode="array",
            tickvals=[-1, 0, 1],
            ticktext=["-1", "0", "1"],
            ticks="outside"
        ),
    ))
    fig.update_layout(
        margin=dict(l=1, r=1, t=1, b=1),
    )
    return fig

def grafico_barras(df, tema):
    """ Função para gerar gráfico de barras"""
    fig = px.bar(df, x=df['Municipio'], y=tema, color=tema, color_continuous_scale='RdBu')
    fig.update_layout(
        margin=dict(l=1, r=1, t=1, b=1),
    )
    return fig

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H4("IPS DATALAB", id="banner-title"),
            ],
        ),
        # Coluna da esquerda
        html.Div(
            id="left-column",
            className="four columns",
            children=[
                description_card(INTRO_INFO),
                generate_control_card(CONTROL_INFO, **CONTROL_DATA),
            ] + [
                html.Div(
                    children=["initial child"], id="output-clientside", style={"display": "none"},
                    ),
            ],
        ),
        # Coluna da direita
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.Br(),
                html.Br(),
                # Mapa
                html.Div(
                    id="",
                    children=[
                        html.B("Mapa do Estado"),
                        html.Hr(),
                        dcc.Graph(
                            id="mapa",
                            figure=grafico_mapa(df_saude, "score_final", 5.2),
                        ),
                    ],
                ),
                html.Br(),
                html.Br(),
                # Indicadores
                html.Div(
                    id="",
                    children=[
                        html.B("Indicadores"),
                        html.Hr(),
                        html.Div(
                            id="", className="row",
                            children=[
                                html.Div(
                                    id="",
                                    className="six columns",
                                    children=[
                                        html.Div(
                                            id="",
                                            children=[
                                                html.B("Score Final"),
                                                html.Hr(),
                                                html.Div(
                                                    id="Texto do Score Final",
                                                    children=[
                                                        html.P("Carregando..."),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="",
                                    className="six columns",
                                    children=[
                                        html.Div(
                                            id="",
                                            children=[
                                                html.B("Ranking Estadual"),
                                                html.Hr(),
                                                html.Div(
                                                    id="Texto do Ranking Estadual",
                                                    children=[
                                                        html.P("Carregando..."),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Br(),
                html.Br(),
                # Gráfico de Barras de Municipios
                html.Div(
                    id="",
                    children=[
                        html.B("Ranking Municipal"),
                        html.Hr(),
                        dcc.Graph(
                            id="barras_municipios",
                            figure=grafico_barras(df_saude.sort_values(by=['score_final'], ascending=False), "score_final"),
                        ),
                    ],
                ),
                html.Br(),
                html.Br(),
                # Grafico de Correlação de Variáveis
                html.Div(
                    id="",
                    children=[
                        html.B("Correlação de Variáveis"),
                        html.Hr(),
                        dcc.Graph(
                            id="heatmap",
                            figure=grafico_correlacao(df_saude[[col for col in df_saude.columns if col in lista_col_numericas]]),
                        ),
                    ],
                ),
                html.Br(),
                html.Br(),
            ],
        ),
    ],
)

@app.callback(Output('mapa', 'figure'),
              [Input('dropdown-select', 'value'),
               Input('dropdown-select-2', 'value'),
               Input('mapa', 'clickData')])
def update_map(selected_municipio, selected_tema):
    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df = df_saude
        zoom = 5.2
    elif selected_municipio in lista_municipios:
        filtered_df = df_saude.loc[df_saude['Municipio'] == selected_municipio]
        zoom = 8.2
    if (selected_tema is None):
        selected_tema = 'score_final'
    new_map = grafico_mapa(filtered_df, selected_tema, zoom)
    return new_map

@app.callback([Output('Texto do Score Final', 'children')],
              [Input('dropdown-select', 'value')])
def update_rank(selected_municipio):
    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        new_score = [html.P("Indisponível")]
    elif selected_municipio in lista_municipios:
        filtered_df = df_saude.loc[df_saude['Municipio'] == selected_municipio]
        new_score = [html.P(str(filtered_df['score_final'].values[0]))]
    return new_score

@app.callback([Output('Texto do Ranking Estadual', 'children')],
                [Input('dropdown-select', 'value')])
def update_rank(selected_municipio):
    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        rank = [html.P("Indisponível")]
    elif selected_municipio in lista_municipios:
        filtered_df = df_saude.sort_values(by=['score_final'], ascending=False).reset_index(drop=True)
        rank = [html.P(str(filtered_df.loc[filtered_df['Municipio'] == selected_municipio].index[0]+1) + 'º de ' + str(filtered_df.shape[0]))]
    return rank

#Callback from multidropdown to update heatmap
@app.callback(Output('heatmap', 'figure'),
            [Input('multidropdown-select', 'value'),])
def update_heatmap(selected_vars):
    if selected_vars is None:
        selected_vars = lista_col_numericas
    new_heatmap = grafico_correlacao(df_saude[selected_vars])
    return new_heatmap

#Callback from dropdown2 to update bar chart
@app.callback(Output('barras_municipios', 'figure'),
            [Input('dropdown-select-2', 'value'),])
def update_barras(selected_tema):
    if selected_tema is None:
        selected_tema = 'score_final'
    new_barras = grafico_barras(df_saude.sort_values(by=[selected_tema], ascending=False), selected_tema)
    return new_barras



if __name__ == "__main__":
    app.run_server(debug=True)