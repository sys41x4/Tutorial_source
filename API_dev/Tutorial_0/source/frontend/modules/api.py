import requests
import math
import pandas as pd

class api:
    def __init__(self,):
        ''''''

    def get_random_user(self, arg_dict={}):
        ''''''
        data = {}
        try:
            api_endpoint = arg_dict["api_endpoint"]
            total_users = arg_dict["count"]
            columns = arg_dict["columns"]

            res = requests.get(api_endpoint+f"?scrape_type=user&db_columns={','.join(columns)}&randomize=1&count={str(total_users)}&action=fetch")
            data.update(res.json()) # Random User Data

        except Exception as e:
            data.update({"err":str(e)})

        return data

        