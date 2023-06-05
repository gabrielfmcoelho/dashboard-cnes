import dash
import dash.html as html
import dash.dcc as dcc
from dash import callback, Input, Output, State
from components.map_state import generate_state_map_fig
from database.dfcontroller import DfController
from components.card_description import generate_description_card
from components.card_control import generate_control_card
import pandas as pd

controller = DfController()

CONTROL_INFO = {"title_dropdown": "Selecione Município", "title_checkbox":"Deseja Desconsiderar a Capital ?", "title_dropdown_2":"Selecione Tema do Mapa", "title_dropdown3":"Selecione Regional de Saúde"}

CONTROL_DATA = {
    "dropdown_2":controller.create_num_features_list(),
    'dropdown_3':controller.get_regions_list(),
}

MAP_COMPONENT1 = html.Div(
    id="generic1",
    children=[
        html.B("1º Mapa Comparativo", id='titulo'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="ContainerMapaG",
            children=[
                dcc.Graph(id="mapa_retrato1"),
                generate_control_card(CONTROL_INFO, CONTROL_DATA, id="control-card-comp"),
            ],
        )
    ],
)

MAP_COMPONENT2 = html.Div(
    id="generic2",
    children=[
        html.B("2º Mapa Comparativo", id='titulo'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="ContainerMapaG2",
            children = [
                dcc.Graph(id="mapa_retrato2"),
                generate_control_card(CONTROL_INFO, CONTROL_DATA, id="control-card-comp2"),
            ],
        ),
    ],
)

MAP_COMPONENT3 = html.Div(
    id="generic3",
    children=[
        html.B("3º Mapa Comparativo", id='titulo'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="ContainerMapaG3",
            children = [
                dcc.Graph(id="mapa_retrato3"),
                generate_control_card(CONTROL_INFO, CONTROL_DATA, id="control-card-comp3"),
            ],
        ),
    ],
)

MAP_COMPONENT4 = html.Div(
    id="generic4",
    children=[
        html.B("4º Mapa Comparativo", id='titulo'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="ContainerMapaG4",
            children = [
                dcc.Graph(id="mapa_retrato4"),
                generate_control_card(CONTROL_INFO, CONTROL_DATA, id="control-card-comp4"),
            ],
        ),
    ],
)

def update_output_control():
    global INTRO_INFO
    global CONTROL_INFO
    div = [
            generate_description_card(INTRO_INFO, id="description-card-comp"),
        ],
    return div

layout = dcc.Loading(
            id="loading-2",
            children=[
                html.Div(id='none',children=[],style={'display': 'none'}),
                html.Div(id='div_especial_1', children=[
                    MAP_COMPONENT1,
                    MAP_COMPONENT2,
                ]),
                html.Div(id='div_especial_2', children=[
                    MAP_COMPONENT3,
                    MAP_COMPONENT4,
                ]),
                html.Br(),
            ],
            type="circle",
            color="#1f77b4",
            fullscreen=True,
            ),

@callback([Output("control-card-comp"+'dropdown-select', 'options'),
           Output("control-card-comp"+'dropdown-select', 'value'),],
          [Input("control-card-comp"+'dropdown-select-3', 'value'),
           Input("control-card-comp"+'checkbox-select', 'value'),])
def update_cities_dropdown1(region, remove_capital):



    if region == 'Todas as Regionais':
        regions_cities_list = controller.get_cities_list()
        if remove_capital:
            try:
                regions_cities_list.remove('Teresina')
            except:
                pass
    else:
        regions_cities_list = controller.create_regions_cities_list(remove_capital, region)
    regions_cities = [{"label": i, "value": i} for i in regions_cities_list]
    return regions_cities, regions_cities_list[-1]

@callback([Output('mapa_retrato1', 'figure'),],
              [Input("control-card-comp"+'dropdown-select', 'value'),
               Input("control-card-comp"+'dropdown-select-2', 'value'),
               Input("control-card-comp"+'checkbox-select', 'value'),
               Input("control-card-comp"+'dropdown-select-3', 'value'),
               Input("screen-width", "value")])
def update_map_from_dropdown1(selected_municipio, selected_tema, checkbox_value, region, width_flag):



    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = controller.get_df_health_without_the().sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = controller.get_df_health()


    if region != 'Todas as Regionais':
        filtered_df = filtered_df.loc[filtered_df['RegionaldeSaude'] == region].reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 4.8 if width_flag > 0 else 4.8
        offset = 0.8
        args = [zoom, offset]
    elif selected_municipio in controller.get_cities_list():
        filtered_df_2 = filtered_df.loc[filtered_df['Municipio'] == selected_municipio]
        zoom = 9
        offset = 0
        args = [zoom, offset]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_map = generate_state_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args, column_cod='CO_MUNICIPIO_GESTOR')

    return [new_map]


@callback([Output("control-card-comp2"+'dropdown-select', 'options'),
           Output("control-card-comp2"+'dropdown-select', 'value'),],
          [Input("control-card-comp2"+'dropdown-select-3', 'value'),
           Input("control-card-comp2"+'checkbox-select', 'value'),])
def update_cities_dropdown2(region, remove_capital):


    if region == 'Todas as Regionais':
        regions_cities_list = controller.get_cities_list()
        if remove_capital:
            try:
                regions_cities_list.remove('Teresina')
            except:
                pass
    else:
        regions_cities_list = controller.create_regions_cities_list(remove_capital, region)
    regions_cities = [{"label": i, "value": i} for i in regions_cities_list]
    return regions_cities, regions_cities_list[-1]

@callback([Output('mapa_retrato2', 'figure'),],
              [Input("control-card-comp2"+'dropdown-select', 'value'),
               Input("control-card-comp2"+'dropdown-select-2', 'value'),
               Input("control-card-comp2"+'checkbox-select', 'value'),
               Input("control-card-comp2"+'dropdown-select-3', 'value'),
               Input("screen-width", "value")])
def update_map_from_dropdown2(selected_municipio, selected_tema, checkbox_value, region, width_flag):



    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = controller.get_df_health_without_the().sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = controller.get_df_health()


    if region != 'Todas as Regionais':
        filtered_df = filtered_df.loc[filtered_df['RegionaldeSaude'] == region].reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 4.8 if width_flag > 0 else 4.8
        offset = 0.8
        args = [zoom, offset]
    elif selected_municipio in controller.get_cities_list():
        filtered_df_2 = filtered_df.loc[filtered_df['Municipio'] == selected_municipio]
        zoom = 7
        offset = 0
        args = [zoom, offset]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_map = generate_state_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args, column_cod='CO_MUNICIPIO_GESTOR')

    return [new_map]

@callback([Output("control-card-comp3"+'dropdown-select', 'options'),
           Output("control-card-comp3"+'dropdown-select', 'value'),],
          [Input("control-card-comp3"+'dropdown-select-3', 'value'),
           Input("control-card-comp3"+'checkbox-select', 'value'),])
def update_cities_dropdown3(region, remove_capital):


    if region == 'Todas as Regionais':
        regions_cities_list = controller.get_cities_list()
        if remove_capital:
            try:
                regions_cities_list.remove('Teresina')
            except:
                pass
    else:
        regions_cities_list = controller.create_regions_cities_list(remove_capital, region)
    regions_cities = [{"label": i, "value": i} for i in regions_cities_list]
    return regions_cities, regions_cities_list[-1]

@callback([Output('mapa_retrato3', 'figure'),],
              [Input("control-card-comp3"+'dropdown-select', 'value'),
               Input("control-card-comp3"+'dropdown-select-2', 'value'),
               Input("control-card-comp3"+'checkbox-select', 'value'),
               Input("control-card-comp3"+'dropdown-select-3', 'value'),
               Input("screen-width", "value")])
def update_map_from_dropdown3(selected_municipio, selected_tema, checkbox_value, region, width_flag):


    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = controller.get_df_health_without_the().sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = controller.get_df_health()


    if region != 'Todas as Regionais':
        filtered_df = filtered_df.loc[filtered_df['RegionaldeSaude'] == region].reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 4.8 if width_flag > 0 else 4.8
        offset = 0.8
        args = [zoom, offset]
    elif selected_municipio in controller.get_cities_list():
        filtered_df_2 = filtered_df.loc[filtered_df['Municipio'] == selected_municipio]
        zoom = 7
        offset = 0
        args = [zoom, offset]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_map = generate_state_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args, column_cod='CO_MUNICIPIO_GESTOR')

    return [new_map]

@callback([Output("control-card-comp4"+'dropdown-select', 'options'),
           Output("control-card-comp4"+'dropdown-select', 'value'),],
          [Input("control-card-comp4"+'dropdown-select-3', 'value'),
           Input("control-card-comp4"+'checkbox-select', 'value'),])
def update_cities_dropdown4(region, remove_capital):


    if region == 'Todas as Regionais':
        regions_cities_list = controller.get_cities_list()
        if remove_capital:
            try:
                regions_cities_list.remove('Teresina')
            except:
                pass
    else:
        regions_cities_list = controller.create_regions_cities_list(remove_capital, region)
    regions_cities = [{"label": i, "value": i} for i in regions_cities_list]
    return regions_cities, regions_cities_list[-1]

@callback([Output('mapa_retrato4', 'figure'),],
              [Input("control-card-comp4"+'dropdown-select', 'value'),
               Input("control-card-comp4"+'dropdown-select-2', 'value'),
               Input("control-card-comp4"+'checkbox-select', 'value'),
               Input("control-card-comp4"+'dropdown-select-3', 'value'),
               Input("screen-width", "value")])
def update_map_from_dropdown4(selected_municipio, selected_tema, checkbox_value, region, width_flag):



    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = controller.get_df_health_without_the().sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
    else:
        filtered_df = controller.get_df_health()


    if region != 'Todas as Regionais':
        filtered_df = filtered_df.loc[filtered_df['RegionaldeSaude'] == region].reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 4.8 if width_flag > 0 else 4.8
        offset = 0.8
        args = [zoom, offset]
    elif selected_municipio in controller.get_cities_list():
        filtered_df_2 = filtered_df.loc[filtered_df['Municipio'] == selected_municipio]
        zoom = 7
        offset = 0
        args = [zoom, offset]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_map = generate_state_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args, column_cod='CO_MUNICIPIO_GESTOR')

    return [new_map]