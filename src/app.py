import dash
from dash import Dash, dash_table
import dash.dcc as dcc
import dash.html as html
from dash.dependencies import Input, Output, ClientsideFunction

import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from datetime import datetime as dt
import geopandas as gpd
from statistics import mean

import pathlib

import database.bigqueryconn as bqconn

from scoreTreatment import score_compile

TITLE = "Análise da Saude no Piauí"

app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title=TITLE,
)

server = app.server
app.config.suppress_callback_exceptions = False

BASE_PATH = pathlib.Path(__file__).parent.resolve()

def get_data_from_bigquery():
    conn = bqconn.BigQueryConn('etl-cnes-a7a20431c4d7.json')
    df_saude = conn.get_data_df('query_saude_score.txt')
    df_saude.to_csv("df_saude.csv")
    return df_saude

df_saude = pd.read_csv("df_saude.csv")
df_score = score_compile(df_saude)
df_score = df_score.sort_values(by=['score_final'], ascending=False).reset_index(drop=True)
DICT_RENAME = {'CO_MUNICIPIO_GESTOR': 'Cód do Município',
                'Municipio': 'Município',
                'score_1': 'Leitos',
                'score_2': 'Estabelecimentos',
                'score_3': 'Demografia Geral',
                'score_4': 'Demografia Faixa Etária',
                'score_5': 'Fluxo de Pacientes',
                'score_final': 'Score Final'}
#rename columns 
df_score = df_score.rename(columns=DICT_RENAME)

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
lista_col_numericas.remove('Cód do Município')

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
    df['Cód do Município'] = df['Cód do Município'].astype(float)
    all_muni = all_muni.loc[all_muni['code_muni'].isin(list(df['Cód do Município']))]
    all_muni = all_muni.rename(columns={'code_muni': 'Cód do Município'})
    all_muni = pd.merge(all_muni, df, how='left', on = 'Cód do Município')
    all_muni.index = list(all_muni['name_muni'])
    fig = px.choropleth_mapbox(all_muni,
        geojson=all_muni.geometry,
        locations=all_muni.index,
        color=tema,
        color_continuous_scale="Spectral",
        opacity=0.6,
        center={"lat": (((mean(list(all_muni.geometry.bounds.maxy))-mean(list(all_muni.geometry.bounds.miny)))/2)+mean(list(all_muni.geometry.bounds.miny)))
        , "lon": (((mean(list(all_muni.geometry.bounds.maxx))-mean(list(all_muni.geometry.bounds.minx)))/2)+mean(list(all_muni.geometry.bounds.minx)))},
        labels={'index':'name_muni'},
        mapbox_style="open-street-map",
        zoom=zoom[0] if zoom else 5.2,
    )
    fig.update_layout(
        dragmode=False,
        margin=dict(l=1, r=1, t=1, b=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        )
    return fig


# Função para gerar heatmap de correlação de variáveis
def grafico_correlacao(df):
    """ Função para gerar heatmap de correlação de variáveis"""
    fig = go.Figure(data=go.Heatmap(
        z=df.corr(),
        x=df.columns,
        y=df.columns,
        colorscale='Spectral',
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
    range_y = [df_score[tema].min(), df_score[tema].max()]
    fig = px.bar(df,
                 x=df['Município'],
                 y=tema, color=tema,
                 color_continuous_scale='Spectral',
                 opacity=0.7,
                 range_y=range_y,
                 color_continuous_midpoint=mean(range_y),
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=1, r=1, t=1, b=1),
    )
    return fig

def table_present(df, tema):
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in df.columns[1:]],
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)',
            },
            {
                'if': {'column_id': tema},
                'font-weight': 'bold',
            }
        ],
    )
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
                            # Mapa
                            html.Div(
                                id="Mapa",
                                children=[
                                    html.B("Mapa do Estado", id='titulo'),
                                    html.Hr(),
                                    html.Br(),
                                    dcc.Graph(
                                        id="mapa",
                                    ),
                                ],
                            ),
                            html.Br(),
                            # Indicadores
                            html.Div(
                                id="indicadores",
                                children=[
                                    html.B("Indicadores", id='titulo2'),
                                    html.Hr(),
                                    html.Br(),
                                    html.Div(
                                        id="", className="row",
                                        children=[
                                            html.Div(
                                                id="",
                                                className="six columns",
                                                children=[
                                                    html.Div(
                                                        id="indicador",
                                                        children=[
                                                            html.B("Score Final", id="Score-tema"),
                                                            html.Hr(),
                                                            html.Div(
                                                                id="Texto_do_Score_Final",
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
                                                        id="indicador2",
                                                        children=[
                                                            html.B("Ranking Estadual"),
                                                            html.Hr(),
                                                            html.Div(
                                                                id="Texto_do_Ranking_Estadual",
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
                            # Gráfico de Barras de Municipios
                            html.Div(
                                id="ranking",
                                children=[
                                    html.B("Ranking Municipal", id='titulo3'),
                                    html.Hr(),
                                    html.Br(),
                                    dcc.Graph(
                                        id="barras_municipios",
                                    ),
                                ],
                            ),
                            html.Br(),
                            # Grafico de Correlação de Variáveis
                            html.Div(
                                id="table",
                                children=[
                                    html.B("Tabela de Referência", id='titulo4'),
                                    html.Hr(),
                                    html.Br(),
                                    html.Div(id="Table", style={'overflowX':'scroll'})
                                ],
                            ),
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
               Output('Texto_do_Score_Final', 'children'),
               Output('Texto_do_Ranking_Estadual', 'children'),
               Output('Score-tema', 'children'),
               Output('Table', 'children')],
              [Input('dropdown-select', 'value'),
               Input('dropdown-select-2', 'value'),
               Input('checkbox-select', 'value'),])
def update_map_from_dropdown(selected_municipio, selected_tema, checkbox_value):

    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = score_compile(df_saude.loc[df_saude['Municipio'] != 'Teresina'])
        filtered_df = filtered_df.rename(columns=DICT_RENAME).sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = df_score

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 5.2
        new_score = [html.P("Indisponível")]
        new_rank = [html.P("Indisponível")]
    elif selected_municipio in lista_municipios:
        filtered_df_2 = filtered_df.loc[filtered_df['Município'] == selected_municipio]
        zoom = 8.2
        new_score = [html.P(str(filtered_df_2[selected_tema].values[0]))]
        new_rank = [html.P(str(filtered_df_2.index[0]+1) + 'º de ' + str(filtered_df.shape[0]))]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_score_title = [html.B(selected_tema.title())]
    new_map = grafico_mapa(filtered_df_2, selected_tema, zoom)
    new_barras = grafico_barras(filtered_df.iloc[0:10], selected_tema)
    new_table = table_present(filtered_df.iloc[0:10], selected_tema)
    
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
    get_data_from_bigquery()
    app.run_server(debug=True)