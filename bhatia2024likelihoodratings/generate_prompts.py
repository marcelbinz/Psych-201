import pandas as pd
import jsonlines
import os

# Load data where rows are behaviors and columns are participants' likelihood ratings
datasets = ["Study 1/data - full clean.csv", "Study 2/data - full clean.csv"]

# Instructions for LLM
instructions = """You will be given a list of behaviors or activities.
Your task is to rate how likely you are to do these behaviors or activities on a scale from 0 to 100. 
A rating closer 0 means that you are LESS LIKELY than others to do the behavior or activity. A rating closer 100 means that you are MORE LIKELY than others do the behavior or activity.


"""

# Initialize list to store prompts
all_prompts = []

# Iterate over dataframes
for dataset in datasets:
    
    # Load data
    df = pd.read_csv(dataset)

    # Reshuffle dataframe so that likelihood ratings are in random order
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Participant IDs are stored as column names
    participant_ids = df_shuffled.columns[3:]

    # Iterate over participants
    for participant_id in participant_ids:

        # Get behavior and participant's likelihood ratings
        responses = df[['ITEM', participant_id]]

        responses_as_text = ""
        
        # Iterate over participants' responses
        for _, row in responses.iterrows():
            
            # Construct prompt for LLM
            responses_as_text += "'" + str(row['ITEM']) + ".'" + " You indicate a rating of <<" + str(row[participant_id]) + ">>.\n"
        
        # Append prompt to list
        all_prompts.append({
            'text': instructions + responses_as_text, 
            'experiment': 'bhatia2024likelihoodratings/' + dataset, 
            'participant': participant_id,
            'nationality': 'United States'
        })

# Get the absolute path of this Python script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the prompts.jsonl file in the same directory
filename = os.path.join(script_dir, 'prompts.jsonl')

# Write json file
with jsonlines.open(filename, 'w') as writer:
    writer.write_all(all_prompts)
