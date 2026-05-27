# A scraper for the California primary election.
# This will grab the statewide resuls and the results for Shasta County. Other counties have been difficult to automate because county/local results are not posted to one centralized space

# Licensed under a GNU General Public License v3.0
# Code written by Roman Battaglia, 2024.

import requests, datetime, json, csv, re, os, pytz, pandas as pd
from datawrapper import Datawrapper

#Set the timezone
pacific_tz = pytz.timezone('US/Pacific')

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

dw_key = os.environ.get("DATAWRAPPER_API_KEY")

dw = Datawrapper(dw_key)

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
    dw.add_data(chart_id=race.get("Key"), data=new_data)
    metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }
    dw.update_metadata(race.get("Key"), metadata=metadata)
    dw.publish_chart(race.get("Key"))


# Update the Shasta County results with the same process as above, but with a different API endpoint


# %%
#Delete any .csv files older than 24 hours

now = datetime.datetime.now(tz=pacific_tz).strftime("%m-%d")
print(f"Checking for old files to delete...")
print(f"Current date: "+now)
for filename in os.listdir('jsons/.'):
	print(f"Checking file: "+filename)
	if filename.endswith('.json'):
		file_date = re.search("-(\d{2}-\d{2})", filename)
		if file_date.group(1) != now:
			os.remove(f'jsons/{filename}')
			print(f"Deleted old file: {filename}")
		else:
			print(f"File is current, not deleting: {filename}")
# %%