import pandas as pd
import numpy as np
from lazy import lazy
import database.bigqueryconn as bqconn
import geopandas as gpd
from scripts.relevancyTreatment import relevancy_compile
from scripts.scoreTreatment import score_compile
import unidecode

class DfController:
    df_health = pd.DataFrame()
    df_health_without_the = pd.DataFrame()
    df_score = pd.DataFrame()
    df_score_without_the = pd.DataFrame()
    df_relevancy = pd.DataFrame()
    df_relevancy_without_the = pd.DataFrame()
    df_cities = pd.DataFrame()
    df = pd.DataFrame()	
    has_run = False

    cities_list = []
    score_list = []
    regions_list = []
    complete_features_list = []

    def __init__(self):
        pass

    def get_has_run(self):
        return self.__class__.has_run
    
    def update_has_run(self):
        self.__class__.has_run = True

    def get_df_health(self):
        return self.__class__.df_health
    
    def update_df_health(self):
        self.__class__.df_health = self.df_health

    def get_df_health_without_the(self):
        return self.__class__.df_health_without_the

    def update_df_health_without_the(self):
        self.__class__.df_health_without_the = self.df_health_without_the

    def get_df_score(self):
        return self.__class__.df_score

    def update_df_score(self):
        self.__class__.df_score = self.df_score

    def get_df_score_without_the(self):
        return self.__class__.df_score_without_the

    def update_df_score_without_the(self):
        self.__class__.df_score_without_the = self.df_score_without_the

    def get_df_relevancy(self):
        return self.__class__.df_relevancy

    def update_df_relevancy(self):
        self.__class__.df_relevancy = self.df_relevancy

    def get_df_relevancy_without_the(self):
        return self.__class__.df_relevancy_without_the

    def update_df_relevancy_without_the(self):
        self.__class__.df_relevancy_without_the = self.df_relevancy_without_the

    def get_df_cities(self):
        return self.__class__.df_cities

    def update_df_cities(self):
        self.__class__.df_cities = self.df_cities

    def get_df(self):
        return self.__class__.df

    def update_df(self):
        self.__class__.df = self.df  

    def get_cities_list(self):
        return self.__class__.cities_list

    def update_cities_list(self):
        self.__class__.cities_list = self.cities_list

    def get_score_list(self):
        return self.__class__.score_list

    def update_score_list(self):
        self.__class__.score_list = self.score_list

    def get_regions_list(self):
        return self.__class__.regions_list

    def update_regions_list(self):
        self.__class__.regions_list = self.regions_list

    def get_complete_features_list(self):
        return self.__class__.complete_features_list

    def update_complete_features_list(self):
        self.__class__.complete_features_list = self.complete_features_list      

    def get_df_health_from_bigquery(self, credentials_file, query_file):
        conn = bqconn.BigQueryConn(credentials_file)
        self.df_health = conn.get_data_df(query_file)
        self.df_health.to_csv("df_saude.csv", index=False)
        return self.df_health
    
    def generate_dfs(self):
        DICT_RENAME = {'CO_MUNICIPIO_GESTOR': 'Cód do Município',
                'Municipio': 'Município',
                'RegionaldeSaude': 'Regional de Saúde',
                'score_1': 'Leitos',
                'score_2': 'Estabelecimentos',
                'score_3': 'Demografia Geral',
                'score_4': 'Demografia Faixa Etária',
                'score_5': 'Fluxo de Pacientes',
                'score_final': 'Score Final'}
            
        self.df_score = score_compile(self.__class__.df_health).sort_values(by=['score_final'], ascending=False).reset_index(drop=True)
        self.df_score = self.df_score.rename(columns=DICT_RENAME)
        self.df_score.to_csv('df_score.csv', index=False)

        self.df_relevancy = relevancy_compile(self.df_score)
        self.df_relevancy.to_csv('df_relevancy.csv', index=False)

        self.df_health_without_the = self.__class__.df_health.loc[self.__class__.df_health['Municipio'] != 'Teresina']
        self.df_health_without_the.to_csv('df_saude_without_the.csv', index=False)

        self.df_score_without_the = score_compile(self.df_health_without_the).sort_values(by=['score_final'], ascending=False).reset_index(drop=True)
        self.df_score_without_the = self.df_score_without_the.rename(columns=DICT_RENAME)
        self.df_score_without_the.to_csv('df_score_without_the.csv', index=False)

        self.df_relevancy_without_the = relevancy_compile(self.df_score_without_the)
        self.df_relevancy_without_the.to_csv('df_relevancy_without_the.csv', index=False)
        return self.df_health_without_the, self.df_score, self.df_score_without_the, self.df_relevancy, self.df_relevancy_without_the
    
    def read_geojson(self, path_geojson):
        self.df_cities = gpd.read_file(path_geojson)
        self.df_cities['code_muni'] = self.df_cities['code_muni'].astype(int)
        self.df_cities['code_muni'] = self.df_cities['code_muni'].astype(str)
        self.df_cities['code_muni'] = self.df_cities['code_muni'].str[:-1]
        self.df_cities['code_muni'] = self.df_cities['code_muni'].astype(float)
        return self.df_cities
    
    def create_cities_list(self):
        def remove_accentuation(text):
            return unidecode.unidecode(text)
        cities_list = self.__class__.df_score['Município'].unique().tolist()
        self.cities_list = sorted(cities_list, key=lambda x: remove_accentuation(x))
        self.cities_list.append('Todos os Municípios')
        return self.cities_list
    
    def create_regions_cities_list(self, remove_capital, region):
        def remove_accentuation(text):
            return unidecode.unidecode(text)
        regions_cities_list = self.__class__.df_score.loc[self.__class__.df_score['Regional de Saúde'] == region]['Município'].unique().tolist()
        if (remove_capital != []) and (region == self.__class__.df_score.loc[self.__class__.df_score['Município'] == 'Teresina']['Regional de Saúde'][0]):
            regions_cities_list.remove('Teresina')
        regions_cities_list = sorted(regions_cities_list, key=lambda x: remove_accentuation(x))
        regions_cities_list.append('Todos os Municípios')
        return regions_cities_list
    
    def create_regions_list(self):
        def remove_accentuation(text):
            return unidecode.unidecode(text)
        regions_list = self.__class__.df_score['Regional de Saúde'].unique().tolist()
        self.regions_list = sorted(regions_list, key=lambda x: remove_accentuation(x))
        self.regions_list.append('Todas as Regionais')
        return self.regions_list
    
    def create_score_list(self):
        self.score_list = self.__class__.df_score.select_dtypes(include=np.number).columns.tolist()
        self.score_list.remove('Cód do Município')
        return self.score_list

    def create_num_features_list(self):
        self.complete_features_list = self.__class__.df_health.select_dtypes(include=np.number).columns.tolist()
        self.complete_features_list.remove('CO_MUNICIPIO_GESTOR')
        return self.complete_features_list