# %% [markdown]
# Election Scraper and results graphs
# 
# This program will scrape the results for specific contests in Oregon and California, organize the data, push the data to a Datawrapper graph and automatically update the graph with the latest data.
# This program was built for the 2024 General Election. It may need to be modified in the future to work with other elections. Places where the program may need to be updated are noted in the comments.
# Licensed under a GNU General Public License v3.0
# Code written by Roman Battaglia, 2024.

# %%
#Import the required packages
import requests, datetime, json, csv, re, os, pytz, pandas as pd

#Create the JSON directory if it doesn't exist
if not os.path.exists('jsons'):
    os.makedirs('jsons')

# Import Propositions from California Secretary of State

#Set the URL for the California ballot measure API
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. Found at https://www.sos.ca.gov/media
r = requests.get("https://api.sos.ca.gov/returns/ballot-measures")

#Call the API
r.raise_for_status()

#Gather the JSON results from the API request
props = r.json()

json_props = json.dumps(props, indent=4)

#Set the time zone to Pacific Time
pacific_tz = pytz.timezone('US/Pacific')

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Create a JSON file with the latest results and the current date and time
latest_prop_name = f"jsons/california_props_{timenow}.json"

#Write the JSON results to the file
with open(latest_prop_name, "w") as outfile:
    json.dump(props, outfile)

# Load the JSON file and extract the ballot measures data
with open(latest_prop_name, "r") as f:
    data = json.load(f)

    # Extract ballot measures data
    ballot_measures = data["ballot-measures"]

    # Define CSV file name
    csv_filename = "california_prop_results.csv"

    # Define CSV headers
    csv_headers = ["Proposition", "Yes Votes", "Yes %", "No Votes", "No %"]

    # Write data to CSV
    #NOTE: This may need to be updated to reflect the current data structure of the API response
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
        for measure in ballot_measures:
            writer.writerow({
                "Proposition": measure["Number"].lstrip('0'),
                "Yes Votes": measure["yesVotes"],
                "Yes %": measure["yesPercent"],
                "No Votes": measure["noVotes"],
                "No %": measure["noPercent"]
            })

    print(f"California Measure data written to {csv_filename}")


# %%

#Update the datawrapper chart

from datawrapper import Datawrapper

#Get the API key from the environment variables
#NOTE: You will need to set the environment variable in GitHub Secrets, or replace this with your API key
dw_key = os.environ.get("DATAWRAPPER_API_KEY")

#Set the API key for Datawrapper
dw = Datawrapper(dw_key)

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart ID
    chart_id="M9hCa",
    data=pd.read_csv("california_prop_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("M9hCa", metadata=metadata)

#republish the chart
dw.publish_chart("M9hCa")

print("California Proposition data updated in Datawrapper")


# %%

# Code to grab the relevant state assembly and senate races in California

#Set the API url to grab all the state legislature districts in our region
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. Found at https://www.sos.ca.gov/media.
#You will also need to change the race IDs to reflect the races you want to grab for the current election. I found those in the API Endpoints CSV file provided by the Cal SOS.
#The first half of the document had api's with words, and those correspond to another URL in the second half with a number for that race. They're both in the same order, so find the matching URL.
r = requests.get('https://api.sos.ca.gov/returns/query?r=["02000000000059","03000000000059","07000000000059","08000000000059","11000002000059","12000002000059","13000001000059","13000002000059","13000003000059"]')

# API url for just statewide races: https://api.sos.ca.gov/returns/query?r=["02000000000059","03000000000059","07000000000059","08000000000059","11000002000059"]

#Call the API
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

#Open the JSON file and extract the data
with open(latest_cal_name, "r") as f:
    data = json.load(f)

    # Define CSV file name
    csv_filename = "california_cand_results.csv"

    #Set the column headers for the CSV file
    csv_headers = ["Race", "Candidate", "Party", "Votes", "Percent"]

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
        #NOTE: This may need to be updated to reflect the current data structure of the API response
        for contest in data:
            #Get the name of the race
            race = contest.get("raceTitle")
            for suffix in (" - Districtwide Results", " - Statewide Results"):
                if suffix in race:
                    race = race.replace(suffix, "")
            for candidate in contest.get("candidates", []):
                #Check if the candidate is an incumbent, if so, add that to their name
                if candidate.get("incumbent") == True:
                    name = candidate.get("Name") + " (Incumbent)"
                else:
                    name = candidate.get("Name")
                #Check for the party of each candidate
                #NOTE: The data structure could change the way parties are represented, so this may need to be updated
                if candidate.get("Party") == "Dem":
                    party = "Democratic"
                elif candidate.get("Party") == "Rep":
                    party = "Republican"
                votes = candidate.get("Votes").replace(',', '')
                percent = candidate.get("Percent")
                
                # Write the candidate's information to the CSV file
                writer.writerow({
                    "Race": race,
                    "Candidate": name,
                    "Party": party,
                    "Votes": votes,
                    "Percent": percent
                })

    print(f"California Statewide data written to {csv_filename}")
# %%
# Take the candidate data for California and update the datawrapper chart
#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart ID
    chart_id="aF8sp",
    data=pd.read_csv("california_cand_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("aF8sp", metadata=metadata)

#republish the chart
dw.publish_chart("aF8sp")

print("California Statewide data updated in Datawrapper")



# %%
# Grab the statewide measures in Oregon

#Set the URL to the call the Oregon results API for all statewide measures
#NOTE: This API URL may change for future elections, so you will need to update it to the correct URL for the current election. Reach out to the PIO for the Oregon SOS before the election. They did not have documentation available for the data feed. Also check the readme for a guide
# I found the right code by messing around with the URL and seeing what worked. I found that getting the type right was important, it matched up with the type in the URL of the https://results.oregonvotes.gov webpage. The other categories are all needed or results won't show up. Party can be changed to "DEM" or "REP" 
"""
#this section of code is unused in 2026 as there are no staewide ballot measures
r = requests.get("https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=MEASURE&category=SW&raceID=0&osn=0&county=0&party=0")

#Call the API
r.raise_for_status()
# Parse the JSON response
measures = r.json()

# Convert the JSON data to a formatted string
json_measures = json.dumps(measures, indent=4)

# Define the filename for the JSON data with the current timestamp
latest_measure_name = f"jsons/oregon_measures_{timenow}.json"

# Write the JSON data to a file
with open(latest_measure_name, "w") as outfile:
    json.dump(measures, outfile)

# Open the JSON file and load the data
with open(latest_measure_name, "r") as f:
    data = json.load(f)

    # Extract the measures data
    measures = data["d"]

    # Define the CSV filename
    csv_filename = "oregon_measure_results.csv"

    # Define the CSV headers
    csv_headers = ["Measure", "Yes Votes", "Yes %", "No Votes", "No %"]

    # Write the measures data to the CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
        
        #NOTE: This may need to be updated to reflect the current data structure of the API response
        #The "[:5]" is used to limit the number of measures to 5, you can change this number to get more or less measures. If removed, this will get all measures twice.
        # Iterate through the measures and write the relevant data to the CSV
        for measure in measures[:5]:
            race_id = measure["RaceID"]
            #The measure number and description were combined in the API response, so we need to separate out the measure number using regex
            race_name = re.search("Measure ...", measure["RaceName"]).group(0)
            calc_candidate = measure["calcCandidate"]
            #For the 2024 election, percentages were shown as decimals, so we need to multiply by 100 to get the percentage
            calc_candidate_percentage = measure["calcCandidatePercentage"] * 100
            calc_candidate_votes = measure["calcCandidateVotes"]

            # Initialize vote and percentage variables
            if calc_candidate == "Yes":
                yes_percent = calc_candidate_percentage
                yes_votes = calc_candidate_votes
            elif calc_candidate == "No":
                no_percent = calc_candidate_percentage
                no_votes = calc_candidate_votes

            #In Oregon, the "Yes" and "No" votes for measures are stored as seperate "candidates" in the API response, so we need to find the other candidate's data by matching the race_id and adding the remaining yes or no votes
            # Find the other candidate's data for the same measure
            for other_measure in measures:
                if other_measure["RaceID"] == race_id and other_measure["calcCandidate"] != calc_candidate:
                    if other_measure["calcCandidate"] == "Yes":
                        yes_percent = other_measure["calcCandidatePercentage"] * 100
                        yes_votes = other_measure["calcCandidateVotes"]
                    elif other_measure["calcCandidate"] == "No":
                        no_percent = other_measure["calcCandidatePercentage"] * 100
                        no_votes = other_measure["calcCandidateVotes"]

            # Write the measure data to the CSV file
            writer.writerow({
                "Measure": race_name,
                "Yes Votes": yes_votes,
                "Yes %": yes_percent,
                "No Votes": no_votes,
                "No %": no_percent
            })

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    # Sort the DataFrame by 'Measure'
    df_sorted = df.sort_values(by='Measure')

    # Write the sorted DataFrame back to the CSV file
    df_sorted.to_csv(csv_filename, index=False)

    print(f"Oregon Measure data written to {csv_filename}")

# %%
#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart ID
    chart_id="1uvst",
    data=pd.read_csv("oregon_measure_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PST"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("1uvst", metadata=metadata)

#republish the chart
dw.publish_chart("1uvst")

print("Oregon Measure data updated in Datawrapper")
"""

# %%

#Gather the statewide Oregon races

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_stwide_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Race", "Candidate", "Party", "Votes", "Percent"]

#Create a dictionary with the raceIDs for the statewide races we want to track
#NOTE: You will need to update this list with the correct raceIDs for future elections. I found these by looking at all statewide races. Use the URL below but replace {raceid} with "0"
oregon_ids = ["300031519", "300031520", "300031518"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Iterate through each ID in oregon_ids
for oregonurl in open("oregon_raceids.txt").read().splitlines():
    #Set the URL to the Oregon SOS API for the statewide results
    #NOTE: Change this API URL to the correct one for the current election, which could change in the future.
    r= requests.get(oregonurl)

    #Call the API
    r.raise_for_status()

    #Gather the JSON results from the API request
    a_data = r.json()

    #If there is a file with the latest data, update it with the new data
    if os.path.isfile(latest_file_name):

        with open(latest_file_name, "r") as infile:
            data = json.load(infile)

        data.update(a_data)

        with open(latest_file_name, "w") as outfile:
            json.dump(data, outfile)
    #otherwise, create a new file with the latest data
    else:
        with open(latest_file_name, "w") as outfile:
            json.dump(a_data, outfile)

    #Open the JSON file and extract the data
    with open(latest_file_name, "r") as f:
        data = json.load(f)

    #Navigate down to just the stuff we want
    races = data["d"]

    #Open the CSV file and prepare to append the data to it
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)

        #Iterate through each candidate in the JSON
        for race in races:
             
            #Gather the required information from the JSON
            race_name = race["RaceName"].replace(
                "(4 Year Term - 3 Seats) (2 Year Unexpired Term - 1 Seat) (Vote For 4)",
                "(4 at-large seats)"
            )
            race_candidate = race["calcCandidate"]
            race_percentage = race["calcCandidatePercentage"]*100
            race_votes = race["calcCandidateVotes"]
            #If there is no party name, fill the cell with an empty string
            if race["PartyName"]:
                race_party = race["PartyName"]
            else:
                race_party = ""

            #Write the data to the CSV file
            writer.writerow({
                "Race": race_name,
                "Candidate": race_candidate,
                "Party": race_party,
                "Votes": race_votes,
                "Percent": race_percentage
            })

print(f"Oregon statewide races data written to {csv_filename}")
# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="FM6iq",
    data=pd.read_csv("oregon_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("FM6iq", metadata=metadata)

#republish the chart
dw.publish_chart("FM6iq")

print("Oregon Statewide race data updated in Datawrapper")

# %%

#Grab the local measures

# Define the filename for the JSON data with the current timestamp
latest_file_name = f"jsons/oregon_measures_{timenow}.json"

# Define the CSV filename
csv_filename = "oregon_measure_results.csv"

# Define the CSV headers
csv_headers = ["Measure", "Yes Votes", "Yes %", "No Votes", "No %"]

# Write the measures data to the CSV file
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

oregon_measure_ids = ["300001785" , "300001805", "300001806","300001808","300001809","300001758","300001742","300001781","300001780","300001816","300001807","300001771"]

#Grab the statewide measure data
for raceids in oregon_measure_ids:
    r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=CTYALL&category=CTY&raceID={raceids}&osn=0&county=0&party=0&map=CTY")

    #Call the API
    r.raise_for_status()
    # Parse the JSON response
    a_data = r.json()

    # Convert the JSON data to a formatted string
    json_measures = json.dumps(a_data, indent=4)

    #If there is a file with the latest data, update it with the new data
    if os.path.isfile(latest_file_name):

        with open(latest_file_name, "r") as infile:
            data = json.load(infile)

        data.update(a_data)

        with open(latest_file_name, "w") as outfile:
            json.dump(data, outfile)
    #otherwise, create a new file with the latest data
    else:
        with open(latest_file_name, "w") as outfile:
            json.dump(a_data, outfile)

    # Open the JSON file and load the data
    with open(latest_file_name, "r") as f:
        data = json.load(f)

    # Extract the measures data
    measures = data["d"]
        
    #NOTE: This may need to be updated to reflect the current data structure of the API response
    #The "[:1]" is used to ensure it only grabs the measure once
    # Iterate through the measures and write the relevant data to the CSV
    for measure in measures[:1]:
        race_id = measure["RaceID"]
        race_name = measure["RaceName"]
        calc_candidate = measure["calcCandidate"]
        #For the 2025 election, percentages were shown as decimals, so we need to multiply by 100 to get the percentage
        calc_candidate_percentage = measure["calcCandidatePercentage"] * 100
        calc_candidate_votes = measure["calcCandidateVotes"]

        # Initialize vote and percentage variables
        if calc_candidate == "Yes":
            yes_percent = calc_candidate_percentage
            yes_votes = calc_candidate_votes
        elif calc_candidate == "No":
            no_percent = calc_candidate_percentage
            no_votes = calc_candidate_votes

        #In Oregon, the "Yes" and "No" votes for measures are stored as seperate "candidates" in the API response, so we need to find the other candidate's data by matching the race_id and adding the remaining yes or no votes
        # Find the other candidate's data for the same measure
        for other_measure in measures:
            if other_measure["RaceID"] == race_id and other_measure["calcCandidate"] != calc_candidate:
                if other_measure["calcCandidate"] == "Yes":
                    yes_percent = other_measure["calcCandidatePercentage"] * 100
                    yes_votes = other_measure["calcCandidateVotes"]
                elif other_measure["calcCandidate"] == "No":
                    no_percent = other_measure["calcCandidatePercentage"] * 100
                    no_votes = other_measure["calcCandidateVotes"]

        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=csv_headers)
        # Write the measure data to the CSV file
            writer.writerow({
                "Measure": race_name,
                "Yes Votes": yes_votes,
                "Yes %": yes_percent,
                "No Votes": no_votes,
                "No %": no_percent
            })

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="2YZ36",
    data=pd.read_csv("oregon_measure_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    #NOTE: Change "PST" to "PDT" if the current time is in Daylight Saving Time
                    "notes": f"Last updated: {latest_time} PDT"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("2YZ36", metadata=metadata)

#republish the chart
dw.publish_chart("2YZ36")

print("Oregon Statewide race data updated in Datawrapper")

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
