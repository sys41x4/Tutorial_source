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

object_dict={}

# Add Objects to object_dict
object_dict.update({'config':config})
object_dict.update({'DB_connector':DB_connector})
object_dict.update({'API':API})


# Initiate FAST API Service
app = FastAPI()

@app.get("/")
def root_index():
    return JSONResponse({"status": 200})


@app.get("/api/")
def api_info():
    return JSONResponse({"api": {"ver":"0.1.0"}})

@app.get("/api/scrape")
def scrape_user(
    scrape_type: str = '', 
    count: Optional[int] = 0, 
    randomize: Optional[bool] = False, 
    action: Optional[str] = '',
    uid: Optional[str] = '',
    email: Optional[str] = '',
    db_columns: Optional[str] = '',
    ):
    # scrape_type = user/db/live
    # count >=0
    # action = update/fetch
    # randomize = true/false
    # uid = <user uid>
    # email = <user mail>
    # db_columns = [<db_col_0>, <db_col_2> ,...]

    formated_json = {"type":scrape_type,
                     "count":count,
                     "action":action,
                     "randomize":randomize,
                     "uid":uid,
                     "email":email,
                     "db_columns":[str(col).strip() for col in db_columns.split(",")]
                     }

    

    foreign_url = "https://randomuser.me/api/?results="+str(formated_json["count"])

    data = {}
    randomize_rows_extended_query = ""
    uid_rows_extend_query = ""
    email_rows_extend_query = ""

    if(formated_json["randomize"]): randomize_rows_extended_query = "ORDER BY RAND()"

    formated_json.update({"randomize_rows_extended_query":randomize_rows_extended_query})
    formated_json.update({"uid_rows_extend_query":uid_rows_extend_query})
    formated_json.update({"email_rows_extend_query":email_rows_extend_query})
    formated_json.update({"existing_columns":existing_columns})
    formated_json.update({"foreign_url":foreign_url})


    if (formated_json['type'].upper()=="USER"):
        # Get data from connected database
        try:
            if(formated_json["action"].upper()=='FETCH'):
                data.update(API.fetch_user_data(formated_json, object_dict))
            else:
                data.update({"data":[]})

        except Exception as e:
            data.update({"err":str(e)})

        # except KeyboardInterrupt:
        #     data.update({"err":str('e')})

    elif (formated_json['type'].upper()=="DB"):
        try:
        # Update/interact with connected database
            if(formated_json["action"].upper()=='UPDATE'):

                data.update(API.update_db_data(formated_json, object_dict))

            elif (formated_json["action"].upper()=='FETCH'):

                data.update(API.fetch_db_data(formated_json, object_dict))
                
            else:
                data.update({"data":[]})
        except KeyboardInterrupt:
            data.update({"err":str('e')})

    elif (formated_json['type'].upper()=="LIVE"):
        # Fetch Direct Unformated JSON DATA from Foreign url
        data.update(API.fetch_live_data(formated_json, object_dict))

    return JSONResponse(data)


if __name__ == "__main__":
    uvicorn.run("app:app", reload=config.server["reload"], host=config.server["host"], port=config.server["port"])