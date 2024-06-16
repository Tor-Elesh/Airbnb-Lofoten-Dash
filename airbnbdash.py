import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

df = pd.read_excel(r'airbnbdata.xlsx')

df['price'] = df['price'].str.replace(' kr NOK ','')
df['price'] = df['price'].str.split().agg("".join)
df['price'] = df['price'].astype(int)

df = df.rename(columns = {'price':'price (NOK)'})
df.loc[df['price (NOK)'] <= df['price (NOK)'].quantile(0.20), 'Price Bucket'] = '20% Quartile'
df.loc[(df['price (NOK)'] > df['price (NOK)'].quantile(0.20)) & (df['price (NOK)'] <= df['price (NOK)'].quantile(0.40)), 'Price Bucket'] = '40% Quartile'
df.loc[(df['price (NOK)'] > df['price (NOK)'].quantile(0.40)) & (df['price (NOK)'] <= df['price (NOK)'].quantile(0.60)), 'Price Bucket'] = '60% Quartile'
df.loc[(df['price (NOK)'] > df['price (NOK)'].quantile(0.60)) & (df['price (NOK)'] <= df['price (NOK)'].quantile(0.80)), 'Price Bucket'] = '80% Quartile'
df.loc[df['price (NOK)'] > df['price (NOK)'].quantile(0.80), 'Price Bucket'] = '>80% Quartile'

df[['Gjester', 'Soverom','Senger', 'Bad']] = pd.DataFrame(df['details'].str.split('·').to_list(), columns=['Gjester', 'Soverom','Senger', 'Bad'])
df.loc[df['Senger'].str.contains('bad','toalett', na=False), 'Bad'] = df['Senger']
df.loc[df['Soverom'].str.contains('seng', na=False), 'Senger'] = df['Soverom']
df.loc[df['Gjester'].str.contains('soverom', na=False), 'Soverom'] = df['Gjester']
df.loc[df['Soverom'].str.contains('bad','toalett', na=False), 'Bad'] = df['Soverom']
df.loc[df['Gjester'].str.contains('seng', na=False), 'Senger'] = df['Gjester']

df.loc[~df['Bad'].str.contains('bad','toalett', na=False), 'Bad'] = 0
df.loc[~df['Senger'].str.contains('seng', na=False), 'Senger'] = 0
df.loc[~df['Soverom'].str.contains('soverom', na=False), 'Soverom'] = 0
df.loc[~df['Gjester'].str.contains('gjester', na=False), 'Gjester'] = 0

df = df.replace(np.nan,0)

for i in ['Gjester', 'Soverom','Senger','Bad']:
    df[i] = df[i].str.extract('(\d+)')
    df[i] = df[i].fillna(0).astype(float)

lst = df.url.str.split('check_in=').str[-1].str.split('&check_out=')
df['check in'] = [item[0] for item in lst]
df['check in'] = pd.to_datetime(df['check in'])

df = df.drop(columns = {'details'})

#-----------------------------------------------------------------------------------------------------------------------
#Dashboarding
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.sidebar.header('Airbnb Lofoten Dashboard, `version 1`')

st.sidebar.subheader('Check-In Date')
dateslider = st.sidebar.slider('Filter Check in Date',
                               df['check in'].min().to_pydatetime(), df['check in'].max().to_pydatetime(), (df['check in'].min().to_pydatetime(), df['check in'].max().to_pydatetime()))

st.sidebar.subheader('Price Bucket')
price_bucket = st.sidebar.multiselect('Select Bucket',
                                      ('20% Quartile','40% Quartile', '60% Quartile', '80% Quartile', '>80% Quartile'),
                                      default=('20% Quartile','40% Quartile', '60% Quartile', '80% Quartile', '>80% Quartile'))

st.write("""
Airbnb Lofoten dash
""")

filtered_data = df.loc[(df['check in'] >= dateslider[0]) & (df['check in'] <= dateslider[1]) & (df['Price Bucket'].isin(price_bucket))]
#Row A
averageprice = filtered_data['price (NOK)'].mean()
averageguestspace = filtered_data['Gjester'].mean()
averagebathroom = filtered_data['Bad'].mean()
averagebedroom = filtered_data['Soverom'].mean()
averagebeds = filtered_data['Senger'].mean()


st.markdown('### Metrics')
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Snitt Pris per Dag", averageprice.round(2).astype(str) + ' NOK')
col2.metric("Snitt gjeste kapasitet",averageguestspace.round(2).astype(str) + ' Gjester')
col3.metric("Snitt antall bad",averagebathroom.round(2).astype(str) + ' Bad')
col4.metric("Snitt antall soverom",averagebedroom.round(2).astype(str) + ' Soverom')
col5.metric("Snitt antall senger",averagebeds.round(2).astype(str) + ' Senger')


#Row B
c1, c2 = st.columns((7,3))
with c2:
    st.markdown('Airbnb listings')
    st.data_editor(
        filtered_data.sort_values('price (NOK)', ascending=False)[['name','price (NOK)','url']],
        column_config={
            "url": st.column_config.LinkColumn("Link til Airbnb")
        },
        hide_index=True,)
with c1:
    st.markdown('Snitt Pris over tid')
    st.plotly_chart(px.line(filtered_data.groupby('check in')['price (NOK)'].mean().reset_index(),
                  x="check in",
                  y="price (NOK)",
                  markers=True), use_container_width=True)
