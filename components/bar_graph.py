import plotly.express as px
from statistics import mean

def generate_bar_graph(df, tema, df_score):
    """ Função para gerar gráfico de barras"""
    range_y = [df_score[tema].min(), df_score[tema].max()]
    fig = px.bar(df,
                 x=df['Município'] if 'Município' in df.columns else df['Regional de Saúde'],
                 y=tema, 
                 color=tema,
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
    fig.update_coloraxes(colorbar_title='')
    return fig