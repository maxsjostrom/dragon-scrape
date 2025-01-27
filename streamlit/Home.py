import streamlit as st
import pandas as pd
import subprocess

# Make streamlit layout wide
st.set_page_config(layout="wide")

# Function to run the main.py script
def run_main_script():
    # Ensure required modules are installed
    st.error('Function not implemented. Fetching most recent data...')

# Load the data
data_path = '../output/final_data.csv'
df = pd.read_csv(data_path, parse_dates=['state_since']
                 ,dtype={'id': str, 'bgg_rank': str, 'year': str,
                        'avg_rating': float, 'played': bool, 'wishlist': bool})


# Display the data
st.title('Dragon\'s Lair Lånebibliotek')

# Button to run the main script
with st.container(border=True):
    st.write('### Update Portfolio')
    if st.button('Run Update Script'):
        try:
            st.write('#### Log')
            st.write('Running the update script...')
            run_main_script()
            #st.success('Update script completed successfully.')
        except Exception as e:
            st.error(f"Error: {e}")
    st.write(f'***Last updated: {df["state_since"].max().strftime("%Y-%m-%d")}***')


# 
today = pd.to_datetime('today')
df['state_since'] = pd.to_datetime(df['state_since'], errors='coerce')

days_since_change = 7 # Number of days to consider a game as recently updated
state_change_games = df.loc[(df['status'] == 'State Change') 
                            | ((today - df['state_since']).dt.days < days_since_change)].sort_values(
                                ['state_since', 'avg_rating'], ascending=False)

st.write('## Recently Updated Games')
st.info('Games updated within last week or changed state in last run')
st.write(state_change_games.reset_index(drop=True))

# Filter options
st.sidebar.header('Filter Options')
columns = df.columns.tolist()

# Select column to filter
selected_column = st.sidebar.selectbox('Select column to filter', columns)

# Select filter value
unique_values = df[selected_column].unique()
selected_value = st.sidebar.selectbox('Select value to filter', unique_values)

# Apply filter
filtered_df = df[df[selected_column] == selected_value]

# Display filtered data
with st.container(border=True):
    st.write('## Filtered Data')
    col1, col2, col3 = st.columns(3)
    col1.metric('Number of games', filtered_df.shape[0])
    col2.metric('Number of wishlisted games', filtered_df.loc[filtered_df['wishlist'] == True].shape[0])
    col3.metric('Number of played games', filtered_df.loc[filtered_df['played'] == True].shape[0])
    st.write(filtered_df)

