from matplotlib.backends.backend_agg import RendererAgg
import streamlit as st
import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt



st.set_option('deprecation.showPyplotGlobalUse', False)

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

st.title('State-Wise Covid-19 Vaccination Appointment Finder')
st.header('Finds available Vaccination Appointments by District')

state_index = {'Andaman and Nicobar Islands': 1,
 'Andhra Pradesh': 2,
 'Arunachal Pradesh': 3,
 'Assam': 4,
 'Bihar': 5,
 'Chandigarh': 6,
 'Chhattisgarh': 7,
 'Dadra and Nagar Haveli': 8,
 'Daman and Diu': 37,
 'Delhi': 9,
 'Goa': 10,
 'Gujarat': 11,
 'Haryana': 12,
 'Himachal Pradesh': 13,
 'Jammu and Kashmir': 14,
 'Jharkhand': 15,
 'Karnataka': 16,
 'Kerala': 17,
 'Ladakh': 18,
 'Lakshadweep': 19,
 'Madhya Pradesh': 20,
 'Maharashtra': 21,
 'Manipur': 22,
 'Meghalaya': 23,
 'Mizoram': 24,
 'Nagaland': 25,
 'Odisha': 26,
 'Puducherry': 27,
 'Punjab': 28,
 'Rajasthan': 29,
 'Sikkim': 30,
 'Tamil Nadu': 31,
 'Telangana': 32,
 'Tripura': 33,
 'Uttar Pradesh': 34,
 'Uttarakhand': 35,
 'West Bengal': 36}


def AppointmentCheckByDist():
    
    select_state = st.selectbox("Select State",list(state_index.keys()))
    state_id = state_index[select_state]

    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0'}
    district_url = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
    
    response = requests.get(district_url,headers = headers )
    data = response.json()

    district_index = {}

    for district in data['districts']:
        district_index[district['district_name']] = district['district_id']
    
    select_dist = st.selectbox("Select District",list(district_index.keys()))
    district_id = district_index[select_dist]

    usr_date = st.sidebar.date_input('Enter Date. I will check the next 7 days from this date as well')
    date = usr_date.strftime("%d-%m-%Y")


    ## CoWIN API
    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}"
   
    response = requests.get(url,headers = headers )

    if response.status_code == 200:

        data = response.json()
        centers = data['centers']

        select_vaccine = st.sidebar.radio('Pick your Poison', options=['COVAXIN','COVISHIELD'])
        select_age = st.sidebar.radio('Minimum Age', options=['Any',18,45])
        select_fee = st.sidebar.radio('Free or Paid', options=['Any','Free','Paid'])

        sesh = {}
        for center in centers:
            for session in center['sessions']:
                sesh[session['session_id']] =  [center['name'],center['pincode'],session['date'],center['fee_type'],session['min_age_limit'],session['available_capacity'],session['vaccine']]
            
        df = pd.DataFrame.from_dict(sesh,orient = 'index',columns = ['Name','Pincode','Date','Fee','Age','Capacity','Vaccine'])
        df.set_index('Name',inplace=True)
        df = df[df['Capacity'] != 0]

        f"I found {len(df)} centers offering {select_vaccine} in {select_dist}"   
        select_center = st.selectbox('Select Center',list(df.index))

        res = df.loc[(df.index == select_center) & (df['Vaccine'] == select_vaccine.upper())]
        
        if select_age != 'Any':
            res = res[res['Age'] == select_age]
        
        if select_fee != 'Any':
            res = res[res['Fee'] == select_fee]

    
        if len(res) == 0:
            st.error(f"No Appointments are available")
        else:
            st.write("Here you go! Don't hate. Vaccinate!")
            res

            row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.beta_columns((.1, 1, .1, 1, .1))

            st.write("")
            with row3_1:
                st.subheader(f"Vaccine Distribution in {select_dist}")
                sns.countplot(x = 'Vaccine',data = df)
                st.pyplot()

            with row3_2:
                st.subheader(f"Vaccine Availability by Date")
                g = sns.lineplot(y = 'Capacity',x = 'Date',data = df)
                g.set_xticklabels(labels = list(df['Date']),rotation=90)
                st.pyplot()
            

            
            





AppointmentCheckByDist()


