# Oregon & California Election Results Scraper

## Overview

This program is designed to scrape and process election results for various races and statewide measures in Oregon and California. It interacts with the Oregon & California election results API to gather data on legislative races and statewide measures, processes the data, and saves it in JSON and CSV formats for further analysis. It then updates premade graphs on Datawrapper for clean display

## Features

- **State Legislature Race Tracking**: For California races, the URL is hard-coded to get the results we want. For Oregon state legislature races, the program reads a list of race IDs from a text file (`oregon_raceids.txt`) and fetches the latest results for each race, because it's easier to pull up the races individually.
- **Statewide Measures**: It also fetches results for all statewide measures in Oregon and California.
- **Data Storage**: The results are stored in JSON files with timestamps and are also converted to CSV format for easy analysis. JSON files are for error-checking, and any files older than 24 hours are deleted.
- **Error Handling**: The program includes error handling to ensure that API requests are successful.

## Files

- **JPRscraper.py**: A Python script that handles the scraping and processing of statewide measure results for Oregon and California.
- **Mayscraper.py**: A new python script to handle scraping and processing of results for the Mary primary in Oregon
- **oregon_raceids.txt**: A text file containing the race IDs for the races being tracked.
- **oregon_leg_results.csv**: A CSV file that stores the latest legislative race results for Oregon.
- **oregon_measure_results.csv**: A CSV file that stores the latest statewide measure results for Oregon.
- **california_leg_results.csv**: A CSV file that stores the latest legislative race results for California.
- **california_measure_results.csv**: A CSV file that stores the latest statewide measure results for California.

## Usage

1. **Setup**: Ensure you have the necessary Python packages installed. You can install the required packages using:
    ```sh
    pip install requests, datawrapper
    ```

2. **Run the Script**: Execute the `JPRscraper.py` script to fetch and process the statewide results:
    ```sh
    python JPRscraper.py
    ```

3. **View Results**: The results will be saved in JSON and CSV files in the same directory.

Note: This program does not CREATE the datawrapper graphs initially, I reccomend running the scraping parts first, then taking the CSVs and manually creating graphs in Datawrapper, then copying the ID's and pasting them in the script so it can auto-update from then on.

## Running automatically

This repository has an action setup to run it automatically.
I found that using Github's built-in scheduler was unreliable and can be late. I found that it was a lot more reliable to [cron-job.org](https://cron-job.org/en/) to schedule a workflow_dispatch three minutes past every hour. Cronjob is free for basic users!

**Setup**:
1. Create a new cronjob

2. Set the url to the API url for the respository dispatch link. For this repository, that is [https://api.github.com/repos/battaglir/JPR-Election-night-scraping/actions/workflows/scraper-app.yml/dispatches](https://api.github.com/repos/battaglir/JPR-Election-night-scraping/actions/workflows/scraper-app.yml/dispatches)

3. Go to "Advanced Settings"

4. Create a header with the key "Accept" and the value "application/vnd.github.v3+json"

5. In Github Settings, go to "developer options" and click "fine-grained tokens" under "personal access tokens." Create a new token that allows access to the scraper repository. Then copy the token.

6. in CronJob, create another header with the key "Authorization" and the value "token" + the token you just copied from github.

7. Under "advanced" set the time zone to match yours, set the request method to POST and paste this in the request body, "{"ref": "main"}". Set the timeout to 30 seconds.

8. Under common, you can set the execution schedule to whatever you like. I had it set to run three minutes past every hour.

Then once you enable the job, it should run. You can manually run it to test it and make sure it works.

## Notes

- Ensure that the `oregon_raceids.txt` file is present in the same directory as the scripts. Make sure you have the right raceIDs for the races you want to track.
- The program uses the current date and time to generate filenames for the JSON files, ensuring that each run produces a unique file.
- This program cannot be used out of the box, you will need to make some changes to adjust for your specific needs, including adding a DataWrapper API key. Those are mostly all noted in comments in the script.

## Oregon URL info

(Accurate as of 5/20/2025)
The Oregon base URL is [https://orresultswebservices.azureedge.us](https://orresultswebservices.azureedge.us)
To access results, you need to input certain codes, after the heading "/ResultsAjax.svc/GetMapData?"
All of the following need to be inputted to access results: type, category, raceID, osn, party & county
Type options:
NEEDS to be filled in
- SWPAR = Statewide partisan races (Governor, Sec of State, Attorney General, etc.)
- MEASURE = Statewide measures
- CTYALL = All county races
- LMEA = Local measures, use Category CTY to access Yes and no candidates, only works with specific RaceID and county = 0, find raceIDs by exporting list on results frontend
- MCR = Shared County, city and district races & measures
- HOUSE = State house races
- SENATE = State senate races

Category options:
NEEDS a category for races ofhter than LMEA, MCR and MEASURE
- CTY = County
- SW = Statewide
- Maybe more?

raceID:
Leave at 0 to show all counties
Can be changed to show just the candidates in one race specifically. raceID's can be found by loading all results, looking at one candidate, and looking at the RaceID, or by exporting the results from [results.oregonvotes.gov](results.oregonvotes.gov) and looking at the RaceID there.

osn:
I believe stands for "Office Sequence Number," leave this at "0"

party:
0 for all parties, DEM for Democrat, REP for republican

county: 
Leave at 0 for all counties
I don't know all the counties yet, but here's what I have, can find more by doing full search of all county races
03 = Jackson
02 = Curry
05 = Klamath
This does not work for LMEA type, possible only works for CTYALL type

## License

This project is licensed under the GPL-3.0 license.
