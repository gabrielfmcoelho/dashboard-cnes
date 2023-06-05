import pandas as pd
import plotly.express as px
from statistics import mean

def generate_state_map_fig(df_muni, df_i, tema, args, column_cod='Cód do Município'):
    """

    :return: Função para Gerar o Gráfico do Mapa
    """
    df = df_i.copy()
    all_muni = df_muni.copy()
    df[column_cod] = df[column_cod].astype(float)
    all_muni = all_muni.loc[all_muni['code_muni'].isin(list(df[column_cod]))]
    all_muni = all_muni.rename(columns={'code_muni': column_cod})
    all_muni = pd.merge(all_muni, df, how='left', on = column_cod)
    all_muni.index = list(all_muni['name_muni'])
    fig = px.choropleth_mapbox(all_muni,
        geojson=all_muni.geometry,
        locations=all_muni.index,
        color=tema,
        color_continuous_scale="Spectral",
        opacity=0.6,
        center={"lat": (((mean(list(all_muni.geometry.bounds.maxy))-mean(list(all_muni.geometry.bounds.miny)))/2)+mean(list(all_muni.geometry.bounds.miny)))
        , "lon": (((mean(list(all_muni.geometry.bounds.maxx))-mean(list(all_muni.geometry.bounds.minx)))/2)+mean(list(all_muni.geometry.bounds.minx)))-args[1]},
        labels={'index':'name_muni'},
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