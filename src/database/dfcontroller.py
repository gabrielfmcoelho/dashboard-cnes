import pandas as pd
import numpy as np
from lazy import lazy

class DfController:
    df = pd.DataFrame()

    def __init__(self):
        pass

    def get_df(self):
        return self.__class__.df
    
    def update_df(self, df):
        self.__class__.df = df