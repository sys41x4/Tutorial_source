import os, io, sys
import ujson
from typing import Optional, Union, List
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn

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
def scrape_user(scrape_type: str = '', count: Optional[int] = 0, action: Optional[str] = ''):
    # scrape_type = user/db /live
    # count >=0
    # action = update/fetch

    formated_json = {"type":scrape_type,
                     "count":count,
                     "action":action
                     }

    foreign_url = "https://randomuser.me/api/?results="+str(formated_json["count"])

    data = {}

    if (formated_json['type'].upper()=="USER"):
        # Get data from connected database
        try:
            if(formated_json["action"].upper()=='FETCH'):
                data.update({"data": DB_connector.query_fetch("""
                SELECT * FROM user_info
                ORDER BY RAND()
                LIMIT """+str(formated_json["count"])+';')})
            else:
                data.update({"data":''})

        except Exception as e:
            data.update({"err":str(e)})

    elif (formated_json['type'].upper()=="DB"):
        try:
        # Update/interact with connected database
            if(formated_json["action"].upper()=='UPDATE'):

                if (formated_json["count"]>0):
                    # Update db with new Values if count is greater than 0

                    # Get Data from remote url
                    df = API.json_normalize(API.get_json_data(foreign_url)["results"])

                    # Get Current Column from the Connected Database
                    existing_columns = []
                    res = DB_connector.query_exec("SHOW COLUMNS FROM user_info")
                    existing_columns = [column[0] for column in res]
                    

                    for column in df.columns:
                        if column not in existing_columns:
                            column_type = 'VARCHAR(255)'  # Adjust the column type as per your requirements
                            try:
                                DB_connector.query_exec(f"ALTER TABLE user_info ADD COLUMN {column.replace('.', '_')} {column_type}")
                                print(f"Added column '{column.replace('.', '_')}' to the table.")
                                existing_columns.append(column.replace('.', '_'))
                            except Exception as e:
                                print(f"Failed to add column '{column.replace('.', '_')}': {e}")

                    keys = ', '.join([col.replace('.', '_') for col in df.columns])

                    for _, row in df.iterrows():
                        
                        row = row.astype(str)
                        values = ', '.join(['"'+value.replace('\'', '"')+'"' for value in row])
                        insert_statement = f"INSERT INTO user_info ({keys}) VALUES ({values})"
                        print(insert_statement)
                        try:
                            DB_connector.query_exec(insert_statement)
                        except Exception as e:
                            print(f"Failed to insert data: {e}")
                    DB_connector.commit() # After Structing the data, commit changes to take place


                data.update({"data":f"Updated DB With {str(formated_json['count'])} Entries"})

            elif (formated_json["action"].upper()=='FETCH'):
                data.update({"data": DB_connector.query_fetch("""
                SELECT * FROM user_info
                ORDER BY RAND()
                LIMIT """+str(formated_json["count"])+';')})
            else:
                data.update({"data":''})
        except Exception as e:
            data.update({"err":str(e)})

    elif (formated_json['type'].upper()=="LIVE"):
        # Fetch Direct Unformated JSON DATA from Foreign url
        try:
            data.update({"data":API.get_json_data(foreign_url)["results"]})
        except Exception as e:
            data.update({"err":str(e)})

    return JSONResponse(data)


if __name__ == "__main__":
    uvicorn.run("app:app", reload=config.server["reload"], host=config.server["host"], port=config.server["port"])