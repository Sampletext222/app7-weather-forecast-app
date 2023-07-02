import streamlit as st
import plotly.express as px

st.title("Weather Forecast for the next days")
place = st.text_input("Place: ")
days = st.slider("Forecast Days", min_value=1, max_value=5,
                 help="Select the number of forecasted days")
option = st.selectbox("select data to view", ("Temperature", "Sky"))
st.subheader(f"{option} for the next {days} days in {place}")

dates = ["02-02-1993", "03-02-1993","04-02-1993"]
temperature = [10, 11, 15]
temperature = [days * i for i in temperature]


figure = px.line(x=dates,y=temperature, labels={"x": "Date", "y": "temperature"})

st.plotly_chart(figure)

