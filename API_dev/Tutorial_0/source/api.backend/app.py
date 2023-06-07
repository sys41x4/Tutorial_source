import os, io, sys
import ujson
from typing import Optional, Union, List
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd

from modules import configurator, db_connector, api


print("--- API Workouts ---")

# users_to_fetch = 5
# foreign_url = "https://randomuser.me/api/?results="+str(users_to_fetch)


# sys.argv assignments
# Format : python3 <filename>.py <BASE_CONFIG_FILE_PATH>
#          BASE_CONFIG_FILE_PATH | format: JSON

def help_msg():
    help_info = """
Format : python3 "+sys.argv[0]+" <BASE_CONFIG_FILE_PATH>
         BASE_CONFIG_FILE_PATH | format: JSON
"""

try:
    if(len(sys.argv)>1):
        if(sys.argv[1].lower()=='help'):
            print(help_msg)
            sys.exit()
        base_config_fp = sys.argv[1]
    else:
        base_config_fp = '/etc/test.app/config/config.json'

    config = configurator.Config(base_config_fp)
    config.load()

except Exception as e:
   print(help_msg())
   print(e)
   sys.exit()

# Data Will only be entered in these fields only
existing_columns = {
    'user': {
        'db_col':('uid', 'email', 'first_name', 'last_name'),
        'remote_api_col':('login.uuid', 'email', 'name.first', 'name.last')
    }, 
    'user_details': {
        'db_col':('uid', 'gender', 'latitude', 'longitude', 'datetime'),
        'remote_api_col':('login.uuid', 'gender', 'location.coordinates.latitude', 'location.coordinates.longitude', 'registered.date'),
    }
}


# generate Database Interaction object
DB_connector = db_connector.Database(config.db["service"])
DB_connector.connect(config.db["host"], config.db["port"], config.db["db_name"], config.db["db_user"], config.db["db_pass"]) # Connect with the Service

# API Connector
API = api.api()

# Initiate FAST API Service
app = FastAPI()

@app.get("/")
def root_index():
    return JSONResponse({"status": 200})


@app.get("/api/")
def api_info():
    return JSONResponse({"api": {"ver":"0.1.0"}})

@app.get("/api/scrape")
def scrape_user(scrape_type: str = '', count: Optional[int] = 0, randomize: Optional[bool] = False, action: Optional[str] = ''):
    # scrape_type = user/db/live
    # count >=0
    # action = update/fetch
    # randomize = true/false

    formated_json = {"type":scrape_type,
                     "count":count,
                     "action":action,
                     "randomize":randomize
                     }

    foreign_url = "https://randomuser.me/api/?results="+str(formated_json["count"])

    data = {}
    randomize_rows_extended_query = ""
    if(formated_json["randomize"]): randomize_rows_extended_query = "ORDER BY RAND()"

    if (formated_json['type'].upper()=="USER"):
        # Get data from connected database
        try:
            if(formated_json["action"].upper()=='FETCH'):
                data.update({"data": []})
                # json_data={}

                db_tables = tuple(existing_columns.keys())
                
                uid_reference = db_tables[0]

                db_col = [col for table in existing_columns for col in existing_columns[table]['db_col']]

                rows = DB_connector.query_fetch(f"""
                SELECT * FROM {', '.join(db_tables)}
                WHERE {'.uid = {uid_reference}.uid AND '.join(db_tables[1::])}.uid = {uid_reference}.uid
                {randomize_rows_extended_query}
                LIMIT """+str(formated_json["count"])+';')

                df = pd.DataFrame(rows, columns=db_col)
                # json_data.update(df.to_json(orient='records')

                data["data"] = df.to_dict(orient='records')
            else:
                data.update({"data":[]})

        except Exception as e:
            data.update({"err":str(e)})

    elif (formated_json['type'].upper()=="DB"):
        try:
        # Update/interact with connected database
            if(formated_json["action"].upper()=='UPDATE'):

                if (formated_json["count"]>0):
                    # Update db with new Values if count is greater than 0
                    
                    df_pre = API.json_normalize(API.get_json_data(foreign_url)["results"])

                    # Get Current Column from the Connected Database

                    
                    for i in range(len(existing_columns)):
                        db_table = tuple(existing_columns.keys())[i]
                        # print(df_pre.columns)
                        df = df_pre[list(existing_columns[db_table]['remote_api_col'])]
                        df.columns = existing_columns[db_table]['db_col']

                        for _, row in df.iterrows():
                            
                            row = row.astype(str)

                        
                            # Insert in to user table
                            
                            # print(type(row))
                            
                            values = ', '.join(['"'+value.replace('\'', '"')+'"' for value in row])
                            query = f"INSERT INTO {db_table} ({', '.join([col.replace('.', '_') for col in existing_columns[db_table]['db_col']])}) VALUES ({values})"

                            try:
                                DB_connector.query_exec(query)
                            except Exception as e:
                                print(f"Failed to insert data: {e}")

                    DB_connector.commit() # After Structing the data, commit changes to take place


                data.update({"data":f"Updated DB With {str(formated_json['count'])} Entries"})

            elif (formated_json["action"].upper()=='FETCH'):
                data.update({"data": []})
                # json_data={}

                db_tables = tuple(existing_columns.keys())
                
                uid_reference = db_tables[0]

                db_col = [col for table in existing_columns for col in existing_columns[table]['db_col']]

                rows = DB_connector.query_fetch(f"""
                SELECT * FROM {', '.join(db_tables)}
                WHERE {'.uid = {uid_reference}.uid AND '.join(db_tables[1::])}.uid = {uid_reference}.uid
                {randomize_rows_extended_query}
                LIMIT """+str(formated_json["count"])+';')

                df = pd.DataFrame(rows, columns=db_col)

                data["data"] = df.to_dict(orient='records')
                
            else:
                data.update({"data":[]})
        except KeyboardInterrupt:
            data.update({"err":str('e')})

    elif (formated_json['type'].upper()=="LIVE"):
        # Fetch Direct Unformated JSON DATA from Foreign url
        try:
            selected_columns = [col for table in existing_columns for col in existing_columns[table]['remote_api_col']]
            selected_db_columns = [col for table in existing_columns for col in existing_columns[table]['db_col']]
            
            df = API.json_normalize(API.get_json_data(foreign_url)["results"])
            df_filtered = df[selected_columns]
            df_filtered.columns = selected_db_columns
            # df_filtered=df.to_dict(orient='records')
            # print(type(df_filtered))
            # data.update({"data":df_filtered})
            data.update({"data":df_filtered.to_dict(orient='records')})

        except Exception as e:
            data.update({"err":str(e)})

    return JSONResponse(data)


if __name__ == "__main__":
    uvicorn.run("app:app", reload=config.server["reload"], host=config.server["host"], port=config.server["port"])