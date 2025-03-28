import numpy as np
import pandas as pd
import jsonlines
import sys
import os
sys.path.append("..")

# Define paths
mri_datapath = "data/mri_study/behaviour/processed/"
patient_datapath = "data/lesion_patient_study/behaviour/"

# Get all CSV files from post scan session
post_scan_path = mri_datapath + "/post_scan_session"
post_scan_files = [f for f in os.listdir(post_scan_path) if f.endswith('.csv')]
post_scan_datasets = [os.path.join(post_scan_path, f) for f in post_scan_files]

# Get all CSV files from scan session 
scan_path = mri_datapath + "/scan_session"
scan_files = [f for f in os.listdir(scan_path) if f.endswith('.csv')]
scan_datasets = [os.path.join(scan_path, f) for f in scan_files]

# Get all CSV files from age matched controls
control_path = patient_datapath + "/age_matched_controls"
control_files = [f for f in os.listdir(control_path) if f.endswith('.csv')]
control_datasets = [os.path.join(control_path, f) for f in control_files]

# Get all CSV files from patient data
patient_path = patient_datapath + "/all_patient_data"
patient_files = [f for f in os.listdir(patient_path) if f.endswith('.csv')]
patient_datasets = [os.path.join(patient_path, f) for f in patient_files]

# Read all datasets separately
scan_data = pd.concat([pd.read_csv(dataset) for dataset in scan_datasets], ignore_index=True)
post_scan_data = pd.concat([pd.read_csv(dataset) for dataset in post_scan_datasets], ignore_index=True)
control_data = pd.concat([pd.read_csv(dataset) for dataset in control_datasets], ignore_index=True)
control_data['participant'] = control_data['participant'] + 200 # make temporary unique IDs for control patients
patient_data = pd.concat([pd.read_csv(dataset) for dataset in patient_datasets], ignore_index=True)

# Get max values from scan data per participant
scan_maxes = scan_data.groupby('participant').agg({
    'block': 'max',
    'total_trial_number': 'max'
}).to_dict('index')

# Add scan maxes to post-scan data for matching participants
for participant in post_scan_data['participant'].unique():
    if participant in scan_maxes:
        mask = post_scan_data['participant'] == participant
        post_scan_data.loc[mask, 'block'] += scan_maxes[participant]['block']
        post_scan_data.loc[mask, 'total_trial_number'] += scan_maxes[participant]['total_trial_number']

# Add Age and Group info
scan_data['age'] = "18-35"
post_scan_data['age'] = "18-35" 
control_data['age'] = "50-75" 
patient_data['age'] = np.nan

scan_data['lesion-group'] = "no-lesion-control"
post_scan_data['lesion-group'] = "no-lesion-control"
control_data['lesion-group'] = "no-lesion-control"
patient_data['lesion-group'] = np.nan

# Combine all datasets
all_data = pd.concat([scan_data, post_scan_data, control_data, patient_data], ignore_index=True)

# add lesion locs (data not available online)
lesion_ids = [545, 345, 350, 344, 352, 346, 347, 333, 327, 319, 325, 330, 315, 317, 303, 306, 310, 304, 305, 339, 407, 349, 348]
lesion_ages = [57, 54, 56, 76, 69, 49, 47, 58, 46, 60, 49, 78, 66, 51, 53, 65, 73, 62, 65, 57, 32, 60, 49]
lesion_locs = ["PFC-lesion", "non-PFC-lesion", "non-PFC-lesion", "PFC-lesion", "non-PFC-lesion", "PFC-lesion", "non-PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "PFC-lesion", "non-PFC-lesion", "non-PFC-lesion", "non-PFC-lesion", "PFC-lesion"]

# Update age and lesion group for lesion patients
for idx, lesion_id in enumerate(lesion_ids):
    mask = all_data['participant'] == lesion_id
    all_data.loc[mask, 'age'] = str(lesion_ages[idx])
    all_data.loc[mask, 'lesion-group'] = lesion_locs[idx]

all_prompts = []

participant_ids = all_data['participant'].unique()
for idx,participant in enumerate(participant_ids):
    df_participant = all_data[(all_data['participant'] == participant)]
    age = df_participant["age"].unique().item()
    group = df_participant["lesion-group"].unique().item()
    num_trials = df_participant['total_trial_number'].max() + 1

    current_prompt = f'In this game, your aim is to fill as many fishing nets as possible with seafood. You will be given a net, and you have to fill it with seafood until it is full. You get a point every time you fill a net. You can fill your net with fish, octopus or crab. However, here is the key part: You can only collect one type of seafood in your net at a time. If you decide to choose a different type of seafood from the type currently in your net, you will have to throw out all the seafood you have already caught. The available quantities of fish, octopus and crab in your fishing patch will gradually change over time. Sometimes, one type of seafood might become more bountiful as a new population enters the fishing patch, or one type of seafood might become more scarce as a population leaves. You will have {num_trials-1} total to play. Try and fill as many nets as possible!'
    
    for trial in range(1,num_trials):

        df_trial = df_participant[(df_participant['total_trial_number'] == trial)]

        goal_size = df_trial['goal_size'].item()
        net_contents = round(df_trial['net_contents'].item(), 4)
        fish_offer = round(df_trial['magnitudes_1'].item(), 4)
        octopus_offer = round(df_trial['magnitudes_2'].item(), 4)
        crab_offer = round(df_trial['magnitudes_3'].item(), 4)
        choice_idx = df_trial['choice'].item()
        choice = ['fish','octopus','crab'][choice_idx-1]
        choice_amount = [fish_offer, octopus_offer, crab_offer][choice_idx-1]

        if df_trial['trial_number'].item() == 1:

            trial_text = f"New block. Your current net size is {goal_size}. You have collected {net_contents}. The available  quantity of fish is {fish_offer}, the quantity of octopus offer is {octopus_offer} and the current crab offer is {crab_offer}. "

            current_prompt += f"{trial_text}. You choose to collect<<{choice}>>. {choice_amount} of {choice} is added to your net. "
        else:
             
            goal_idx = df_participant.loc[df_participant['total_trial_number'] == trial-1, 'choice'].item()
            goal_item = ['fish','octopus','crab'][goal_idx-1]

            trial_text = f"Your current net size is {goal_size}. You have collected {net_contents} of {goal_item} in your net. The current fish offer is {fish_offer}, the current octopus offer is {octopus_offer} and the current crab offer is {crab_offer}. "
            current_prompt += f"{trial_text}. You choose to collect<<{choice}>>. {choice_amount} of {choice} is added to your net. "


    all_prompts.append({"text": current_prompt, "experiment": "holton2024goalcommitment", "participant": str(idx), "age":age, "diagnosis":group})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)