import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import logging
import os

os.makedirs('output', exist_ok=True)


logger = logging.getLogger(__name__)

BASE_URL = "https://dragonslair.se/lanebiblioteket/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


def fetch_page(page_number):
    '''
    Fetch the HTML content of a page from the Dragonslair website.
    '''

    # Parameters for the request
    params = {
        'page': page_number,
        'restore_auto_pagination': 'true'
    }

    # Make the request
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        logger.info(f"Fetched page {page_number}")
        return response.text
    else:
        logger.warning(f"Failed to fetch page {page_number}. Status code: {response.status_code}")
        return None
    

def parse_games(page_content):
    '''
    Parse the HTML content of a page and extract the game data.
    '''
    soup = BeautifulSoup(page_content, 'html.parser')
    games = []
    
    # Game elements are in cards on the webpage
    game_cards = soup.find_all('div', class_='column')
    
    for card in game_cards:
    # Extract the product data (from an attribute)
        product_data = card.get('data-product-object')
        
        if product_data:
            try:
                product_json = json.loads(product_data)
                name = product_json.get('name', 'Unknown')

                # Remove unwanted strings from the name
                strings_to_remove = ['-Lånebiblioteket- ', '-Lånebiblioteket -']
                for string in strings_to_remove:
                    name = name.replace(string, '').strip()
            except:
                product_json = None
                name = "Unknown"
            
            # Extract the stock availability (nested tag)
            stock_span = card.find('div', class_='stock')
            state = stock_span.text.strip() if stock_span else "Unknown"
            state = state.replace('\n', '').replace('Finns i lager', 'Available').strip()
        
            games.append({
                    'name': name,
                    'state': state
                })
            
    return games


def scrape_all_pages():
    '''
    Scrape all pages of the Dragonslair website and return a list of all games.
    '''
    all_games = []
    page_number = 1

    # Loop through all pages until no more games are found
    while page_number < 20:
        logger.info(f"Fetching page {page_number}...")
        page_content = fetch_page(page_number)
        if not page_content:
            break  # Stop if request fails
        
        games = parse_games(page_content)
        if not games:
            logger.warning("No more games found. Stopping.")
            break  # Stop if no more games are found on the page
        
        all_games.extend(games)
        page_number += 1
        
    return all_games

def clean_data(all_games):
    '''
    Clean the list of games and convert it to a DataFrame.
    '''
    # Convert the list of games to a DataFrame
    df = pd.DataFrame(all_games)
    # Replace the state values to be consistently in English
    df.loc[df['state'] == 'Beställningsvara', 'state'] = 'Unavailable'
    # Remove any games with the name 'Unknown'
    df = df[df['name'] != 'Unknown'].reset_index(drop=True)
    # Replace commas with semicolons in the game names
    df['name'] = df['name'].str.replace(',', ';')

    return df


def generate_output(new_run):
    '''
    Generate the output files and compare the new run with the previous run.
    '''
    # Load the previous run
    try:
        previous_run = pd.read_csv('output/final_data.csv')
        previous_run = previous_run[['name', 'state_current', 'state_previous' , 'state_since', 'status']]
    except FileNotFoundError:
        # If the file doesn't exist, create an empty DataFrame
        previous_run = pd.DataFrame(columns=['name', 'state_current', 'state_previous' , 'state_since', 'status'])

    # Rename the columns for the comparison
    previous_run = previous_run.rename(columns={'state_current': 'state'})
    previous_run.drop(columns=['state_previous'], inplace=True)

    # Merge the previous and new runs for comparison
    comparison = pd.merge(previous_run, new_run, on='name', how='outer', suffixes=('_previous', '_current'))

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update the 'status' column based on the state changes
    comparison['status'] = 'No Change'
    comparison.loc[comparison['state_previous'] != comparison['state_current'], 'status'] = 'State Change'
    comparison.loc[comparison['state_previous'].isna() & ~comparison['state_current'].isna(), 'status'] = 'New Game'
    comparison.loc[~comparison['state_previous'].isna() & comparison['state_current'].isna(), 'status'] = 'Removed'

    # Update the 'state_since' column to the current time where applicable
    comparison.loc[comparison['state_since'].isna(), 'state_since'] = current_time
    comparison.loc[comparison['status'] == 'State Change', 'state_since'] = current_time

    # Reorder the columns
    comparison = comparison[['name', 'state_previous', 'state_current', 'state_since', 'status']]

    # Save the new run
    differences = comparison[(comparison['status'] == 'State Change') | (comparison['status'] == 'New Game')]

    return comparison, differences
