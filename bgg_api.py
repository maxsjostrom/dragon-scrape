import requests
import xml.etree.ElementTree as etree
import pandas as pd
import numpy as np
import re
import time

def get_game_details(game_id):
    url = f"https://boardgamegeek.com/xmlapi2/thing"
    params = {'id': game_id,
              'stats': 1}
    response = requests.get(url, params=params)
    
    print(response.status_code)

    for attempt in range(3):
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
            print(f"Title: {title}, Year: {year}, Best with: {best_with}, Reccomended with: {recommended_with}, Avg rating: {avg_rating}, No of ratings: {no_ratings}, bgg_rank: {bgg_rank}")
            #print(f"Title: {title}, Year: {year}")

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
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)

        elif attempt > 1:
            print(f"Failed with status {response.status_code}. Retrying...")
            time.sleep(3 ** attempt)  # Exponential backoff
        
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
                return dl_name, item.get("id")
        
        # If exact match not found return the first result
        if game:
            id = game[0].get("id")
            return dl_name, game[0].get("id")
        # If no results found return unknown
        else:
            return dl_name, "Unknown"
    if response.status_code == 429:
        print("Rate limited. Retrying after 10 seconds...")
        time.sleep(10)
        return get_bgg_id(dl_name)

    # If request still fails return null
    else:
        return dl_name, ''



def call_bgg_for_id(game_list):
    id_list = []
    
    for game in game_list:
        print(f"Searching for game: {game}")
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


# ----------------------------------------------------------------------------------------------------------------------------
# Import the scraped data
prev_dragons_lair_data = pd.read_csv('output/dragonslair.csv')
prev_bgg_data = pd.read_csv('output/bgg_output.csv')
prev_bgg_enriched_data = pd.read_csv('output/bgg_enrich.csv')
prev_bgg_enriched_data['id'] = prev_bgg_enriched_data['id'].astype(str)
prev_final_output = pd.read_csv('output/final_data.csv')

new_games = prev_dragons_lair_data.loc[prev_dragons_lair_data['status'] == 'New Game']['name']
unfetched_games = prev_final_output.loc[prev_final_output['id'] == 'Unknown']['name']
games_to_fetch = pd.concat([new_games, unfetched_games], ignore_index=True).drop_duplicates()

if not games_to_fetch.empty:
    ids_to_get = games_to_fetch.tolist()
    id_output = pd.DataFrame(call_bgg_for_id(ids_to_get), columns=['name', 'id'])

    updated_bgg_data = pd.concat([prev_bgg_data, id_output]).drop_duplicates(subset=['name'], keep='last')

    print(updated_bgg_data)
else:
    print("No new games to fetch.")
    updated_bgg_data = prev_bgg_data

# Get the details for the games
# only run for games that have an ID and are not in the previous enriched data
games_to_enrich = updated_bgg_data.loc[(updated_bgg_data['id'] != 'Unknown') & (~updated_bgg_data['id'].isin(prev_bgg_enriched_data['id']))]
bgg_enriched = call_bgg_for_details(games_to_enrich)
bgg_enriched = pd.concat([bgg_enriched, prev_bgg_enriched_data]).drop_duplicates(subset=['id'], keep='last')

# Merge the two DataFrames
df_merge = prev_dragons_lair_data.merge(updated_bgg_data, how='left', on='name')
df_merge = df_merge.merge(bgg_enriched, how='left', on='id')

updated_bgg_data.to_csv('output/bgg_output.csv', index=False)
bgg_enriched.to_csv('output/bgg_enrich.csv', index=False)
df_merge.to_csv('output/final_data.csv', index=False)

print(df_merge.head(50))


'''
# Get the gameid details from BoardGameGeek
all_games = prev_dragons_lair_data['name'].tolist()
df_bgg = pd.DataFrame(call_bgg_for_id(all_games), columns=['name', 'id'])

# Get rating game details from BoardGameGeek
bgg_enrich = call_bgg_for_details(prev_bgg_data)

    

# Merge the two DataFrames
df_merge = prev_dragons_lair_data.merge(prev_bgg_data, how='left', on='name')
df_merge = df_merge.merge(bgg_enrich, how='left', on='id')
print(df_merge.head(50))

# Save the outputs
df_bgg.to_csv('output/bgg_output.csv', index=False)
bgg_enrich.to_csv('output/bgg_enrich.csv', index=False)
df_merge.to_csv('output/final_data.csv', index=False)

'''


# Open the output
# Create list of games without IDs
    # Get the IDs from BGG
    # Update the list of games with IDs
# Check the bgg_output.csv file for IDs without details
    # Get the details from BGG
    # Save the details to bgg_enrich.csv
# Merge the dragonslair.csv with bgg_output.csv
# Merge the merged file with bgg_enrich.csv
# Save the final file as final_data.csv