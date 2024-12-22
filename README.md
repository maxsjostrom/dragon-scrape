# Dragon-Scrape

Dragon-Scrape is a Python project for scraping and tracking board game availability from the "Lånebiblioteket" section of Dragonslair's website. It fetches game data, cleans it, and identifies changes in availability between runs.

## Features

- Scrapes multiple pages of game data from Dragonslair's website.
- Extracts and cleans game names and availability status.
- Tracks changes in game availability over time.
- Enriches game data with additional details from the BGG API.
- Handles API rate limits and retries.
- Outputs results to CSV files for easy comparison.

## Requirements

- Python 3.8 or higher
- Required libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `json`
  - `datetime`


## How It Works
### Scraping Pages:

The script fetches game data page by page from the Dragonslair website, using requests to retrieve HTML content and BeautifulSoup to parse it.

### Parsing Game Data:

Extracts game names and availability status from the website’s HTML structure.

### Cleaning Data:

Removes invalid entries and standardizes the availability status (Available, Unavailable).

### Tracking Changes:

Compares the current scrape with the previous run, tracking changes in game availability and identifying new games.

### Enriching Data with BGG API:

1. **Fetching Game IDs**: The script calls the BGG API to fetch game IDs for new or unfetched games.
2. **Fetching Game Details**: Once the game IDs are obtained, the script fetches additional details such as title, year, average rating, number of ratings, and BGG rank.
3. **Handling Rate Limits**: The script includes logic to handle API rate limits by implementing retries with exponential backoff.


## Output:

Saves the results in dragonslair.csv for future comparisons and generates dragonslair_changes.csv for quick analysis of changes.

The script generates the following CSV files in the `output` directory:
- `dragonslair.csv`: Contains the scraped game data from Dragonslair.
- `bgg_output.csv`: Contains the game IDs fetched from the BGG API.
- `bgg_enrich.csv`: Contains the enriched game details from the BGG API.
- `final_data.csv`: Merged data from Dragonslair and BGG, including game availability and additional details.


### Example Output
`dragonslair_changes.csv`:

| Name              | State Previous | State Current | State Since         | Status       |
|-------------------|----------------|---------------|---------------------|--------------|
| Example Game 1    | Unavailable    | Available     | 2024-12-21 10:00:00 | State Change |
| Example Game 2    | Available      | Unavailable   | 2024-12-21 10:00:00 | State Change |
| Example New Game  | N/A            | Available     | 2024-12-21 10:00:00 | New Game     |


