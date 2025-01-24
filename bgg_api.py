import requests
import xml.etree.ElementTree as etree
import pandas as pd
import logging
import re
import time

logger = logging.getLogger(__name__)

def clean_name(name):
    # Remove any language tags
    name = re.sub(r'\(.*\)', '', name) # Remove anything in parentheses
    return name.strip()

def get_bgg_id(dl_name):
    # Clean the name
    cleaned_name = clean_name(dl_name)

    url = f"https://boardgamegeek.com/xmlapi2/search?"
    params = {'query': cleaned_name,
              'type': 'boardgame'}
    response = requests.get(url, params=params)

    logger.info(f"Fetching ID for game: {dl_name}")

    if response.status_code == 200:
        # Parse the XML response
        root = etree.fromstring(response.content)
        game = root.findall("item")

        # Loop through the results
        for item in game:
            # Get the name of the game
            name = item.find("name").get("value")
            
            # Check for exact match and return the ID
            if name == cleaned_name:
                id = item.get("id")
                logger.info(f"Found exact match for: {cleaned_name}")
                return dl_name, item.get("id")
        
        # If exact match not found return the first result
        if game:
            id = game[0].get("id")
            logger.info(f"Found closest match for: {cleaned_name}")
            return dl_name, game[0].get("id")
        # If no results found return unknown
        else:
            logger.info(f"No results found for: {cleaned_name}")
            return dl_name, "Unknown"
    if response.status_code == 429:
        logger.warning(f"Rate limited. Retrying after 10 seconds...")
        time.sleep(10)
        return get_bgg_id(dl_name)

    # If request still fails return null
    else:
        logger.info(f"Failed to fetch ID for: {dl_name}")
        return dl_name, ''

def get_game_details(game_id):
    ''' Get the details for a game from the BoardGameGeek API. '''
    url = f"https://boardgamegeek.com/xmlapi2/thing"
    params = {'id': game_id,
              'stats': 1}
    response = requests.get(url, params=params)

    for attempt in range(3):
        logger.info(f"Fetching details for game: {game_id}")

        if response.status_code == 200:
            # Parse the XML response
            root = etree.fromstring(response.content)
            game = root.find("item")
            best_with = game.find(".//poll-summary/result[@name='bestwith']").get("value")
            recommended_with = game.find(".//poll-summary/result[@name='recommmendedwith']").get("value")
            title = game.find("name").get("value")
            year = game.find("yearpublished").get("value")
            avg_rating = game.find(".//statistics/ratings/average").get("value")
            no_ratings = game.find(".//statistics/ratings/usersrated").get("value")
            bgg_rank = game.find(".//statistics/ratings/ranks/rank[@name='boardgame']").get("value")
            #description = game.find("description").text
            
            logger.info(f"Title: {title}, Year: {year}, Best with: {best_with}, Reccomended with: {recommended_with}, Avg rating: {avg_rating}, No of ratings: {no_ratings}, bgg_rank: {bgg_rank}")

            return pd.DataFrame({
                        'title': [title], 
                        'id': [game_id],
                        'year': [year], 
                        'best_with': [best_with], 
                        'recommended_with': [recommended_with], 
                        'avg_rating': [avg_rating], 
                        'no_ratings': [no_ratings], 
                        'bgg_rank': [bgg_rank]})
        
        elif response.status_code == 429 & attempt == 1:  # Rate limit
                retry_after = int(response.headers.get("Retry-After", 5))  # Default to 2 seconds
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)

        elif attempt > 1:
            logger.error(f"Failed with status {response.status_code}. Retrying...")
            time.sleep(3 ** attempt)  # Exponential backoff

def call_bgg_for_id(game_list):
    id_list = []
    
    for game in game_list:
        name, id = get_bgg_id(game)
        id_list.append([name, id])
    return id_list

def call_bgg_for_details(bgg_data):
    bgg_enrich = pd.DataFrame(columns=['title', 'year', 'best_with', 'recommended_with', 'avg_rating', 'no_ratings', 'bgg_rank'])

    for id in bgg_data['id']:
        try:
            bgg_enrich = pd.concat([bgg_enrich, get_game_details(id)], ignore_index=True)
        except Exception as e:
            continue
    return bgg_enrich

