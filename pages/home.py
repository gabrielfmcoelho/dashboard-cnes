import dash
import dash.html as html
import dash.dcc as dcc
from dash import callback, Input, Output, State
from components.card_description import generate_description_card
from components.card_control import generate_control_card
from components.bar_graph import generate_bar_graph
from components.table_ref import generate_table_ref
from components.table_rel import generate_table_rel
from components.map_state import generate_state_map_fig
from components.map_regions import generate_regions_map_fig
from database.dfcontroller import DfController

controller = DfController()
suppesed_callback_exceptions = True

INTRO_INFO = {"title": "Solude Growth", "subtitle":"Descubra Insights Valiosos", "description": "Explore os dados de saúde e conheça mais sobre a situação em cada município."}
CONTROL_INFO = {"title_dropdown": "Selecione Município", "title_checkbox":"Deseja Desconsiderar a Capital ?", "title_dropdown_2":"Selecione Tema do Mapa", "title_dropdown3":"Selecione Regional de Saúde"}

CONTROL_DATA = {
    "dropdown_2":controller.get_score_list(),
    'dropdown_3':controller.get_regions_list(),
}

LEFT_SIDE_COLUMN = html.Div(
    id="left-column",
    className="four columns",
)

#style={'width': '100%', 'display': 'inline-block'},

MAP_COMPONENT = html.Div(
            id="Mapa",
            children=[
                html.B("Mapa do Estado", id='titulo'),
                html.Hr(),
                html.Br(),
                html.Div(
                    children = [
                        dcc.Graph(id='mapa'),
                    ],
                ),
            ],
        )

SCORE_COMPONENT = html.Div(
    id="Indicadores",
    children=[
        html.B("Indicadores", id='titulo2'),
        html.Hr(),
        html.Br(),
        html.Div(
            children = [
                html.Div(
                    id="indicador",
                    children=[
                        html.B(id="Score-tema"),
                        html.P("Carregando...", id="Texto_do_Score_Final"),
                    ],
                ),
                html.Div(
                    id="indicador2",
                    children=[
                        html.B("Ranking Estadual", id="Ranking_Estadual"),
                        html.P("Carregando...", id="Texto_do_Ranking_Estadual"),
                    ],
                ),
            ],
        ),
    ],
)

SCORE_TEXT_COMPONENT = html.Div(
    id="IndicadoresExplicacao",
    children=[
        html.B("O que é o Score ?", id='titulo2'),
        html.Hr(),
        html.Br(),
        html.Div(
            children = [
                html.P("O Score é um indicador que varia de 0 a 100, que representa a situação de um município em relação a um tema específico. Quanto maior o Score, melhor a situação do município em relação ao tema.", id="Texto_do_Score"),
            ],
        ),
    ],
)

RANKING_COMPONENT = html.Div(
    id="Ranking",
    children=[
        html.B("Ranking Municipal", id='titulo3'),
        html.Hr(),
        html.Br(),
        dcc.Graph(id="barras_municipios"),
    ],
)

TABLE_REF_COMPENENT = html.Div(
    id="table",
    children=[
        html.B("Tabela de Referência", id='titulo4'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="Table",
            style={'overflowX':'scroll'}
        ),
    ],
)

TABLE_REL_COMPENENT = html.Div(
    id="table_rel",
    children=[
        html.B("Tabela Relevância", id='titulo5'),
        html.Hr(),
        html.Br(),
        html.Div(
            id="Table_rel",
            style={'overflowX':'scroll'}
        ),
    ],
)

RIGHT_SIDE_COLUMN = html.Div(
    id="right-column",
    className="eight columns",
    children=[
        html.Div(
            id="Mapa_Completo",
            children=[
                MAP_COMPONENT,
                html.Div([
                    SCORE_COMPONENT,
                    SCORE_TEXT_COMPONENT,
                ], id="Indicadores_coluna"),
            ],
        ),
        RANKING_COMPONENT,
        TABLE_REF_COMPENENT,
        TABLE_REL_COMPENENT,
    ],
)

def update_output_control():
    global INTRO_INFO
    global CONTROL_INFO
    div = [
            generate_description_card(INTRO_INFO),
            html.P("Metodo de Visualização", className="control-card-title", id="tab-title"),
            dcc.Tabs(id="tabs", value='tab-1', children=[
                            dcc.Tab(label='Municipios', value='tab-1'),
                            dcc.Tab(label='Regionais', value='tab-2'),
                        ], colors={
                            "border": "white",
                            "primary": "#2c8cff",
                            "background": "lightgray",
                            },
                        ),
            html.Br(),
            generate_control_card(CONTROL_INFO, CONTROL_DATA),
        ],
    return div

layout = dcc.Loading(
            id="loading-1",
            children=[
                html.Div(id='none',children=[],style={'display': 'none'}),
                # Coluna da esquerda
                LEFT_SIDE_COLUMN,
                # Coluna da direita
                RIGHT_SIDE_COLUMN,
                ],
            type="circle",
            color="#1f77b4",
            fullscreen=True,
            ),

@callback([Output('left-column', 'children')],
          [Input('none', 'children'),])
def control(none):


    div = update_output_control()
    return div

@callback([Output("control-card"+'dropdown-select', 'options'),
           Output("control-card"+'dropdown-select', 'value'),],
          [Input("control-card"+'dropdown-select-3', 'value'),
           Input("control-card"+'checkbox-select', 'value'),])
def update_cities_dropdown(region, remove_capital):


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

@callback([Output('mapa', 'figure'),
               Output('barras_municipios', 'figure'),
               Output('Texto_do_Score_Final', 'children'),
               Output('Texto_do_Ranking_Estadual', 'children'),
               Output('Score-tema', 'children'),
               Output('Table', 'children'),
               Output('Table_rel', 'children'),],
              [Input("control-card"+'dropdown-select', 'value'),
               Input("control-card"+'dropdown-select-2', 'value'),
               Input("control-card"+'checkbox-select', 'value'),
               Input("control-card"+'dropdown-select-3', 'value'),
               Input("screen-width", "value"),
               Input("tabs", 'value'),])
def update_map_from_dropdown(selected_municipio, selected_tema, checkbox_value, region, width_flag, tab):

    if checkbox_value != [] and checkbox_value[0] == "Sim":
        filtered_df = controller.get_df_score_without_the().sort_values(by=selected_tema, ascending=False).reset_index(drop=True)
        df_relevancy = controller.get_df_relevancy_without_the()
        df_untouched = controller.get_df_health_without_the().rename(columns={'CO_MUNICIPIO_GESTOR': 'Cód do Município',})
    else:
        filtered_df = controller.get_df_score()       
        df_untouched = controller.get_df_health().rename(columns={'CO_MUNICIPIO_GESTOR': 'Cód do Município',})
        df_relevancy = controller.get_df_relevancy()

    if region != 'Todas as Regionais':
        filtered_df = filtered_df.loc[filtered_df['Regional de Saúde'] == region].reset_index(drop=True)
        df_untouched = df_untouched.loc[df_untouched['RegionaldeSaude'] == region].reset_index(drop=True)

    if (selected_municipio is None)or(selected_municipio == 'Todos os Municípios'):
        filtered_df_2 = filtered_df
        zoom = 5.2 if width_flag > 0 else 4.8
        offset = 0.8
        args = [zoom, offset]
        new_score = [html.P("Indisponível")]
        new_rank = [html.P("Indisponível")]
    elif selected_municipio in controller.get_cities_list():
        filtered_df_2 = filtered_df.loc[filtered_df['Município'] == selected_municipio]
        zoom = 9
        offset = 0
        args = [zoom, offset]
        new_score = [html.P(str(filtered_df_2[selected_tema].values[0]))]
        new_rank = [html.P(str(filtered_df_2.index[0]+1) + 'º de ' + str(filtered_df.shape[0]))]

    if (selected_tema is None):
        selected_tema = 'Score Final'

    new_score_title = [html.B(selected_tema.title())]
    if tab == 'tab-1':
        new_relevancy_table = generate_table_rel(df_relevancy)
        new_map = generate_state_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args)
    elif tab == 'tab-2':
        new_relevancy_table = html.H1("Disponível apenas para municípios")
        new_map = generate_regions_map_fig(controller.get_df_cities(), filtered_df_2, selected_tema, args)
        filtered_df = filtered_df.groupby(['Regional de Saúde']).mean().sort_values(by=selected_tema, ascending=False).reset_index()
    new_barras = generate_bar_graph(filtered_df.iloc[0:10], selected_tema, filtered_df)
    new_table = generate_table_ref(filtered_df.iloc[0:10], selected_tema)
    
    
    return new_map, new_barras, new_score, new_rank, new_score_title, new_table, new_relevancy_table