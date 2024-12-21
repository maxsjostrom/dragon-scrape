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
            time.sleep(5 ** attempt)  # Exponential backoff
    
    
def clean_name(name):
    # Remove any language tags
    name = re.sub(r'\(.*\)', '', name) # Remove anything in parentheses
    return name.strip()

def get_details(dl_name):
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
       # print(game)

        for item in game:
            name = item.find("name").get("value")
            
            if name == cleaned_name:
                id = item.get("id")
                # print(f"Found game: {name}")
                # print(item.get("id"))
                
                return dl_name, item.get("id")
        
        # If exact match not found return the first result
        if game:
            id = game[0].get("id")
            # print(f"Found game: {cleaned_name}")
            # print(game[0].get("id"))
            
            return dl_name, game[0].get("id")
        else:
            return dl_name, "Unknown"
    

    else:
        return dl_name, "Unknown"
        #print(f"Game not found: {name}")
        #print(f"Failed to fetch game details. Status code: {response.status_code}")


def get_bgg_id(game_list):
    id_list = []
    
    for game in game_list:
        print(f"Searching for game: {game}")
        name, id = get_details(game)
        id_list.append([name, id])
    return id_list

def get_enriched_data(bgg_data):
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

# Get the gameid details from BoardGameGeek
all_games = prev_dragons_lair_data['name'].tolist()
df_bgg = pd.DataFrame(get_bgg_id(all_games), columns=['name', 'id'])

# Get rating game details from BoardGameGeek
bgg_enrich = get_enriched_data(prev_bgg_data)

    

# Merge the two DataFrames
df_merge = prev_dragons_lair_data.merge(prev_bgg_data, how='left', on='name')
df_merge = df_merge.merge(bgg_enrich, how='left', on='id')
print(df_merge.head(50))

# Save the outputs
df_bgg.to_csv('output/bgg_output.csv', index=False)
bgg_enrich.to_csv('output/bgg_enrich.csv', index=False)
df_merge.to_csv('output/final_data.csv', index=False)




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