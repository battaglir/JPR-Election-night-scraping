# %% [markdown]
# Election Scraper and results graphs
# 
# This program will scrape the results for specific contests in Oregon and California, organize the data, push the data to a Datawrapper graph and automatically update the graph with the latest data.

# %%
import requests, datetime, json, csv, re, os, pytz, pandas as pd

# Import Propositions from California Secretary of State

#Set the URL for the California ballot measure API
r = requests.get("https://api.sos.ca.gov/returns/ballot-measures")

#Call the API
r.raise_for_status()

#Gather the JSON results from the API request
props = r.json()

json_props = json.dumps(props, indent=4)

pacific_tz = pytz.timezone('US/Pacific')

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Create a JSON file with the latest results and the current date and time
latest_prop_name = f"california_props_{timenow}.json"

#Write the JSON results to the file
with open(latest_prop_name, "w") as outfile:
    json.dump(props, outfile)

print("Latest filename:", latest_prop_name)

print (json_props)

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

    print(f"Data written to {csv_filename}")


# %%

#Update the datawrapper chart

from datawrapper import Datawrapper

dw_key = os.environ.get("DATAWRAPPER_API_KEY")

#Set the API key for Datawrapper
dw = Datawrapper(dw_key)

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    chart_id="ysg3H",
    data=pd.read_csv("california_prop_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    "notes": f"Last updated: {latest_time} PST"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("ysg3H", metadata=metadata)

#republish the chart
dw.publish_chart("ysg3H")


# %%

# Code to grab the relevant state assembly and senate races in California

#Set the API url to grab all the state legislature districts in our region
r = requests.get('https://api.sos.ca.gov/returns/query?r=["13000001000059","13000002000059","13000003000059","12000001000059"]')

#Call the API
r.raise_for_status()

#Gather the JSON results from the API request
cal_cands = r.json()

#Dump the JSON results to a readable format
cal_json = json.dumps(cal_cands, indent=4)

#Set the filename of the JSON to the current date and time
latest_cal_name = f"california_cands_{timenow}.json"

#Write the JSON results to the file
with open(latest_cal_name, "w") as outfile:
    json.dump(cal_cands, outfile)

print("Latest filename:", latest_cal_name)

print (cal_json)

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
        for contest in data:
            #Get the name of the race
            race = contest.get("raceTitle").replace(" - Districtwide Results", "")
            for candidate in contest.get("candidates", []):
                #Check if the candidate is an incumbent, if so, add that to their name
                if candidate.get("incumbent") == True:
                    name = candidate.get("Name") + " (Incumbent)"
                else:
                    name = candidate.get("Name")
                #Check for the party of each candidate
                if candidate.get("Party") == "Dem":
                    party = "Democratic"
                elif candidate.get("Party") == "Rep":
                    party = "Republican"
                votes = candidate.get("Votes").replace(',', '')
                percent = candidate.get("Percent")
                
                print ([race, name, party, votes, percent])
                # Write the candidate's information to the CSV file
                writer.writerow({
                    "Race": race,
                    "Candidate": name,
                    "Party": party,
                    "Votes": votes,
                    "Percent": percent
                })

# %%
# Take the candidate data for California and update the datawrapper chart
#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    chart_id="lyV8E",
    data=pd.read_csv("california_cand_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    "notes": f"Last updated: {latest_time} PST"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("lyV8E", metadata=metadata)

#republish the chart
dw.publish_chart("lyV8E")

# %%
# Grab the statewide measures in Oregon

#Set the URL to the call the Oregon results API for all statewide measures
r = requests.get("https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=MEASURE&category=SW&raceID=0&osn=0&county=0&party=0")

#Call the API
r.raise_for_status()
# Parse the JSON response
measures = r.json()

# Convert the JSON data to a formatted string
json_measures = json.dumps(measures, indent=4)

# Define the filename for the JSON data with the current timestamp
latest_measure_name = f"oregon_measures_{timenow}.json"

# Write the JSON data to a file
with open(latest_measure_name, "w") as outfile:
    json.dump(measures, outfile)

print("Latest filename:", latest_measure_name)
print(json_measures)

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

        # Iterate through the measures and write the relevant data to the CSV
        for measure in measures[:5]:
            race_id = measure["RaceID"]
            race_name = re.search("Measure ...", measure["RaceName"]).group(0)
            calc_candidate = measure["calcCandidate"]
            calc_candidate_percentage = measure["calcCandidatePercentage"] * 100
            calc_candidate_votes = measure["calcCandidateVotes"]

            # Initialize vote and percentage variables
            if calc_candidate == "Yes":
                yes_percent = calc_candidate_percentage
                yes_votes = calc_candidate_votes
            elif calc_candidate == "No":
                no_percent = calc_candidate_percentage
                no_votes = calc_candidate_votes

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

            print([race_name, yes_votes, yes_percent, no_votes, no_percent])

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    # Sort the DataFrame by 'Measure'
    df_sorted = df.sort_values(by='Measure')

    # Write the sorted DataFrame back to the CSV file
    df_sorted.to_csv(csv_filename, index=False)

    print(f"Sorted data written to {csv_filename}")

# %%
#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    chart_id="1uvst",
    data=pd.read_csv("oregon_measure_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    "notes": f"Last updated: {latest_time} PST"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("1uvst", metadata=metadata)

#republish the chart
dw.publish_chart("1uvst")

# %%

#Open the text file containing race IDs for races we are tracking
with open('oregon_raceids.txt', 'r') as f:
    oregon_ids = [line.strip() for line in f.readlines()]

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"oregon_leg_{timenow}.json"

#Set the filename for the CSV file with the latest data
csv_filename = "oregon_leg_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Race", "Candidate", "Party", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Iterate through each race in the raceids text file
for raceid in oregon_ids:
    #Print the current Race id we're working on
    print("raceid:"+raceid)
    #Convert the raceID to an integer, and if it's greater than 300031536, it's a house race, otherwise, set the URL to a Senate race
    if int(raceid) >= 300031536:
        r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=HOUSE&category=SW&raceID={raceid}&osn=0&county=0&party=0")
    else:
        r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=SENATE&category=SW&raceID={raceid}&osn=0&county=0&party=0")

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

    print("Latest filename:", latest_file_name)

    #Open the JSON file and extract the data
    with open(latest_file_name, "r") as f:
        data = json.load(f)
    
    #We only want the data from the "d" key, which is everything, so we can navigate down to there, essentially ignoring it.
    races = data["d"]
    
    with open(csv_filename, mode='a', newline='') as file:
        #Setup the CSV writer again
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        #go through every candidate in that specific race
        for race in races:
            #Gather the race name, candidate, percentage, votes, and check if they have a party name.
            race_name = race["RaceName"]
            race_candidate = race["calcCandidate"]
            race_percentage = race["calcCandidatePercentage"]*100
            race_votes = race["calcCandidateVotes"]
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

            print([race_name, race_candidate, race_party, race_votes, race_percentage])

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    chart_id="2pT4G",
    data=pd.read_csv("oregon_leg_results.csv")
)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

#set the metadata for the chart we want to replace
metadata = {
                "annotate": {
                    "notes": f"Last updated: {latest_time} PST"
                }
            }

#Update the chart with the latest time and date
dw.update_chart("2pT4G", metadata=metadata)

#republish the chart
dw.publish_chart("2pT4G")


