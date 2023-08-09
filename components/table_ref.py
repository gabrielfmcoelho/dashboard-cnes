from dash import dash_table

def generate_table_ref(df, tema):
    if 'Município' in df.columns:
        df = df.iloc[:, 1:]
    else:
        df.drop(columns=['Cód do Município'], inplace=True)
        #formatar colunas numericas para 2 casas decimais
        for col in df.columns:
            if col != 'Regional de Saúde':
                df[col] = df[col].apply(lambda x: round(x, 2))
        df = df.iloc[:, :]
    return dash_table.DataTable(
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in df.columns],
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)',
            },
            {
                'if': {'column_id': tema},
                'font-weight': 'bold',
            },
        ],
    )