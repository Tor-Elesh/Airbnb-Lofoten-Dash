import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_excel('airbnbdata.xlsx')

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
with c1:
    st.markdown('Snitt Pris over tid')
    st.plotly_chart(px.line(filtered_data.groupby('check in')['price (NOK)'].mean().reset_index(),
                  x="check in",
                  y="price (NOK)",
                  markers=True), use_container_width=True)
with c2:
    st.markdown('Airbnb listings')
    st.dataframe(
        filtered_data.drop_duplicates(subset=['name','price (NOK)']).sort_values('price (NOK)', ascending=False)[['name','price (NOK)','url']],
        column_config={
            "url": st.column_config.LinkColumn()
        },
        hide_index=True)
