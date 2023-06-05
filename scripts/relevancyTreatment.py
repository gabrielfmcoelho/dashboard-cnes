import pandas as pd
import numpy as np
import warnings
from scripts.scoreTreatment import score_compile
warnings.filterwarnings("ignore", category=Warning)

def relevancy_compile(df):
    df_leitos = df[['Município', 'Leitos']]
    df_leitos = df.sort_values(by='Leitos', ascending=False).reset_index(drop=True)
    df_leitos['Leitos'] = df_leitos.apply(lambda x: x['Município'], axis=1)
    df_leitos = df_leitos['Leitos'].iloc[:10]

    df_estabelecimentos = df[['Município', 'Estabelecimentos']]
    df_estabelecimentos = df.sort_values(by='Estabelecimentos', ascending=False).reset_index(drop=True)
    df_estabelecimentos['Estabelecimentos'] = df_estabelecimentos.apply(lambda x: x['Município'], axis=1)
    df_estabelecimentos = df_estabelecimentos['Estabelecimentos'].iloc[:10]

    df_demograficos = df[['Município', 'Demografia Geral']]
    df_demograficos = df.sort_values(by='Demografia Geral', ascending=False).reset_index(drop=True)
    df_demograficos['Demografia Geral'] = df_demograficos.apply(lambda x: x['Município'], axis=1)
    df_demograficos = df_demograficos['Demografia Geral'].iloc[:10]

    df_demograficos_faixa_etaria = df[['Município', 'Demografia Faixa Etária']]
    df_demograficos_faixa_etaria = df.sort_values(by='Demografia Faixa Etária', ascending=False).reset_index(drop=True)
    df_demograficos_faixa_etaria['Demografia Faixa Etária'] = df_demograficos_faixa_etaria.apply(lambda x: x['Município'], axis=1)
    df_demograficos_faixa_etaria = df_demograficos_faixa_etaria['Demografia Faixa Etária'].iloc[:10]

    df_fluxo = df[['Município', 'Fluxo de Pacientes']]
    df_fluxo = df.sort_values(by='Fluxo de Pacientes', ascending=False).reset_index(drop=True)
    df_fluxo['Fluxo de Pacientes'] = df_fluxo.apply(lambda x: x['Município'], axis=1)
    df_fluxo = df_fluxo['Fluxo de Pacientes'].iloc[:10]

    df_pop = df[['Município', 'População']]
    df_pop = df.sort_values(by='População', ascending=False).reset_index(drop=True)
    df_pop['População'] = df_pop.apply(lambda x: x['Município'], axis=1)
    df_pop = df_pop['População'].iloc[:10]

    df_final = df[['Município', 'Score Final']]
    df_final = df.sort_values(by='Score Final', ascending=False).reset_index(drop=True)
    df_final['Score Final'] = df_final.apply(lambda x: x['Município'], axis=1)
    df_final = df_final['Score Final'].iloc[:10]

    #merge dataframes with same index
    merge_df = pd.merge(df_pop, df_leitos, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, df_estabelecimentos, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, df_demograficos, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, df_demograficos_faixa_etaria, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, df_fluxo, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, df_final, left_index=True, right_index=True)

    return merge_df


