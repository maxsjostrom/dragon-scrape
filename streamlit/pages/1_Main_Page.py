import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# Make streamlit layout wide
st.set_page_config(layout="wide")
st.logo('../assets/dragons-lair-logo.webp')

# Function to run the main.py script
def run_main_script():
    # Ensure required modules are installed
    st.error('Function not implemented.')

# Load the data
data_path = '../output/final_data.csv'
df = pd.read_csv(data_path)

st.image('../assets/dragons-lair-logo.webp', width=500)

st.title('Lånebiblioteket')


st.write('### All Games')
st.write(df)

# Select data for scatter plot
scatter_data = df[['name', 'avg_rating', 'no_ratings', 'state_current', 'bgg_rank', 'played']]
scatter_data['bgg_rank'] = scatter_data['bgg_rank'].replace('Not Ranked', np.nan).dropna().astype(int)

# Filter options
st.sidebar.header('Sidebar')
columns = df.columns.tolist()

col1, col2 = st.columns(2)

fig1 = px.scatter(scatter_data, x='avg_rating', y='no_ratings', color='state_current', hover_name='name', title='Scatter plot of Average Rating vs Number of Ratings',
                 color_discrete_map={'Available': 'mediumspringgreen', 'Unavailable': 'indianred'})
fig1.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
col1.plotly_chart(fig1)

fig2 = px.scatter(df, x='avg_rating', y='no_ratings', color='played', hover_name='name', title='Scatter plot of Average Rating vs Number of Ratings',
                 color_discrete_map={True: 'mediumspringgreen', False: 'indianred'})
fig2.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
col2.plotly_chart(fig2)
