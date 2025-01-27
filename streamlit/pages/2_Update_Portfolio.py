import streamlit as st
import pandas as pd
import numpy as np

# Make Streamlit layout wide
st.set_page_config(layout="wide", page_title="Update Portfolio")

# Load the data
data_path = '../output/final_data.csv'
df = pd.read_csv(data_path)

# Display the data
st.title('Dragon\'s Lair Lånebibliotek')

# Filter options
st.sidebar.header('Filter Options')
columns = df.columns.tolist()

# Select column to filter
selected_column = st.sidebar.selectbox('Select column to filter', columns)

# Select filter value
unique_values = df[selected_column].dropna().unique()
selected_value = st.sidebar.selectbox('Select value to filter', unique_values)

# Apply filter
filtered_df = df[df[selected_column] == selected_value]

# Display filtered data
st.write('## Filtered Data')
st.write(filtered_df)

# Open data in data editor
st.write('## Data Editor')
#st.write('You can edit the played and wishlist fields below. Click "Save Data" to save the changes.')
df_editor = df[[ 'name', 'played', 'wishlist', 'status', 'state_current', 'best_with', 'recommended_with', 'bgg_rank']].copy()

df_editor = st.data_editor(df_editor,
                           disabled=('name', 'status', 'state_current', 'best_with', 'recommended_with', 'bgg_rank'))

# Save updated `played` and `wishlist` columns back to the full data and CSV file
# Display warning if user tries to leave the page without saving
if df[['played', 'wishlist']].equals(df_editor[['played', 'wishlist']]):
    pass
else:
    st.warning('Values updated. Please save before leaving the page.')

if st.button('Save Data'):
    # Update the original DataFrame with the edited columns
    df.update(df_editor[['name', 'played', 'wishlist']])
    
    # Save the full DataFrame to the CSV file
    df.to_csv(data_path, index=False)
    st.success('Data saved successfully.')
