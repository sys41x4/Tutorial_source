import requests
import pandas as pd

class api:
    def __init__(self,):
        ''''''

    def get_json_data(self, url):
        data = requests.get(url)
        return data.json()

    def dump_json_to_csv(self, fp, data):
        # Using pandas to dump data
        df = pd.json_normalize(API.get_json_data(url)['results'])
        df.to_csv(data_out_fp, index=False)

    def json_normalize(self, json_data):
        return pd.json_normalize(json_data)