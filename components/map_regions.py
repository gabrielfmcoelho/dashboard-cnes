import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statistics import mean

def generate_regions_map_fig(df_muni, df_i, tema, args, column_cod='Cód do Município'):
    """

    :return: Função para Gerar o Gráfico do Mapa
    """
    df = df_i.copy()
    all_muni = df_muni.copy()
    df[column_cod] = df[column_cod].astype(float)
    all_muni = all_muni.loc[all_muni['code_muni'].isin(list(df[column_cod]))]
    all_muni = all_muni.rename(columns={'code_muni': column_cod})
    all_muni = pd.merge(all_muni, df, how='left', on = column_cod)

    regions = all_muni.rename(columns={'Regional de Saúde': "regiao"})
    regions = regions.dissolve(by='regiao', aggfunc='mean')
    regions = regions.reset_index()
    regions.index = list(regions['regiao'])

    regions[tema] = regions[tema].apply(lambda x: round(x, 2))

    fig = px.choropleth_mapbox(
        regions,
        geojson=regions.geometry,
        locations=regions.index,
        color=tema,
        color_continuous_scale="Spectral",
        opacity=0.6,
        center={"lat": (((mean(list(regions.geometry.bounds.maxy))-mean(list(regions.geometry.bounds.miny)))/2)+mean(list(regions.geometry.bounds.miny)))
        , "lon": (((mean(list(regions.geometry.bounds.maxx))-mean(list(regions.geometry.bounds.minx)))/2)+mean(list(regions.geometry.bounds.minx)))-args[1]},
        labels={'index':'Regional de Saúde'},
        mapbox_style="open-street-map",
        zoom=args[0] if args[0] else 5.2,
    )
    fig.update_layout(
        dragmode=False,
        margin=dict(l=1, r=1, t=1, b=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        )
    fig.update_coloraxes(colorbar_title='')

    return fig