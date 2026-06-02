# A scraper for the California primary election.
# This will grab the statewide resuls and the results for Shasta County. Other counties have been difficult to automate because county/local results are not posted to one centralized space

# Licensed under a GNU General Public License v3.0
# Code written by Roman Battaglia, 2024.

import requests, datetime, json, csv, re, os, pytz, time, pandas as pd
from datawrapper import Datawrapper

#Set the timezone
pacific_tz = pytz.timezone('US/Pacific')

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the datawrapper API key from an environment variable for security
dw_key = os.environ.get("DATAWRAPPER_API_KEY")

#Setup the Datawrapper client
dw = Datawrapper(dw_key)

#Create the JSON directory if it doesn't exist
if not os.path.exists('jsons'):
    os.makedirs('jsons')

# Grab the statewide results
r = requests.get('https://api.sos.ca.gov/returns/query?r=["02000000000059", "03000000000059", "04000000000059", "07000000000059", "11000001000059", "11000002000059", "12000002000059", "13000001000059", "13000002000059"]')

r.raise_for_status()

#Gather the JSON results from the API request
cal_cands = r.json()

#Dump the JSON results to a readable format
cal_json = json.dumps(cal_cands, indent=4)

#Set the filename of the JSON to the current date and time
latest_cal_name = f"jsons/california_cands_{timenow}.json"

#Write the JSON results to the file
with open(latest_cal_name, "w") as outfile:
    json.dump(cal_cands, outfile)

print(f"Full statewide results saved to {latest_cal_name}")

#Load the JSON file we just created
with open(latest_cal_name) as f:
    data = json.load(f)

# Iterate through each contest int he JSON data
for contst in data:
    # Set the name of the CSV file to match the contest, using regex to clean up the name
    csv_filename = f"California_{contst['raceTitle'].split('-', 1)[0].strip().replace(' ', '_').replace('.', '')}_results.csv"
    # Open the CSV file for writing
    with open(csv_filename, 'w', newline='') as file:
        # Write the header row
        csv_headers = ["Candidate", "Party", "Votes", "Percent"]
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
        # Iterate through the candidates in the contest and write their data to the CSV
        for cand in contst['candidates']:
            # Determine the candidate's name and incumbency
            if cand.get("incumbent") == True:
                name = cand.get("Name") + " (Incumbent)"
            else:
                name = cand.get("Name")
            # Determine the candidate's party affiliation
            if cand.get("Party") == "Dem":
                party = "Democratic"
            elif cand.get("Party") == "Rep":
                party = "Republican"
            elif cand.get("Party") == "NPP":
                party = "No Party Preference"
            elif cand.get("Party") == "Lib":
                party = "Libertarian"
            elif cand.get("Party") == "P&F":
                party = "Peace and Freedom"
            elif cand.get("Party") == "Grn":
                party = "Green"

            votes = cand.get("Votes").replace(",", "")

            percent = cand.get("Percent")
            #Write the collected data to the CSV file
            writer.writerow({
                "Candidate": name, 
                "Party": party, 
                "Votes": votes, 
                "Percent": percent
            })

    print(f"Saved {contst['raceTitle'].split('-', 1)[0].strip()} results to {csv_filename}")

with open('calraces.json') as f:
    calraces = json.load(f)

latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

# Update the Datawrapper charts with the new data
for race in calraces:
    print(f"Updating {race.get('filename')}")
    try:
        new_data = pd.read_csv(race.get("filename"), encoding="utf-8-sig")
    except UnicodeDecodeError:
        new_data = pd.read_csv(race.get("filename"), encoding="cp1252")
    metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }
    chart_id = race.get("Key")
    dw.add_data(chart_id=chart_id, data=new_data)
    dw.update_metadata(chart_id=chart_id, metadata=metadata)
    dw.publish_chart(chart_id=chart_id)

# %%
# Update the Shasta County results with the same process as above, but with a different API endpoint
#import requests, time, json, datetime, csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Upgrade-Insecure-Requests': '1', # You can add more headers if needed
}

url = "https://results.enr.clarityelections.com/CA/Shasta/126486/373172/json/en/summary.json"
retry_count = 5  # Number of retries if request fails
retry_delay = 5  # Delay between retries in seconds

#Make the request with retries for handling 202 responses and other potential errors
for i in range(retry_count):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 202:
            print("Received 202 response, retrying...")
            print(r.text)
            time.sleep(retry_delay)
            continue
        r.raise_for_status()
        print("Request successful")
        break
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
else:
    print("Max retries exceeded. Exiting...")
    print(r.text)
# Import the JSON
print(r.status_code)
r.raise_for_status()
if not r.content:
    print("There's no data available")

#Converts the raw data to a JSON file
data = r.json()

# parses the raw python data into JSON data
json_object = json.dumps(data, indent=4)

# set the current date and time
timenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

#set the name of the file
latest_file_name = f"jsons/shasta_results_{timenow}.json"

# write output to file
with open(latest_file_name, "w") as outfile:
    json.dump(data, outfile)

#Print out the name of the latest file
print("Latest filename:", latest_file_name)

# Read the watched contests
with open('watched_contests.txt', 'r') as f:
     watched_contests = [line.strip() for line in f.readlines()]

# Open the JSON file
with open(latest_file_name, 'r') as f:
     data = json.load(f)

# Iterate through the JSON data
for contest in data:
     # If the contest's name is in the watched contests list
     if contest['C'] in watched_contests:
          # Extract the 'C', 'CH', 'PCT', and 'V' values
          c_value = contest.get('C')
          #Convert the candidate names to title case for better readability in the CSV
          ch_value = [name.title() for name in contest.get('CH', [])]
          pct_value = contest.get('PCT')
          v_value = contest.get('V')

          # Prepare the data for writing to CSV
          rows = zip(ch_value, v_value, pct_value)

          # Set the name of the CSV file to match the contest
          clean_name = f"{c_value}_results_clean.csv"

          # Write to CSV
          with open(clean_name, 'w', newline='') as f:
               writer = csv.writer(f)
               #Check if the contest is a measure, which will use a different header.
               if c_value == "Measure B":
                    writer.writerow(["Result", "Votes", "Percent"]) # Write header for measure
               else:
                    writer.writerow(["Candidate", "Votes", "Percent"])  # Write header
               for row in rows:
                    writer.writerow(row)  # Write data rows

# %%
#Update the datawrapper charts

#open the JSON file with the list of CSV files and their corresponding Datawrapper chart keys
with open('shastaraces.json') as f:
    calraces = json.load(f)

#Set the latest time for the annotation in the Datawrapper charts
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

# Update the Datawrapper charts with the new data
for race in calraces:
    print(f"Updating {race.get('filename')}")
    # Try UTF-8 encoding first, then fall back to cp1252 if that fails (for files with special characters like accents)
    try:
        new_data = pd.read_csv(race.get("filename"), encoding="utf-8-sig") 
    except UnicodeDecodeError:
        new_data = pd.read_csv(race.get("filename"), encoding="cp1252")
    #Update the metadata to include an annotation with the last updated time
    metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }
    #Update chart data/metadata and publish in one call
    chart_id = race.get("Key")
    dw.add_data(chart_id=chart_id, data=new_data)
    dw.update_metadata(chart_id=chart_id, metadata=metadata)
    dw.publish_chart(chart_id=chart_id)

# %%
#Delete any .json files older than 24 hours
now = datetime.datetime.now(tz=pacific_tz).strftime("%m-%d")
print(f"Checking for old files to delete...")
print(f"Current date: "+now)
#Iterate through all files in the JSON
for filename in os.listdir('jsons/.'):
	print(f"Checking file: "+filename)
	if filename.endswith('.json'):
        #Extract the month and day from the filename. All JSON filenames use the format "YYYY-MM-DD_HH-MM" at the end
		file_date = re.search("-(\d{2}-\d{2})", filename)
        #If the data doesn't match the current month and day, delete the file
		if file_date.group(1) != now:
			os.remove(f'jsons/{filename}')
			print(f"Deleted old file: {filename}")
		else:
			print(f"File is current, not deleting: {filename}")