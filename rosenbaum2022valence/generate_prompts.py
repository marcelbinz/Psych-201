import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options



dataset = "MemDF.csv"
all_prompts = []


df = pd.read_csv(dataset)
df = df[df["TrialType"] != 2]

metadata = pd.read_csv("widedf.csv")
additional_columns = ["Gender", "WASI", "DOSPERT", "BIS11", "BAS_Drive", "BAS_Fun_Seeking", "BAS_Reward_Response", "BAS_total", "BIS", "Reward"]
df = df.merge(metadata[["SubjectNumber"] + additional_columns], on="SubjectNumber", how="left")

print(df)


df["NewTrialNumber"] = 0

for participant in df['SubjectNumber'].unique():
    RTs = []
    anyrisk = [] # did they make a risky choice? (1 if yes, 0 if no, regardless of condition)
    risky_resp = [] # risky choice in condition risky
    participant_mask = df["SubjectNumber"] == participant
    trial_numbers = range(1, participant_mask.sum() + 1)
    df.loc[participant_mask, "NewTrialNumber"] = trial_numbers
    num_trials = df["NewTrialNumber"].max()

    df_participant = df[(df['SubjectNumber'] == participant)]
    age = df_participant["Age"].iloc[0]
    participant_data = df_participant.iloc[0]  # Extract the first row of the group
    additional_data = {
        col.lower(): participant_data[col].item() if isinstance(participant_data[col], (np.generic, np.ndarray)) else
        participant_data[col]
        for col in additional_columns}

    #STICSAT_total_Somatic = df_participant['STICSAT_total_Somatic'].iloc[0]
    #STICSAT_total_Cognitive = df_participant['STICSAT_total_Cognitive'].iloc[0]
    #STAIT_total_present = df_participant['STAIT_total_present'].iloc[0]
    #STAIT_total_absent = df_participant['STAIT_total_absent'].iloc[0]

    choice_options = randomized_choice_options(num_choices=9)

    memory_choices =  ["definitely old", "maybe old", "maybe new", "definitely new"]

    prompt = ( "In this task, you have to repeatedly choose between two machines.\n"\
        "There are five machines in total, but only two will be available at a time.\n"\
        "The machines are labeled as follows: " + choice_options[0] + ', ' + choice_options[1] + ', ' + choice_options[2] + ', ' +
               choice_options[3] + ', ' + choice_options[4] + "\n"\
        "When you select one of the machines, you will either win points or no receive no points.\n" \
        "Your goal is to choose the slot machines that will give you the most points.\n" \
        "You will receive feedback about the outcome after making a choice. \n"\
        "After having received feedback, you will be shown an image. \n"\
        "Your task is to identify whether this image was presented before or not. \n"\
        "Choose "+ choice_options[5] + " to identify the image as " + memory_choices[0] + ", " + choice_options[6] + " to identify the image as " + memory_choices[1] +
        ", " + choice_options[7] + " to identify the image as " + memory_choices[2] +  ", " + choice_options[8] + " to identify the image as " + memory_choices[3] +"\n\n")

    for _, row in df_participant.iterrows():
        #prompt += 'Game ' + str(task) + ':\n'
        trial = row['NewTrialNumber']
        condition = row['FullTrialType']
        image_response = row['MemResp']
        if image_response == 5:
            mem_choice = choice_options[5]
        elif image_response == 6:
            mem_choice = choice_options[6]
        elif image_response == 7:
            mem_choice = choice_options[7]
        elif image_response == 8:
            mem_choice = choice_options[8]

        if condition == 1:
            choice_1 = choice_options[1]
            choice_2 = choice_options[3]
        elif condition == 2:
            choice_1 = choice_options[1]
            choice_2 = choice_options[4]
        elif condition == 3:
            choice_1 = choice_options[2]
            choice_2 = choice_options[4]
        elif condition == 4:
            choice_1 = choice_options[0]
            choice_2 = choice_options[0]
        elif condition == 5:
            choice_1 = choice_options[1]
            choice_2 = choice_options[1]
        elif condition == 6:
            choice_1 = choice_options[2]
            choice_2 = choice_options[2]
        elif condition == 7:
            choice_1 = choice_options[3]
            choice_2 = choice_options[3]
        elif condition == 8:
            choice_1 = choice_options[4]
            choice_2 = choice_options[4]
        elif condition == 9:
            choice_1 = choice_options[1]
            choice_2 = choice_options[2]
        elif condition == 10:
            choice_1 = choice_options[2]
            choice_2 = choice_options[3]
        elif condition == 11:
            choice_1 = choice_options[3]
            choice_2 = choice_options[4]
        elif condition == 12:
            choice_1 = choice_options[0]
            choice_2 = choice_options[3]
        elif condition == 13:
            choice_1 = choice_options[0]
            choice_2 = choice_options[4]
        elif condition == 14:
            choice_1 = choice_options[0]
            choice_2 = choice_options[1]
        elif condition == 15:
            choice_1 = choice_options[0]
            choice_2 = choice_options[2]


        df_trial = df_participant[(df_participant['NewTrialNumber'] == trial)]
        c = df_trial["UnshuffledResp"].item() - 1
        r = df_trial['Outcome'].item()
        image = df_trial['MemIdx'].item()
        RTs.append(df_trial["RT"].item())
        risky_resp.append(df_trial["RiskyResp"].item())
        anyrisk.append(df_trial["AnyRisk"].item())
        choices = [choice_1, choice_2]
        prompt += 'You have a choice between ' + str(choice_1) + ' and ' + str(choice_2) + '. You choose <<' + str(choices[c]) + '>> and get ' + str(r) + ' points.\n'\
                    'The presented image is ' + str(image) + '. You choose <<' + str(mem_choice) + '>>.\n'\


    prompt += '\n'

    prompt = prompt[:-2]
    #print(prompt)
    #print(RTs)

    all_prompts.append({'text': prompt,
        'experiment': 'rosenbaum2022valence/' + dataset,
        'participant': str(participant),
        'RTs': RTs,
        'age': str(age),
        'risky_resp': risky_resp,
        'anyrisk': anyrisk,
        **additional_data
    })



#### checks #####
# Count the number of trials per participant
trial_counts = df.groupby("SubjectNumber")["NewTrialNumber"].count()

# Calculate the mode (most common number of trials)
most_common_trials = trial_counts.mode()[0]

# Identify participants with differing trial counts
different_counts = trial_counts[trial_counts != most_common_trials]

# Count how many participants have different trial counts
num_different_participants = len(different_counts)

# Calculate the total number of differing trials
total_differing_trials = (different_counts - most_common_trials).abs().sum()

# Print results
print(f"Most common number of trials: {most_common_trials}")
print(f"Number of participants with different trial counts: {num_different_participants}")
print(f"Total number of differing trials: {total_differing_trials}")


if df.isnull().values.any():
    print("There are NaN values in the DataFrame.")
    print(df.isnull().sum())  # Number of NaNs per column
else:
    print("No NaN values in the DataFrame.")

# Group by participant
for participant, group in df.groupby("SubjectNumber"):
    # Calculate the lengths of RT and choices columns
    rt_length = group["RT"].notnull().sum()  # Count non-null RTs
    choice_length = group["UnshuffledResp"].notnull().sum()  # Count non-null choices

    # Compare the lengths
    if rt_length != choice_length:
        print(f"Participant {participant} has mismatched lengths:")
        print(f"  RT length: {rt_length}")
        print(f"  Choices length: {choice_length}")
    else:
        print(f"Participant {participant} has matching lengths.")

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)


