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
import os

import pathlib

import database.bigqueryconn as bqconn
from database import dfcontroller

from scoreTreatment import score_compile

TITLE = "Análise da Saude no Piauí"

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title=TITLE,
)

server = app.server
app.config.suppress_callback_exceptions = False

BASE_PATH = pathlib.Path(__file__).parent.resolve()

def get_data_from_bigquery():
    print('executou 1 puxada')
    conn = bqconn.BigQueryConn('etl-cnes-a7a20431c4d7.json')
    df_saude = conn.get_data_df('query_saude_score.txt')
    df_saude = df_saude.sort_values(by=['Municipio'], ascending=True)
    df_saude.to_csv("df_saude.csv")
    return df_saude

# Verify is df_saude is in directory
list_files = os.listdir()
if "df_saude.csv" in list_files:
    df_saude = pd.read_csv("df_saude.csv")
else:
    df_saude = get_data_from_bigquery()

df_score = score_compile(df_saude)
df_score.sort_values(by=['score_final'], ascending=False)

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

CONTROL_INFO = {"title_dropdown": "Selecione Município", "title_checkbox":"Deseja Desconsiderar a Capital ?", "title_multidropdown": "Selecione a Pagina da Tabela", "title_dropdown_2":"Selecione Tema do Mapa"}

lista_municipios = df_saude['Municipio'].unique().tolist()

lista_municipios_c_todos = lista_municipios
lista_municipios_c_todos.append('Todos os Municípios')

lista_col_numericas = df_score.select_dtypes(include=np.number).columns.tolist()
lista_col_numericas.remove('CO_MUNICIPIO_GESTOR')

#lista_col = df_saude.columns.tolist()

CONTROL_DATA = {
    "dropdown":lista_municipios_c_todos,
    "dropdown_2":lista_col_numericas,
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
            #botão de checkbox yes or no, por padrão selecionado yes
            html.P(dict_control_info["title_checkbox"], className="control-card-title"),
            dcc.Checklist(
                id="checkbox-select",
                options=[
                    {'label': 'Sim', 'value': 'Sim'},
                ],
                value=["Sim"]
            ),
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

def table_present(df):
    table = html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(len(df))
        ]),
    ])
    return table

app.layout = dcc.Loading(
        id="loading-1",
        children=[
            html.Div(
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
                                                            html.B("Score Final", id="Score-tema"),
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
                                    html.B("Tabela de Referência"),
                                    html.Hr(),
                                    html.Div(id="Table", style={'overflowX':'scroll'})
                                ],
                            ),
                            html.Br(),
                            html.Br(),
                        ],
                    ),
                ],
            ),
        ],
        type="default",
        fullscreen=True,
    )

@app.callback([Output('mapa', 'figure'),
               Output('barras_municipios', 'figure'),
               Output('Texto do Score Final', 'children'),
               Output('Texto do Ranking Estadual', 'children'),
               Output('Score-tema', 'children'),
               Output('Table', 'children')],
              [Input('dropdown-select', 'value'),
               Input('dropdown-select-2', 'value'),
               Input('checkbox-select', 'value'),])
def update_map_from_dropdown(selected_municipio, selected_tema, checkbox_value):

    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = score_compile(df_saude.loc[df_saude['Municipio'] != 'Teresina']).sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = df_score.sort_values(by=['score_final'], ascending=False).reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 5.2
        new_score = [html.P("Indisponível")]
        new_rank = [html.P("Indisponível")]
    elif selected_municipio in lista_municipios:
        filtered_df_2 = filtered_df.loc[filtered_df['Municipio'] == selected_municipio]
        zoom = 8.2
        new_score = [html.P(str(filtered_df_2[selected_tema].values[0]))]
        new_rank = [html.P(str(filtered_df_2.index[0]+1) + 'º de ' + str(filtered_df.shape[0]))]

    if (selected_tema is None):
        selected_tema = 'score_final'
    
    new_score_title = [html.B(selected_tema.replace('_', ' ').title())]
    new_map = grafico_mapa(filtered_df_2, selected_tema, zoom)
    new_barras = grafico_barras(filtered_df.iloc[0:10], selected_tema)
    new_table = table_present(filtered_df.iloc[0:10])
    
    return new_map, new_barras, new_score, new_rank, new_score_title, new_table

#Callback from multidropdown to update heatmap
#@app.callback(Output('heatmap', 'figure'),
#            [Input('multidropdown-select', 'value'),])
#def update_heatmap(selected_vars):
#    if selected_vars is None:
#        selected_vars = lista_col_numericas
#
#    new_heatmap = grafico_correlacao(df_score[selected_vars])
#    return new_heatmap



if __name__ == "__main__":

    app.run_server(debug=True)