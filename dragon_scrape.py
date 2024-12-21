import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime

BASE_URL = "https://dragonslair.se/lanebiblioteket/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


def fetch_page(page_number):
    """Fetch a single page of games."""
    params = {
        'page': page_number,
        'restore_auto_pagination': 'true'
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch page {page_number}. Status code: {response.status_code}")
        return None
    


def parse_games(page_content):
    """Parse game details (name and state) from the page HTML."""
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
                name = name.replace('-Lånebiblioteket- ', '').strip()
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
    """Scrape all pages until no more data is loaded."""
    all_games = []
    page_number = 1

    while page_number < 20:
        print(f"Fetching page {page_number}...")
        page_content = fetch_page(page_number)
        if not page_content:
            break  # Stop if request fails
        
        games = parse_games(page_content)
        if not games:
            print("No more games found. Stopping.")
            break  # Stop if no more games are found on the page
        
        all_games.extend(games)
        page_number += 1
        
    return all_games

def clean_data(all_games):
    df = pd.DataFrame(all_games)
    df.loc[df['state'] == 'Beställningsvara', 'state'] = 'Unavailable'
    df = df[df['name'] != 'Unknown'].reset_index(drop=True)

    return df

def generate_output(new_run):
    try:
        previous_run = pd.read_csv('dragonslair.csv')
    except FileNotFoundError:
        previous_run = pd.DataFrame(columns=['name', 'state_current', 'state_previous' , 'state_since', 'status'])

    previous_run = previous_run.rename(columns={'state_current': 'state'})
    previous_run.drop(columns=['state_previous'], inplace=True)

    comparison = pd.merge(previous_run, new_run, on='name', how='outer', suffixes=('_previous', '_current'))


    #comparison['state_since'] = pd.NaT
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update the 'status' column based on the state changes
    comparison['status'] = 'No Change'
    comparison.loc[comparison['state_previous'].isna(), 'status'] = 'New Game'
    comparison.loc[comparison['state_previous'] != comparison['state_current'], 'status'] = 'State Change'

    # Update the 'state_since' column to the current time where applicable
    comparison.loc[comparison['state_since'].isna(), 'state_since'] = current_time
    comparison.loc[comparison['status'] == 'State Change', 'state_since'] = current_time

    # Reorder the columns
    comparison = comparison[['name', 'state_previous', 'state_current', 'state_since', 'status']]

    # Save the new run
    comparison.to_csv('dragonslair.csv', index=False, sep='|')
    differences = comparison[comparison['status'] == 'State Change']
    differences.to_csv('dragonslair_changes.csv', index=False, sep='|')

    return comparison, differences


if __name__ == '__main__':
    scrape_results = scrape_all_pages()
    output, updates = generate_output(clean_data(scrape_results))
    print('Scraping complete.')
    print(updates)
