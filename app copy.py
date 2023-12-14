import streamlit as st
import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import base64

# Move set_page_config to the beginning
st.set_page_config(
    page_title="Voilà - Bakery Sales Forecast",
    page_icon="🥐",
    layout="centered",
    initial_sidebar_state="auto"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    body {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: fill;
    }}
    body::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7));
        pointer-events: none;
    }}
    </style>
    '''

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

# Use the function to set background image
set_png_as_page_bg('assets/stock.jpeg')

st.image("assets/image.png", width=100)

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
    st.write('Forecast requested, please wait...')
    # st.write('Fare requested ... ')
    st.markdown("""
        <iframe src="https://giphy.com/embed/YMkogTfbM5DfBncRLO" width="480" height="270" frameborder="0" class="giphy-embed" allowfullscreen></iframe>
        <p><a href="https://giphy.com/gifs/baking-time-cookine-YMkogTfbM5DfBncRLO">via GIPHY</a></p>
    """, unsafe_allow_html=True)

    if uploaded_sales_file is not None and  uploaded_forecast_file is not None:
        data_uploaded = [
            ('files', uploaded_sales_file.getvalue()),
            ('files', uploaded_forecast_file.getvalue())
        ]

        # st.write(data_uploaded)
        url = 'https://bakerysales-qe7pmw7ita-ew.a.run.app'
        # url = 'http://0.0.0.0:8000'

        # Creating lists for saving the results
        sales_pred_tradi = []
        sales_pred_croissant = []
        sales_pred_pain_au_choc = []
        timestamp = []
        daily_pred_multi = pd.DataFrame()

        # Multiplicating the number of requests
        request_mutiplier = 5
        for i in range(request_mutiplier):
            res = requests.post(url + "/upload", files= data_uploaded).json()

            # Getting the components of the prediction: timestam and units to sell
            sales_pred_tradi=[float(x) for x in res['output']['tradi']]
            sales_pred_croissant=[float(x) for x in res['output']['croissant']]
            sales_pred_pain_au_choc=[float(x) for x in res['output']['pain_au_choc']]
            timestamp=[pd.to_datetime(x) for x in res['output']['dates']]

            # Creates a dataset with the predictions in the right format and groups by date
            df_pred = pd.DataFrame({'Dates' : timestamp,
                    'FC Traditional Baguette' :sales_pred_tradi,
                    'FC Croissant': sales_pred_croissant,
                    'FC Pain au chocolat': sales_pred_pain_au_choc
                    })
            df_pred.set_index('Dates', inplace=True)
            daily_pred = df_pred[['FC Traditional Baguette','FC Croissant', 'FC Pain au chocolat' ]].groupby(df_pred.index.date).sum().round(0)

            #Appending the newly generated prediction dataset
            daily_pred_multi = pd.concat([daily_pred_multi, daily_pred], axis =0)
        daily_predictions = daily_pred_multi.groupby(daily_pred_multi.index).median()

    # Communicating predictions
    st.success('STEP 4: Completed!')
    st.markdown (
        """ ### These are the predicted sales for next week:
        """
    )

    #Filtering results to the week requested for forecast
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
    bar_container = ax.bar(week_days, units_sold, color='#A68A64')
    ax.set(ylabel='units sold', title='Traditional baguette - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    # Displaying chart with results / Croissant
    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Croissant']
    max_y = max(daily_predictions['FC Croissant'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#936639')
    ax.set(ylabel='units sold', title='Croissant - Weekly sales forecast', ylim=(0, max_y))
    ax.bar_label(bar_container)
    st.pyplot(fig)

    # Displaying chart with results / Pain au chocolat
    plt.figure(figsize=(12,5))
    week_days = daily_predictions.index
    units_sold = daily_predictions['FC Pain au chocolat']
    max_y = max(daily_predictions['FC Pain au chocolat'])*1.1
    fig, ax = plt.subplots(figsize=(10,3))
    bar_container = ax.bar(week_days, units_sold, color='#582F0E')
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

else:
    st.write('Please complete STEPS 1, 2 and 3 and make the request.')
