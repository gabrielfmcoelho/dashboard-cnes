from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

class BigQueryConn:
    def __init__(self, credentials_path):
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])

    def create_table(self):
        pass

    def insert_data(self):
        pass

    def get_data_df(self, query_filename):
        with open('./queries/'+query_filename, 'r') as file:
            query = file.read()
        self.df = pd.read_gbq(query, credentials=self.credentials)
        return self.df


