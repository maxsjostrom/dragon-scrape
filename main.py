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
print(f"Output directory: {output_dir}")
os.makedirs(output_dir, exist_ok=True) 

# Set up logging
log_file = os.path.join(output_dir, 'dragonlog.log')
print(f"Log file: {log_file}")
logger = logging.getLogger(__name__)
logging.basicConfig(filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    print("Starting the scraping process...")
    logger.info('Starting the scraping process...')
    # Scrape the Dragon's Lair website
    scrape_results = scrape_all_pages()
    output, updates = generate_output(clean_data(scrape_results))
    logger.info('Scraping complete.')
    logger.info(f'Stock availability updates: {updates}')

    # Check if this is the first run
    final_data_path = os.path.join(output_dir, 'final_data.csv')
    first_run = not os.path.exists(final_data_path)

    if first_run:
    # if first run, only get IDs for new games
        games_to_fetch = output.loc[output['status'] == 'New Game']['name']
        # Create empty DataFrames to avoid errors
        prev_bgg_data = pd.DataFrame(columns=['id', 'name'])
        prev_bgg_enriched_data = pd.DataFrame(columns=['id'])
        prev_dragons_lair_data = output
        
    else:
        # If not first run, get IDs for new games and games with unknown IDs
        prev_dragons_lair_data = pd.read_csv(os.path.join(output_dir, 'dragonslair.csv'))
        prev_bgg_data = pd.read_csv(os.path.join(output_dir, 'bgg_output.csv'))
        prev_bgg_enriched_data = pd.read_csv(os.path.join(output_dir, 'bgg_enrich.csv'))
        prev_bgg_enriched_data['id'] = prev_bgg_enriched_data['id'].astype(str)
        prev_final_output = pd.read_csv(final_data_path)

        new_games = prev_dragons_lair_data.loc[prev_dragons_lair_data['status'] == 'New Game']['name']
        unfetched_games = prev_final_output.loc[prev_final_output['id'] == 'Unknown']['name']
        games_to_fetch = pd.concat([new_games, unfetched_games], ignore_index=True).drop_duplicates()

    # Get the IDs for the games
    if not games_to_fetch.empty:
        ids_to_get = games_to_fetch.tolist()
        logger.info(f"Fetching IDs for {len(ids_to_get)} games...")
        id_output = pd.DataFrame(call_bgg_for_id(ids_to_get), columns=['name', 'id'])
        updated_bgg_data = pd.concat([prev_bgg_data, id_output]).drop_duplicates(subset=['name'], keep='last')
    else:
        print("No new games to fetch.")
        updated_bgg_data = prev_bgg_data
    
    updated_bgg_data.to_csv(os.path.join(output_dir, 'bgg_output.csv'), index=False)

    # Get the details for the games
    # only run for games that have an ID and are not in the previous enriched data
    games_to_enrich = updated_bgg_data.loc[(updated_bgg_data['id'] != 'Unknown') & (~updated_bgg_data['id'].isin(prev_bgg_enriched_data['id']))]
    logger.info(f"Fetching details for {len(games_to_enrich)} games...")
    # call the BGG API for the details
    bgg_enriched = call_bgg_for_details(games_to_enrich)
    bgg_enriched = pd.concat([bgg_enriched, prev_bgg_enriched_data]).drop_duplicates(subset=['id'], keep='last')

    # Merge the two DataFrames
    df_merge = prev_dragons_lair_data.merge(updated_bgg_data, how='left', on='name')
    df_merge = df_merge.merge(bgg_enriched, how='left', on='id')

    # Save the output files
    logger.info("Saving output files...")
    bgg_enriched.to_csv(os.path.join(output_dir, 'bgg_enrich.csv'), index=False)
    df_merge.to_csv(final_data_path, index=False)
    logger.info("Complete.")
    print("Complete.")

