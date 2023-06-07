import streamlit as st
import plotly.express as px
import requests
import pandas as pd

user_count = 0
url = "http://172.16.91.131:8080/api/scrape?scrape_type=user&action=fetch&count="

def main():
    st.title("Streamlit API Testing APP")

    # Random User
    random_user_data = requests.get(url+str(1)).json()
    df = pd.DataFrame(random_user_data)  # Parse as JSON
    # Display the DataFrame
    st.write(df)

    # Add a textbox
    user_count = st.text_input("Enter a value")

    # Add a button
    if st.button("Click me!"):
        st.write("Button clicked!")
        st.write("User input:", user_count)
    
    json_data = requests.get(url+str(user_count)).json()
    # json_str = json_data.decode('utf-8')  # Decode bytes to string
    df = pd.DataFrame(json_data)  # Parse as JSON
    
    # Display the DataFrame
    st.write(df)

    # Create a plot using Plotly Express
    fig = px.scatter(df)
    st.plotly_chart(fig)



# Test


# TEst API Endpoint : https://randomuser.me/documentation

if __name__ == '__main__':
    main()
