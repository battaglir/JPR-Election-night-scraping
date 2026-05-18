# %% [markdown]
# Election Scraper and results graphs
# 
# This program will scrape the results for specific contests in Oregon, organize the data, push the data to a Datawrapper graph and automatically update the graph with the latest data.
# This program was built for the 2025 May primary. It may need to be modified in the future to work with other elections. Places where the program may need to be updated are noted in the comments.
# Licensed under a GNU General Public License v3.0
# Code written by Roman Battaglia, 2025.

# %%
#Import the required packages
import requests, datetime, json, csv, re, os, pytz, pandas as pd

#Set the time zone to Pacific Time
pacific_tz = pytz.timezone('US/Pacific')

#Set the current date and time
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

from datawrapper import Datawrapper

#Get the API key from the environment variables
#NOTE: You will need to set the environment variable in GitHub Secrets, or replace this with your API key
dw_key = os.environ.get("DATAWRAPPER_API_KEY")

#Set the API key for Datawrapper
dw = Datawrapper(dw_key)

#Set the latest time and date
latest_time = datetime.datetime.now(tz=pacific_tz).strftime("%m/%d/%Y, %I:%M %p")

# %%
# Grab the local ballot measures in Oregon

# Ensure the 'jsons' directory exists
if not os.path.exists('jsons'):
    os.makedirs('jsons')

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

#Grab the statewide measure data
#NOTE: This is for Measure 102, the gas tax.
r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=MEASURE&category=SW&raceID=300001646&osn=0&county=0&party=0")

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

#NOTE: This is for The Ashland School District measure
r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=CTYALL&category=CTY&raceID=300001691&osn=0&county=0&party=0")

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
    race_name = "Measure " + measure["RaceName"]
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

#Now grab the local county measures

#Set the raceIDs for the measures we want to track
#NOTE: You will need to update this list with the correct raceIDs for future elections.
oregon_measure_ids = ["300001668" , "300001682"]

#Set the URL to the call the Oregon results API for all statewide measures
#NOTE: This API URL may change for future elections, so you will need to update it to the correct URL for the current election. Reach out to the PIO for the Oregon SOS before the election. They did not have documentation available for the data feed. Also check the readme
# I found the right code by messing around with the URL and seeing what worked. I found that getting the type right was important, it matched up with the type in the URL of the https://results.oregonvotes.gov webpage. The other categories are all needed or results won't show up. Party can be changed to "DEM" or "REP" 

for raceids in oregon_measure_ids:
    r = requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=LMEA&category=CTY&raceID={raceids}&osn=0&county=0&party=0&map=CTY")

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
        race_name = "Measure " + measure["RaceName"]
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
    chart_id="sJKnc",
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
dw.update_chart("sJKnc", metadata=metadata)

#republish the chart
dw.publish_chart("sJKnc")

print("Oregon Measure data updated in Datawrapper")


# %%

#CD2 primary

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_CD2_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_CD2_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Party", "Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Democratic Primary
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=FED&category=SW&raceID=300037829&osn=0&county=0&party=DEM")

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
        
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon CD2 DEM Candidate races data written to {csv_filename}")

#Republican primary
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=FED&category=SW&raceID=300037830&osn=0&county=0&party=REP")

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
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon CD2 REP Candidate races data written to {csv_filename}")
# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="RcMN2",
    data=pd.read_csv("oregon_CD2_results.csv")
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
dw.update_chart("RcMN2", metadata=metadata)

#republish the chart
dw.publish_chart("RcMN2")

print("CD2 data updated in Datawrapper")

# %%

# Governor race

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_GOV_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_GOV_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Party", "Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Republican Primary
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=SWPAR&category=SW&raceID=300037840&osn=0&county=0&party=REP")

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
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon GOV REP Candidate races data written to {csv_filename}")

#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=SWPAR&category=SW&raceID=300037839&osn=0&county=0&party=DEM")

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
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon GOV DEM Candidate races data written to {csv_filename}")

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="x6bDp",
    data=pd.read_csv("oregon_GOV_results.csv")
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
dw.update_chart("x6bDp", metadata=metadata)

#republish the chart
dw.publish_chart("x6bDp")

print("GOV data updated in Datawrapper")

# %%

# US Senate race

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_SEN_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_SEN_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Party","Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Democratic Primary
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=FED&category=SW&raceID=300037825&osn=0&county=0&party=DEM")

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
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon DEM Senate Candidate races data written to {csv_filename}")

#Republican Primary
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=FED&category=SW&raceID=300037826&osn=0&county=0&party=REP")

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
        if race.get("PartyCode") == "DEM":
            race_party = "Democratic"
        elif race.get("PartyCode") == "REP":
            race_party = "Republican"
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Party": race_party,
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon REP Senate Candidate races data written to {csv_filename}")

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="foelS",
    data=pd.read_csv("oregon_SEN_results.csv")
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
dw.update_chart("foelS", metadata=metadata)

#republish the chart
dw.publish_chart("foelS")

print("US Senate data updated in Datawrapper")

# %%

# State Senate 3rd District DEM Primary

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_STSEN_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_STSEN_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=SENATE&category=SW&raceID=300037841&osn=0&county=0&party=DEM")

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
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Oregon DEM State Senate 3rd District Candidate races data written to {csv_filename}")

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="R3cxI",
    data=pd.read_csv("oregon_STSEN_results.csv")
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
dw.update_chart("R3cxI", metadata=metadata)

#republish the chart
dw.publish_chart("R3cxI")

print("State Senate 3rd District DEM data updated in Datawrapper")

#%%

# Josephine County comissioners races

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_JoCo_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_JoCo_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Race","Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

race_ids = ["300038070", "300038071"]

#Seat 1 ID:300038070 Seat 2:300038071
#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs
for race_id in race_ids:
    r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=CTYALL&category=CTY&raceID={race_id}&osn=0&county=0&party=0")

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
            if race.get("RaceName") == "County Commissioner, Position 2":
                race_name = "Position 2"
            elif race.get("RaceName") == "County Commissioner, Position 1":
                race_name = "Position 1"
            race_candidate = race["calcCandidate"]
            race_percentage = race["calcCandidatePercentage"]*100
            race_votes = race["calcCandidateVotes"]

            #Write the data to the CSV file
            writer.writerow({
                "Race": race_name,
                "Candidate": race_candidate,
                "Votes": race_votes,
                "Percent": race_percentage
            })

    print(f"Josephine County Commissioner races data written to {csv_filename}")

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="2XSaT",
    data=pd.read_csv("oregon_JoCo_results.csv")
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
dw.update_chart("2XSaT", metadata=metadata)

#republish the chart
dw.publish_chart("2XSaT")

print("Josephine County Commissioner races data updated in Datawrapper")

#%%

# Curry County comissioners race

#Set the current time and date
timenow = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d_%H-%M")

#Set the filename for the JSON file with the latest data and time
latest_file_name = f"jsons/oregon_Curry_{timenow}.json"

#Set the filename for the CSV file
#NOTE: We are using the same CSV file for both the statewide and state legislature races because they're on the same graph. Change the CSV filename if you want to separate them.
csv_filename = "oregon_Curry_results.csv"

#Set the column headers for the CSV file
csv_headers = ["Candidate", "Votes", "Percent"]

#Clear the CSV file and add the headers to the top
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

#Set the URL to the Oregon SOS API for the statewide results
#NOTE: Change this API URL to the correct one for the current election, which could change in the future. See README for details on Oregon URLs

r= requests.get(f"https://orresultswebservices.azureedge.us/ResultsAjax.svc/GetMapData?type=CTYALL&category=CTY&raceID=300034738&osn=0&county=0&party=0")

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
        race_candidate = race["calcCandidate"]
        race_percentage = race["calcCandidatePercentage"]*100
        race_votes = race["calcCandidateVotes"]

        #Write the data to the CSV file
        writer.writerow({
            "Candidate": race_candidate,
            "Votes": race_votes,
            "Percent": race_percentage
        })

print(f"Curry County Commissioner races data written to {csv_filename}")

# %%

#Call datawrapper and replace the data in the chart with the latest data
dw.add_data(
    #NOTE: Change the chart_id to the correct chart ID for the graph you want to update. You can find this in the URL of the chart in Datawrapper. I created the graphs first manually, then grabbed the chart
    chart_id="wghXn",
    data=pd.read_csv("oregon_Curry_results.csv")
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
dw.update_chart("wghXn", metadata=metadata)

#republish the chart
dw.publish_chart("wghXn")

print("Curry County Commissioner races data updated in Datawrapper")

#%%

# Delete any JSON files in the directory that are older than 24 hours
now = datetime.datetime.now(tz=pacific_tz)
for filename in os.listdir('jsons/.'):
    if filename.endswith('.json'):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(f'jsons/{filename}'), tz=pacific_tz)
        if (now - file_time).total_seconds() > 24 * 3600:
            os.remove(f'jsons/{filename}')
            print(f"Deleted old file: {filename}")
