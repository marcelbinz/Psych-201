import re
import json
import jsonlines
import pandas as pd
import glob


CLEANR = re.compile('<.*?>') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext


jsonl = []
# Get a list of all CSV files in the target directory
csv_files = glob.glob("*.csv")

# Read each CSV file into a DataFrame and store them in a dictionary
dataframes = {file: pd.read_csv(file) for file in csv_files}

prompt = ""

p_id = 1
# Print the names of the files and their corresponding DataFrame shapes
for file, df in dataframes.items():
    individual_response = {}
    individual_response["participant"] = p_id
    individual_response["experiment"] = "Ying2023NIPE"

    text = "In this experiment, your task is to read a scenario of a gameshow where a player is trying to retrieve one of the three trophies (gold, silver, and bronze). We will describe the location of the trophies and the player's actions. We will ask you to rate how likely is it that the player is going for a particular trophy from 1 (definitely not this trophy) to 7 (definitely this trophy). \n\n"
    
    stimulus_cnt = 1
    for i, row in df.iterrows():
        if "query_utility_gold" in str(row["response"]):
            background = cleanhtml(row["stimuli_background"])
            condition = cleanhtml(row["stimuli_conditions"])
            text += "Stimulus "+ str(stimulus_cnt)+ ":\n"+ background + "\n" + condition + "\n"
            # text += cleanhtml(row["response"]) + "\n"
            text += "You rated the likelihood of the player going for the gold trophy as <<" + str(json.loads(row["response"])["query_utility_gold"]) + ">>\n"
            text += "You rated the likelihood of the player going for the silver trophy as <<" + str(json.loads(row["response"])["query_utility_silver"]) + ">>\n"
            text += "You rated the likelihood of the player going for the bronze trophy as <<" + str(json.loads(row["response"])["query_utility_bronze"]) + ">>\n\n\n\n"
            stimulus_cnt += 1

    individual_response["text"] = text
    jsonl.append(individual_response)
    p_id += 1


with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(jsonl)