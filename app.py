import streamlit as st
from emoji import emojize

import requests
import datetime
import pandas as pd

import os
import subprocess
import json

st.set_page_config(
    page_title="Voilà - Bakery Sales Forecast", # => Voilà - Bakery Sales Forecast - Streamlit
    page_icon="🥐",
    layout="centered", # wide
    initial_sidebar_state="auto") # collapsed



CSS = """
h1 {
    color: black;
}
body {
    background-color: #92a8d1;
    }
# .stApp {
#     background-image: url(https://avatars1.githubusercontent.com/u/9978111?v=4);
#     background-size: cover;
#     opacity: 0.5;
# }
.stImage {
    background-image: url(https://avatars1.githubusercontent.com/u/9978111?v=4);
    background-size: cover;
    opacity: 0.5;
}
"""

if st.checkbox('Inject CSS'):
    st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)


st.markdown("""
            # 🥖Voilà - Bakery Sales Forecast🥐

            ## Welcome to *Voilà - Bakery Sales Forecast's* user interface.

            In order to get the sales forecast for the next week, please follow these steps:

            - **STEP 1:** Select the week start date. (The first day of the week must be Monday)
            - **STEP 2:** Upload previous week's actual sales as a .csv file
            - **STEP 3:** Upload next week's weather forecast as a .csv file
            - **STEP 4:** Press the "Get forecast" button

            ... and **Voilà** get the expected sales for next week and optimize your production to the most!


            """
)

# STEP 1: Selecting the start date of the week

today = datetime.date.today()
# test = datetime.datetime.today().weekday()

start_date = st.date_input("**STEP 1: Please select the week's start date (Monday)**", today)
end_date = start_date + datetime.timedelta(days=7)

if start_date.weekday() == 0:
    st.success('STEP 1 completed! The forecasted week will start on `%s` and ends on `%s`' % (start_date, end_date))
else:
    st.error('Error: Start date must correspond to a Monday')

# STEP 2: Uploading sales file

# st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_sales_file = st.file_uploader("**STEP 2: Upload a CSV file with the previous week sales**", type="csv")

if uploaded_sales_file is not None:
    data = pd.read_csv(uploaded_sales_file)
    st.write(data.head(3))
    st.success("STEP 2: Completed! Last week's sales have been successfully uploaded.")

# STEP 3: Uploading weather forecast file

# st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_forecast_file = st.file_uploader("**STEP 3: Upload a CSV file with next week's weather forecast**", type="csv")

if uploaded_forecast_file is not None:
    data = pd.read_csv(uploaded_forecast_file)
    st.write(data.head(3))
    st.success("STEP 3: Completed!'Next week's weather forecast has been successfully uploaded.")

# Button for triggering the request to API
if st.button('**Get forecast 🥐**'):
    # print is visible in the server output, not in the page
    st.write('Forecast requested!')
    # st.write('Fare requested ... ')

    if uploaded_sales_file is not None and  uploaded_forecast_file is not None:
            data_uploaded = {
                'sales_data' : uploaded_sales_file,
                'weather_data' : uploaded_forecast_file
            }
            url = 'https://xxxxxew.a.run.app'
            # url = 'http://0.0.0.0:8000'

            res = requests.post(url + "/predict_pickle", files=data_uploaded).json()

            if st.checkbox('Show forecast file upload progress bar'):

                import time
                'Forecast file is being uploaded, please wait...'

                # Add a placeholder
                latest_iteration = st.empty()
                bar = st.progress(0)
                for i in range(100):
                    # Update the progress bar with each iteration.
                    latest_iteration.text(f'Upload % {i+1}')
                    bar.progress(i + 1)
                    time.sleep(0.02)

    # Getting the components of the prediction: timestam and units to sell
    # sales_prediction = res['output']['values']   ### CHNAGE FROM STRING TO FLOAT
    sales_prediction = res['output']['values'].astype(float)
    timestamp = [pd.to_datetime(x) for x in res['output']['dates'] ]
    st.success('STEP 4: Completed!')

    # Generating the predictions dataset
    # Guild the dictionary for the POST request
    df_pref = pd.DataFrame({'Dates' : timestamp,
                        'Sales Predictions' :sales_prediction})
    # Communicating predictions
    st.markdown (
        """ ### These are the predicted sales for next week:
        """
    )
    df_pred.set_index('Dates', inplace=True)

    daily_predictions = df_pred[['Sales Predictions']].groupby(df_pred.index.date).sum()

    daily_predictions = daily_predictions[(daily_predictions.index >= start_date)
                   & (daily_predictions.index <= end_date)]

    # Displaying tabular results
    daily_predictions

    # Displaying chart with results
    plt.figure(figsize=(12,5));
    week_days = daily_predictions.index;
    units_sold = daily_predictions['prediction'];
    max_y = max(daily_predictions['prediction'])*1.1;
    fig, ax = plt.subplots(figsize=(10,3));
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69');
    ax.set(ylabel='units sold', title='Weekly sales forecast', ylim=(0, max_y));
    ax.bar_label(bar_container, fmt='{:,.0f}');
    plt.show();

    # response = requests.get(url,params=params).json()
    #st.write(f"Your estimated fare is: {round(response['fare'],2)} USD.")
else:
    st.write('Please complete STEPS 1, 2 and 3 and make the request.')
