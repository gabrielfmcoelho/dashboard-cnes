import plotly.graph_objects as go

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