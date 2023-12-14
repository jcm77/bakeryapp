import streamlit as st
import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Add an image using HTML and CSS
image_html = """
    <div style="text-align:center; background-color: #FF0000; padding: 20px;">
        <img src="https://example.com/your_image_url.jpg" alt="Bakery Image" width="300"/>
    </div>
"""

st.markdown(image_html, unsafe_allow_html=True)

st.set_page_config(
    page_title="Voilà - Bakery Sales Forecast",
    page_icon="🥐",
    layout="centered",
    initial_sidebar_state="auto"
)

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
start_date = st.date_input("**STEP 1: Please select the week's start date (Monday)**", today)
end_date = start_date + datetime.timedelta(days=7)

if start_date.weekday() == 0:
    st.success('STEP 1 completed! The forecasted week will start on `%s` and ends on `%s`' % (start_date, end_date))
else:
    st.error('Error: Start date must correspond to a Monday')

# STEP 2: Uploading sales file
uploaded_sales_file = st.file_uploader("**STEP 2: Upload a CSV file with the previous week sales**", type="csv")

if uploaded_sales_file is not None:
    data = pd.read_csv(uploaded_sales_file)
    st.write(data.head(3))
    st.success("STEP 2: Completed! Last week's sales have been successfully uploaded.")

# STEP 3: Uploading weather forecast file
uploaded_forecast_file = st.file_uploader("**STEP 3: Upload a CSV file with next week's weather forecast**", type="csv")

if uploaded_forecast_file is not None:
    data = pd.read_csv(uploaded_forecast_file)
    st.write(data.head(3))
    st.success("STEP 3: Completed! Next week's weather forecast has been successfully uploaded.")

# Button for triggering the request to API
if st.button('**Get forecast 🥐**'):
    st.write('Forecast requested!')

    if uploaded_sales_file is not None and  uploaded_forecast_file is not None:
        data_uploaded = [
            ('files', uploaded_sales_file.getvalue()),
            ('files', uploaded_forecast_file.getvalue())
        ]

        url = 'https://bakerysales-qe7pmw7ita-ew.a.run.app'

        sales_pred_tradi = []
        sales_pred_croissant = []
        sales_pred_pain_au_choc = []
        timestamp = []
        daily_pred_multi = pd.DataFrame()

        request_mutiplier = 5
        for i in range(request_mutiplier):
            res = requests.post(url + "/upload", files= data_uploaded).json()

            sales_pred_tradi=[float(x) for x in res['output']['tradi']]
            sales_pred_croissant=[float(x) for x in res['output']['croissant']]
            sales_pred_pain_au_choc=[float(x) for x in res['output']['pain_au_choc']]
            timestamp=[pd.to_datetime(x) for x in res['output']['dates']]

            df_pred = pd.DataFrame({'Dates' : timestamp,
                    'FC Traditional Baguette' :sales_pred_tradi,
                    'FC Croissant': sales_pred_croissant,
                    'FC Pain au chocolat': sales_pred_pain_au_choc
                    })
            df_pred.set_index('Dates', inplace=True)
            daily_pred = df_pred[['FC Traditional Baguette','FC Croissant', 'FC Pain au chocolat' ]].groupby(df_pred.index.date).sum().round(0)

            daily_pred_multi = pd.concat([daily_pred_multi, daily_pred], axis =0)
        daily_predictions = daily_pred_multi.groupby(daily_pred_multi.index).median()

    st.success('STEP 4: Completed!')
    st.markdown (
        """ ### These are the predicted sales for next week:
        """
    )

    daily_predictions = daily_predictions[(daily_predictions.index >= pd.to_datetime(start_date).date())
                  & (daily_predictions.index <= pd.to_datetime(end_date).date())]

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

    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Traditional Baguette']
    max_y = max(daily_predictions['FC Traditional Baguette'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Traditional baguette - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Croissant']
    max_y = max(daily_predictions['FC Croissant'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Croissant - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Pain au chocolat']
    max_y = max(daily_predictions['FC Pain au chocolat'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#4A4E69')
    ax.set(ylabel='units sold', title='Pain au chocolat - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)
