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

    def sort_data_using_coord(self, original_coord=[], modified_coord=[], original_data=[], reverse=False):
        '''
        Sort uid using their coordinates
        Required:
        1. original coordinate list
        2. original data list
        3. modified coordinate list
        '''

        combined_data = zip(original_coord, original_data, modified_coord)
        # Sort the combined data based on modified coordinates
        sorted_data = sorted(combined_data, key=lambda x: x[2], reverse=reverse)

        # Extract the sorted uids
        sorted_uids = [item[1] for item in sorted_data]

        return sorted_uids

    def sort_coord(self, arg_dict={}):
        data = {}
        try:
            api_endpoint = arg_dict["api_endpoint"]
            url = api_endpoint+'?'+'&'.join([f"{key}={value}" for key, value in arg_dict.items()])

            res = requests.get(url)
            data.update(res.json()) # Random User Data

        except Exception as e:
            data.update({"err":str(e)})

        return data        


        

        