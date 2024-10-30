# Oregon & California Election Results Scraper

## Overview

This program is designed to scrape and process election results for various races and statewide measures in Oregon and California. It interacts with the Oregon & California election results API to gather data on legislative races and statewide measures, processes the data, and saves it in JSON and CSV formats for further analysis. It then updates premade graphs on Datawrapper for clean display

## Features

- **State Legislature Race Tracking**: For California races, the URL is hard-coded to get the results we want. For Oregon state legislature races, the program reads a list of race IDs from a text file (`oregon_raceids.txt`) and fetches the latest results for each race, because it's easier to pull up the races individually.
- **Statewide Measures**: It also fetches results for all statewide measures in Oregon and California.
- **Data Storage**: The results are stored in JSON files with timestamps and are also converted to CSV format for easy analysis.
- **Error Handling**: The program includes error handling to ensure that API requests are successful.

## Files

- **JPRscraper.py**: A Python script that handles the scraping and processing of statewide measure results for Oregon and California.
- **oregon_raceids.txt**: A text file containing the race IDs for the races being tracked.
- **oregon_leg_results.csv**: A CSV file that stores the latest legislative race results.
- **oregon_measure_results.csv**: A CSV file that stores the latest statewide measure results.

## Usage

1. **Setup**: Ensure you have the necessary Python packages installed. You can install the required packages using:
    ```sh
    pip install requests, datawrapper
    ```

3. **Run the Script**: Execute the `JPRscraper.py` script to fetch and process the statewide results:
    ```sh
    python JPRscraper.py
    ```

4. **View Results**: The results will be saved in JSON and CSV files in the same directory.

## Notes

- Ensure that the `oregon_raceids.txt` file is present in the same directory as the scripts. Make sure you have the right raceIDs for the races you want to track.
- The program uses the current date and time to generate filenames for the JSON files, ensuring that each run produces a unique file.

## License

This project is licensed under the GPL-3.0 license.
