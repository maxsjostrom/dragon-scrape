# Dragon-Scrape

Dragon-Scrape is a Python project for scraping and tracking board game availability from the "Lånebiblioteket" section of Dragonslair's website. It fetches game data, cleans it, and identifies changes in availability between runs.

## Features

- Scrapes multiple pages of game data from Dragonslair's website.
- Extracts and cleans game names and availability status.
- Tracks changes in game availability over time.
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

## Output:

Saves the results in dragonslair.csv for future comparisons and generates dragonslair_changes.csv for quick analysis of changes.

  - `dragonslair.csv`: A CSV file containing the current state of all games.
  - `dragonslair_changes.csv`: A CSV file highlighting changes in game availability since the last run.

### Example Output
`dragonslair_changes.csv`:

| Name              | State Previous | State Current | State Since         | Status       |
|-------------------|----------------|---------------|---------------------|--------------|
| Example Game 1    | Unavailable    | Available     | 2024-12-21 10:00:00 | State Change |
| Example Game 2    | Available      | Unavailable   | 2024-12-21 10:00:00 | State Change |
| Example New Game  | N/A            | Available     | 2024-12-21 10:00:00 | New Game     |


