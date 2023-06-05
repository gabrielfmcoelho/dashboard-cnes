# IMPORT DE BIBLIOTECAS DE DASH
import dash
import dash.dcc as dcc
import dash.html as html
from dash import callback
from dash.dependencies import Input, Output, ClientsideFunction
# IMPORT DE BIBLIOTECAS DE MANIPULAÇÃO DE DADOS
import pandas as pd
import numpy as np
from datetime import datetime as dt
import geopandas as gpd
import lazy
# IMPORT DE SCRIPTS DE DADOS
from database.dfcontroller import DfController
# IMPORT DE COMPONENTES
from components.card_description import generate_description_card
from components.card_control import generate_control_card
from components.map_state import generate_state_map_fig
from components.bar_graph import generate_bar_graph
from components.table_ref import generate_table_ref
from components.table_rel import generate_table_rel

TITLE = "Solude Growth"

PATH_CREDENTIALS = "./database/etl-cnes-a7a20431c4d7.json"
PATH_QUERY = "query_saude_score.txt"
PATH_DATASETS = './datasets/'
PATH_GEOJSON = './database/municipios.geojson'

controller = DfController()
if not (controller.get_has_run()):
    controller.update_has_run()
    controller.get_df_health_from_bigquery(PATH_CREDENTIALS, PATH_QUERY)
    controller.update_df_health()

    controller.generate_dfs()
    controller.update_df_health_without_the()
    controller.update_df_score()
    controller.update_df_score_without_the()
    controller.update_df_relevancy()
    controller.update_df_relevancy_without_the()

    controller.read_geojson(PATH_GEOJSON)
    controller.update_df_cities()

    controller.create_cities_list()
    controller.create_regions_list()
    controller.create_score_list()
    controller.create_num_features_list()

    controller.update_cities_list()
    controller.update_regions_list()
    controller.update_score_list()
    controller.update_complete_features_list()

from pages import home, comparison

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title=TITLE,
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H4("SOLUDE DATALAB", id="banner-title"),
                html.Div(
                    id="banner-nav",
                    children=[
                        html.A("Visão Geral", id="banner-link", className="banner-link-inicio", href="/"),
                        html.A("Comparações", id="banner-link-2", className="banner-link-Comparação", href="/comparacao"),
                    ],
                ),
            ],
        ),
        dcc.Input(id="screen-width", type="hidden"),
        html.Div(
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content")
            ],
        )
    ],
    style={'overflowX':'scroll'}
)

app.clientside_callback(
    """
    function(value) {
        let screen_width = window.innerWidth;
        if (screen_width < 768) {
            return 0;
        } else {
            return 1;
        }
    }
    """,
    Output("screen-width", "value"),
    Input("app-container", "children"),
)

@callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/comparacao":
        return comparison.layout
    else:
        return "404"

if __name__ == "__main__":
    
    app.run_server(debug=False, host="0.0.0.0", port=8080)