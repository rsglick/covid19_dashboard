import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set()

st.title('USA COVID-19 Dashboard')
metric = st.sidebar.selectbox('Cases/Deaths:',['cases','deaths'])

def add_new(df):
    df['new_cases'] = df['cases'].diff()
    df['new_deaths'] = df['deaths'].diff()
    
    df['new_cases_rolling_mean'] = df['new_cases'].rolling(7).mean()
    df['new_deaths_rolling_mean'] = df['new_deaths'].rolling(7).mean()
    df = df.fillna(0)

    df = df.astype({'cases':int, 'deaths':int, 'new_cases':int, 'new_deaths':int, 'new_cases_rolling_mean':int, 'new_deaths_rolling_mean':int})
    return df    

@st.cache(allow_output_mutation=True)
def load_data() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    DATA_SOURCE_URL      = 'https://github.com/nytimes/covid-19-data'
    us_data_url          = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
    us_states_data_url   = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    us_counties_data_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

    df_us_data          = pd.read_csv(us_data_url)
    df_us_data['date']  = pd.to_datetime(df_us_data['date'])

    df_us_states_data          = pd.read_csv(us_states_data_url)
    df_us_states_data['date']  = pd.to_datetime(df_us_states_data['date'])

    
    df_us_counties_data          = pd.read_csv(us_counties_data_url)
    df_us_counties_data['date']  = pd.to_datetime(df_us_counties_data['date'])


    return (df_us_data, df_us_states_data, df_us_counties_data)

us_data, us_states_data, us_counties_data = load_data()

st.sidebar.write(f'Total Cases: {us_data["cases"].max()}')
st.sidebar.write(f'Total Deaths: {us_data["deaths"].max()}')


display_columns = ['date', 'cases', "deaths", 'new_cases', 'new_deaths']


bars = alt.Chart().mark_bar(
    size=0.5
).encode(
    x='date:T',
    y=alt.Y(f'new_{metric}:Q', axis=alt.Axis(title=metric)),
    tooltip=['date', f'new_{metric}']
)
line_rolling = alt.Chart().mark_line(    
    color='red',
    size=3
).encode(
    x='date:T',
    y=alt.Y(f'new_{metric}_rolling_mean:Q', axis=alt.Axis(labels=False)),
    tooltip=['date', f'new_{metric}_rolling_mean']
)

us_data = add_new(us_data)
layer = alt.layer(line_rolling, bars, data=us_data).interactive()
st.altair_chart(layer, use_container_width=True)
st.write(us_data[display_columns])







st.write('State trends')
state_choice = st.selectbox('Select', sorted(us_states_data['state'].unique()))

condition = us_states_data['state'] == state_choice
state_data = us_states_data[condition]
state_data = add_new(state_data)

layer = alt.layer(line_rolling, bars, data=state_data).interactive()
st.altair_chart(layer, use_container_width=True)
st.write(state_data[display_columns])


st.write('County trends')
county_state_conditon = us_counties_data['state'] == state_choice
county_choice = st.selectbox('Select', sorted(us_counties_data[county_state_conditon]['county'].unique()))

condition = (county_state_conditon) &  (us_counties_data[county_state_conditon]['county'] == county_choice)
county_data = us_counties_data[condition]
county_data = add_new(county_data)

layer = alt.layer(line_rolling, bars, data=county_data).interactive()
st.altair_chart(layer, use_container_width=True)
st.write(county_data[display_columns])