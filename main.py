import pandas as pd
import logging
import os
from dragon_scrape import scrape_all_pages, clean_data, generate_output
from bgg_api import call_bgg_for_id, call_bgg_for_details

# Get the directory of the script and set it as the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create the output directory if it doesn't exist, relative to the script's directory
output_dir = os.path.join(script_dir, 'output')
os.makedirs(output_dir, exist_ok=True) 

# Set up logging
log_file = os.path.join(output_dir, 'dragonlog.log')
logger = logging.getLogger(__name__)
logging.basicConfig(filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    logger.info('Starting the scraping process...')
    # Scrape the Dragon's Lair website
    scrape_results = scrape_all_pages()
    output, updates = generate_output(clean_data(scrape_results))
    logger.info('Scraping complete.')
    logger.info(f'Stock availability updates: {updates}')

    # Check if this is the first run
    final_data_path = os.path.join(output_dir, 'final_data.csv')
    first_run = not os.path.exists(final_data_path)

    # if first run, only get IDs for new games
    if first_run:
        games_to_fetch = output.loc[output['status'] == 'New Game']['name']
        # Create empty DataFrames to avoid errors
        prev_id_data = pd.DataFrame(columns=['id', 'name'])
        prev_bgg_enriched_data = pd.DataFrame(columns=['id'])
        prev_final_data = output
        
    else:
        # If not first run, get IDs for new games and games with unknown IDs
        prev_final_data = pd.read_csv(final_data_path) 
        prev_id_data = prev_final_data[['id', 'name']]
        prev_bgg_enriched_data = prev_final_data[['title','year','best_with','recommended_with','avg_rating','no_ratings','bgg_rank','id']]

        # Get the games to fetch
        new_games = output.loc[output['status'] == 'New Game']['name']
        unfetched_games = prev_final_data.loc[prev_final_data['id'] == 'Unknown']['name']
        games_to_fetch = pd.concat([new_games, unfetched_games], ignore_index=True).drop_duplicates().tolist()

    # Get the IDs for the games
    if games_to_fetch:
        #ids_to_get = games_to_fetch.tolist()
        logger.info(f"Fetching IDs for {len(games_to_fetch)} games...")
        id_output = pd.DataFrame(call_bgg_for_id(games_to_fetch), columns=['name', 'id'])
        updated_bgg_data = pd.concat([prev_id_data, id_output]).drop_duplicates(subset=['name'], keep='last')
    else:
        print("No new games to fetch.")
        updated_bgg_data = prev_id_data
    

    # Get the details for the games
    ## only run for games that have an ID and are not in the previous enriched data
    games_to_enrich = updated_bgg_data.loc[(updated_bgg_data['id'] != 'Unknown') & (~updated_bgg_data['id'].isin(prev_bgg_enriched_data['id']))]
    logger.info(f"Fetching details for {len(games_to_enrich)} games...")

    # call the BGG API for the details
    bgg_enriched = call_bgg_for_details(games_to_enrich)
    bgg_enriched = pd.concat([bgg_enriched, prev_bgg_enriched_data]).drop_duplicates(subset=['id'], keep='last')
    

    # If columns 'played' and 'wishlist' are not present, add them
    if 'played' not in prev_final_data.columns and 'wishlist' not in prev_final_data.columns:
        prev_final_data['played'] = False
        prev_final_data['wishlist'] = False

    # Merge the two DataFrames info the final data
    prev_final_data = prev_final_data[['name', 'state_previous', 'state_current', 'state_since', 'status', 'played', 'wishlist']] # only keep the necessary columns to prevent duplicates
    final_data = prev_final_data.merge(updated_bgg_data, how='left', on='name')
    final_data = final_data.merge(bgg_enriched, how='left', on='id')
    
    # Re-order columns
    final_data = final_data[['name', 'state_previous', 'state_current', 'state_since', 'status', 'id', 'title', 'year', 'best_with', 'recommended_with', 'avg_rating', 'no_ratings', 'bgg_rank', 'played', 'wishlist']]
    # if the state_current is nan, the game has been removed
  
    # Save the output files
    logger.info("Saving output files...")
    final_data.to_csv(final_data_path, index=False)
    logger.info("Complete.")
    print("Complete.")

