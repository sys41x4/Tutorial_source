import sys, os
import ujson

class Config:
    def __init__(self, base_config_fp):
        '''Load core config data'''
        if(os.path.isfile(base_config_fp)):
            self.base_config_data = self.get_json_data(base_config_fp)
            print("Base CONFIG | Loaded Successfully | :)")
        else:
            print("\n\nBase CONFIG PATH | Not Found : at "+base_config_fp+" | :/")
            sys.exit()

    def get_json_data(self, fp):
        '''Get JSON File Data'''
        with open(fp, 'r') as f:
            data = ujson.loads(f.read())
        return data

    def get_server(self, config_fp=''):
        '''Get Server Loader Config File'''
        return self.get_json_data(config_fp)

    def load(self,):
        '''LOAD CONFIG Data'''
        try:
            # Load server_info | config
            if(os.path.isfile(self.base_config_data['fp_server_config'])):
                self.server = self.get_json_data(self.base_config_data['fp_server_config'])
                print("[\\0/] SUCCESS | SERVER CONFIG | Loaded Successfully")
            else:
                print("[X] FAILED | SERVER CONFIG FilePath | Not Found")
        except Exception as e:
            print(e)

        try:
            # Load DB Config Data
            if(os.path.isfile(self.base_config_data['fp_db_config'])):
                self.db = self.get_json_data(self.base_config_data['fp_db_config'])
                print("[\\0/] SUCCESS | DB CONFIG | Loaded Successfully")
            else:
                print("[X] FAILED | DB CONFIG FilePath | Not Found")
        except Exception as e:
            print(e)