import streamlit as st
# from emoji import emojize

import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# import os
# import subprocess
# import json

st.set_page_config(
    page_title="Voilà - Bakery Sales Forecast", # => Voilà - Bakery Sales Forecast - Streamlit
    page_icon="🥐",
    layout="centered", # wide, centered
    initial_sidebar_state="auto") # collapsed

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
    st.success("STEP 3: Completed!Next week's weather forecast has been successfully uploaded.")

# Button for triggering the request to API
if st.button('**Get forecast 🥐**'):
    # print is visible in the server output, not in the page
    st.write('Forecast requested!')
    # st.write('Fare requested ... ')

    if uploaded_sales_file is not None and  uploaded_forecast_file is not None:
            data_uploaded = [
                ('files', uploaded_sales_file.getvalue()),
                ('files', uploaded_forecast_file.getvalue())
            ]

            # st.write(data_uploaded)
            url = 'https://bakerysales-qe7pmw7ita-ew.a.run.app'
            # url = 'http://0.0.0.0:8000'

            res = requests.post(url + "/upload", files= data_uploaded).json()
            #st.json(res)

            # if st.checkbox('Show forecast file upload progress bar'):

            #     import time
            #     'Forecast file is being uploaded, please wait...'

            #     # Add a placeholder
            #     latest_iteration = st.empty()
            #     bar = st.progress(0)
            #     for i in range(100):
            #         # Update the progress bar with each iteration.
            #         latest_iteration.text(f'Upload % {i+1}')
            #         bar.progress(i + 1)
            #         time.sleep(0.02)

    # Getting the components of the prediction: timestam and units to sell
    # sales_prediction = res['output']['values']   ### CHANGE FROM STRING TO FLOAT
    sales_pred_tradi = [float(x) for x in res['output']['tradi']]
    sales_pred_croissant = [float(x) for x in res['output']['croissant']]
    sales_pred_pain_au_choc = [float(x) for x in res['output']['pain_au_choc']]
    timestamp = [pd.to_datetime(x) for x in res['output']['dates']]
    st.success('STEP 4: Completed!')

    # Generating the predictions dataset
    # Guild the dictionary for the POST request
    df_pred = pd.DataFrame({'Dates' : timestamp,
                        'FC Traditional Baguette' :sales_pred_tradi,
                        'FC Croissant': sales_pred_croissant,
                        'FC Pain au chocolat': sales_pred_pain_au_choc
                        })
    # Communicating predictions
    st.markdown (
        """ ### These are the predicted sales for next week:
        """
    )
    df_pred.set_index('Dates', inplace=True)

    daily_predictions = df_pred[['FC Traditional Baguette','FC Croissant', 'FC Pain au chocolat' ]].groupby(df_pred.index.date).sum().round(0)


    daily_predictions = daily_predictions[(daily_predictions.index >= pd.to_datetime(start_date).date())
                  & (daily_predictions.index <= pd.to_datetime(end_date).date())]

    # Displaying tabular results
    st.data_editor(
        daily_predictions,
        column_config={
            'Sales Predictions': st.column_config.NumberColumn(
                'Number of units forecasted',
                help ='Number of units forecasted',
                format ='%i'
            )
        },

    )

    # Displaying chart with results / traditional baguette
    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Traditional Baguette']
    max_y = max(daily_predictions['FC Traditional Baguette'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Traditional baguette - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    # Displaying chart with results / Croissant
    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Croissant']
    max_y = max(daily_predictions['FC Croissant'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Croissant - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    # Displaying chart with results / Pain au chocolat
    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Pain au chocolat']
    max_y = max(daily_predictions['FC Pain au chocolat'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Pain au chocolat - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)



    # Generating chart with 3 bars grouped
    week_days = daily_predictions.index
    daily_preds = {
        'FC Traditional Baguette': list(daily_predictions['FC Traditional Baguette']),
        'FC Croissant':list(daily_predictions['FC Croissant']),
        'FC Pain au chocolat':list(daily_predictions['FC Pain au chocolat'])
    }

#     x = np.arange(len(week_days))

#     width = 0.25 # the witdh of the bars
#     multiplier = 0

#     fig, ax = plt.subplots(layout='constrained')

#     for attribute, measurement in daily_preds.items():
#         offset = width * multiplier
#         rects = ax.bar(x + offset, measurement, width, label=attribute)
#         ax.bar_label(rects, padding=3)
#         multiplier += 1

#    # Add some text for labels, title and custom x-axis tick labels, etc.
#     ax.set_ylabel('Units sold')
#     ax.set_title('Weekly Sales Forecast')
#     ax.set_xticks(x + width, week_days)
#     ax.legend(loc='upper left')
#     ax.set_ylim(0, 150)
#     st.pyplot(fig)



else:
    st.write('Please complete STEPS 1, 2 and 3 and make the request.')
