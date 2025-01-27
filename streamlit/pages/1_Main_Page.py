import streamlit as st
import pandas as pd
import subprocess

# Make streamlit layout wide
st.set_page_config(layout="wide")

# Function to run the main.py script
def run_main_script():
    # Ensure required modules are installed
    st.error('Function not implemented.')

# Load the data
data_path = '../output/final_data.csv'
df = pd.read_csv(data_path)

# Display the data
st.title('Dragon\'s Lair Lånebibliotek')

# Button to run the main script
if st.button('Run Update Script'):
    st.write('Running the update script...')
    stdout, stderr = run_main_script()
    if stderr:
        st.error(f"Error: {stderr}")
    else:
        st.success('Update script completed successfully.')
        # Reload the data
        df = pd.read_csv(data_path)
        st.experimental_rerun()

state_change_games = df.loc[df['status'] == 'State Change']
st.write('### Recently Updated Games')
st.write(state_change_games.reset_index(drop=True))

st.write('### All Games')
st.write(df)

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
st.title('Filtered Data')
st.write(filtered_df)

