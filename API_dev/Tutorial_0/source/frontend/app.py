import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import numpy as np
import folium

from modules import api

api_host = "http://172.16.91.131:8080"

API = api.api()

data = {}


json_data = {}



def main():
    st.title("Streamlit API Testing Frontend")


    # Buttons
    if st.button('Get Random User'):
        json_data.update({"api_endpoint":api_host+'/api/scrape', 'count':10, 'columns':['user.uid', 'user.email', 'user_details.latitude', 'user_details.longitude']})
        # Assume that the first entry will be our current user

        data = API.get_random_user(json_data)
        if('data' in data):
            df = pd.json_normalize(data['data'])
        

        df.rename(columns={'user_details.latitude': 'latitude'}, inplace=True)
        df.rename(columns={'user_details.longitude': 'longitude'}, inplace=True)

        st.write("Current Random User")
        st.write(df)

        
        # Extract latitude and longitude columns from the DataFrame
        latitude_list = [float(lat) for lat in df['latitude'].tolist()]
        longitude_list = [float(lon) for lon in df['longitude'].tolist()]
        coordinate_tuples = list(zip(latitude_list, longitude_list))
        df_map = pd.DataFrame(coordinate_tuples,columns=['latitude', 'longitude'])


        # Create coordinate tuples
        # coordinate_tuples = list(zip(latitude_list, longitude_list))

        # Plot map using st.map()
        st.map(df_map)

if __name__ == '__main__':
    main()
