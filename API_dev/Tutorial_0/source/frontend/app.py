import streamlit as st
import plotly.express as px
import requests
import pandas as pd
import numpy as np
import folium
import random

from modules import api

api_host = "http://172.16.91.131:8080"

API = api.api()

data = {}






def main():
    st.title("Streamlit API Testing Frontend")
    json_data = {}

    # Buttons
    if st.button('Get Random User'):
        json_data.update({"api_endpoint":api_host+'/api/scrape', 'count':1, 'columns':['user.uid', 'user.email', 'user_details.latitude', 'user_details.longitude']})
        # Assume that the first entry will be our current user

        current_user_data = API.get_random_user(json_data)
        if('data' in current_user_data):
            df_current = pd.json_normalize(current_user_data['data'])
        

            df_current.rename(columns={'user_details.latitude': 'latitude'}, inplace=True)
            df_current.rename(columns={'user_details.longitude': 'longitude'}, inplace=True)
            df_current['latitude'] = df_current['latitude'].astype(float)
            df_current['longitude'] = df_current['longitude'].astype(float)

            st.write("Current Random User")
            st.write(df_current)

            st.write("Current Users Map")
            st.map(df_current)


            json_data.update({"api_endpoint":api_host+'/api/scrape', 'count':random.randint(1, 30), 'columns':['user.uid', 'user.email', 'user_details.latitude', 'user_details.longitude']})
            other_user_data = API.get_random_user(json_data)

            if('data' in other_user_data):
                df_others = pd.json_normalize(other_user_data['data'])
                df_others.rename(columns={'user_details.latitude': 'latitude'}, inplace=True)
                df_others.rename(columns={'user_details.longitude': 'longitude'}, inplace=True)
                df_others['latitude'] = df_others['latitude'].astype(float)
                df_others['longitude'] = df_others['longitude'].astype(float)


                st.write("Other Users")
                st.write(df_others)

                st.write("Other Users Map")
                st.map(df_others)

            # Get coordinate of current user and other to short
            # Assuming we have to get top 10 nearest users

            # Get current_user's location
            current_user_coordinates = f"{str(df_current['latitude'].iloc[0])},{str(df_current['longitude'].iloc[0])}"

            # Get Other_user's location
            others_coordinates = str(list(zip(df_others['latitude'], df_others['longitude']))).replace(' ', '')[1:-1]
            
            json_data = {}
            # Sort others_coordinates with reference to current_user's coordinate
            json_data.update({"api_endpoint":api_host+'/api/coordinates', 'origin':current_user_coordinates, 'coordinates':others_coordinates, 'reverse':0})

            others_sorted_coordinates = API.sort_coord(json_data) # This will get the sorted coordinates of other users
            
            if('data' in others_sorted_coordinates):
                others_sorted_coordinates = others_sorted_coordinates['data']
                others_sorted_uids = API.sort_data_using_coord(others_coordinates, others_sorted_coordinates, df_others['user.uid'].tolist())
                
                # Sort df_others according to sorted uids
                latitude_list = [float(coord[0]) for coord in others_sorted_coordinates]
                longitude_list = [float(coord[1]) for coord in others_sorted_coordinates]
                data = {'uid': others_sorted_uids, 'latitude': latitude_list, 'longitude': longitude_list}
                df_others_sorted = pd.DataFrame(data)




                total_others_mapped_users = 5 # It ensures that only top x nearest users are to be mapped

                st.write(f"Top {total_others_mapped_users} nearest Users")
                st.write(df_others_sorted)

                st.write("Sorted Other Users Map")
                st.map(df_others_sorted.head(total_others_mapped_users))

if __name__ == '__main__':
    main()
