import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=Warning)

def score_compile(df):
    df = df.copy()
    # Score 1 - Leitos de Saúde
    lista_scores_1 = ['QTLeitosSUS', 'QT_NaoSUS', 'DVLeitos', 'EXTLeitosPediatrico']
    for column in lista_scores_1:
        df[column] = df[column].astype(float)
        max_col = df[column].max()
        df[column] = df[column]/max_col
    df['score_1'] = np.mean(df[lista_scores_1], axis=1)
    df['score_1'] = df['score_1'].apply(lambda x: round(x*100, 2))

    # Score 2 - Estabelecimentos de Saúde
    lista_score_2 = ['QTUnidades', 'QTCNES', 'QTProfissionais', 'QTHospitais', 'QTClinicas', 'QTLaboratorios', 'QTConsultorios', 'QTUnidadesBasicas', 'DVtpunidade']
    for column in lista_score_2:
        df[column] = df[column].astype(float)
        max_col = df[column].max()
        df[column] = df[column]/max_col
    df['score_2'] = np.mean(df[lista_score_2], axis=1)
    df['score_2'] = df['score_2'].apply(lambda x: round(x*100, 2))


    df['População'] = df['PopulacaoEstimada_2021_']
    # Score 3 - Dados Demográficos Gerais
    lista_score_3 = ['DensidadeDemografica_2010_', 'PopulacaoEstimada_2021_', 'IDHM_2010_', 'PIBPerCapita_2020_']
    for column in lista_score_3:
        df[column] = df[column].astype(float)
        max_col = df[column].max()
        df[column] = df[column]/max_col
    df['score_3'] = np.mean(df[lista_score_3], axis=1)
    df['score_3'] = df['score_3'].apply(lambda x: round(x*100, 2))

    # Score 4 - Dados Demográficos de Faixa Etaria
    lista_score_4 = ['IdadeMediaPop', 'PopRelPediatrica', 'PopRelIdoso']
    for column in lista_score_4:
        df[column] = df[column].astype(float)
        max_col = df[column].max()
        df[column] = df[column]/max_col
    df['score_4'] = np.mean(df[lista_score_4], axis=1)
    df['score_4'] = df['score_4'].apply(lambda x: round(x*100, 2))

    # Score 5 - SIH envio e recebimento de pacientes
    df['DiffRecEnv'] = df['PacientesRec'] - df['PacientesEnv']
    lista_score_5 = ['DiffRecEnv']
    for column in lista_score_5:
        df[column] = df[column].astype(float)
        max_col = df[column].max()
        df[column] = df[column]/max_col
    df['score_5'] = np.mean(df[lista_score_5], axis=1)
    df['score_5'] = df['score_5'].apply(lambda x: round(x*100, 2))

    lista_de_scores = ['score_1', 'score_2', 'score_3', 'score_4', 'score_5']
    df['score_final'] = np.mean(df[lista_de_scores], axis=1)
    df['score_final'] = df['score_final'].apply(lambda x: round(x, 2))
    lista_final = ['CO_MUNICIPIO_GESTOR', 'Municipio', 'Mesoregiao', 'RegionaldeSaude', 'População'] + lista_de_scores + ['score_final']
    df = df[lista_final]

    return df