import requests
import math
import pandas as pd


class api:
    def __init__(self,):
        ''''''

    def get_json_data(self, url):
        data={}
        try:
            data = requests.get(url)
            data = data.json()
        except Exception as e:
            data.update({'err':str(e)})
        return data
        

    def dump_json_to_csv(self, fp, data):
        # Using pandas to dump data
        df = pd.json_normalize(self.get_json_data(url)['results'])
        df.to_csv(data_out_fp, index=False)

    def json_normalize(self, json_data):
        return pd.json_normalize(json_data)

    def calculate_distance(self, coord, origin):
        x1, y1 = coord
        x2, y2 = origin
        return math.hypot(x2 - x1, y2 - y1)


    def sort_coordinates(self, origin_coord=[0, 0], coord_list=[(0,0)], reverse_sort=False):
        '''
        sort_by: 0/1 [0: ascending_order, 1: descending_order]
        '''
        data={}

        try:

            sorted_coordinates = sorted(coord_list, key=lambda coord: self.calculate_distance(coord, origin_coord), reverse=reverse_sort)
            data.update({"data":sorted_coordinates})

        except Exception as e:
            data.update({"err":str(e)})

        return data

    def fetch_db_data(self, arg_dict={}, object_dict={}):

        data={}
        
        try:
            
            data.update({"data": []})
            # json_data={}

            db_tables = tuple(arg_dict['existing_columns'].keys())
            
            uid_reference = db_tables[0]

            if(arg_dict["uid"]!=''):arg_dict['uid_rows_extend_query'] = f'{uid_reference}.uid = "{str(arg_dict["uid"])}" AND '
            if(arg_dict["email"]!=''):arg_dict['email_rows_extend_query'] = f'{uid_reference}.email = "{str(arg_dict["email"])}" AND '
            


            db_col = arg_dict['db_columns']

            if('*' in arg_dict['db_columns']):
                arg_dict['db_columns'] = ['*']
                db_col = [col for table in arg_dict['existing_columns'] for col in arg_dict['existing_columns'][table]['db_col']]

            query = f"""
            SELECT {', '.join(arg_dict['db_columns'])} FROM {', '.join(db_tables)}
            WHERE  {arg_dict['uid_rows_extend_query']} {arg_dict['email_rows_extend_query']}
            {'.uid = {uid_reference}.uid AND '.join(db_tables[1::])}.uid = {uid_reference}.uid
            {arg_dict['randomize_rows_extended_query']}
            LIMIT """+str(arg_dict["count"])+';'
            # print(query)

            rows = object_dict['DB_connector'].query_fetch(query)
            # print(db_col, rows)

            df = pd.DataFrame(rows, columns=db_col)
            
            # json_data.update(df.to_json(orient='records')
            
            data["data"] = df.to_dict(orient='records')

        except Exception as e:
            data.update({"err":str(e)})

        # except KeyboardInterrupt:
        #     data.update({"err":str('e')})

        return data

    def fetch_user_data(self, arg_dict={}, object_dict={}):
        '''
        Currently This Function does work same as fetch_db_data(arg_dict)
        '''
        return self.fetch_db_data(arg_dict, object_dict)

    def fetch_live_data(self, arg_dict={}):
        '''
        Fetch Live daa from remote api end point
        '''

        data={}

        try:
            selected_columns = [col for table in arg_dict['existing_columns'] for col in arg_dict['existing_columns'][table]['remote_api_col']]
            selected_db_columns = [col for table in arg_dict['existing_columns'] for col in arg_dict['existing_columns'][table]['db_col']]
            
            df = self.json_normalize(self.get_json_data(arg_dict['foreign_url'])["results"])
            df_filtered = df[selected_columns]
            df_filtered.columns = selected_db_columns
            # df_filtered=df.to_dict(orient='records')
            # print(type(df_filtered))
            # data.update({"data":df_filtered})
            data.update({"data":df_filtered.to_dict(orient='records')})

        except Exception as e:
            data.update({"err":str(e)})

        return data


    def update_db_data(self, arg_dict={}, object_dict={}):
        '''
        Update DB Data
        '''
        data = {}
        try:
            if (arg_dict["count"]>0):
                # Update db with new Values if count is greater than 0
                
                df_pre = self.json_normalize(self.get_json_data(arg_dict['foreign_url'])["results"])

                # Get Current Column from the Connected Database

                
                for i in range(len(arg_dict['existing_columns'])):
                    db_table = tuple(arg_dict['existing_columns'].keys())[i]
                    # print(df_pre.columns)
                    df = df_pre[list(arg_dict['existing_columns'][db_table]['remote_api_col'])]
                    df.columns = arg_dict['existing_columns'][db_table]['db_col']

                    for _, row in df.iterrows():
                        
                        row = row.astype(str)

                    
                        # Insert in to user table
                        
                        # print(type(row))
                        
                        values = ', '.join(['"'+value.replace('\'', '"')+'"' for value in row])
                        query = f"INSERT INTO {db_table} ({', '.join([col.replace('.', '_') for col in arg_dict['existing_columns'][db_table]['db_col']])}) VALUES ({values})"

                        try:
                            object_dict['DB_connector'].query_exec(query)
                        except Exception as e:
                            print(f"Failed to insert data: {e}")

                object_dict['DB_connector'].commit() # After Structing the data, commit changes to take place


            data.update({"data":f"Updated DB With {str(arg_dict['count'])} Entries"})

        except KeyboardInterrupt:
            data.update({"err":str('e')})

        return data