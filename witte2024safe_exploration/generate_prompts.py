import numpy as np
import pandas as pd
import jsonlines
#from utils import randomized_choice_options

data_path = "/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/safe_exploration.csv"
data = pd.read_csv(data_path)
# remove all rows where blocknr = 6 (bonus round)
data = data[data.blocknr != 6]
data = data.reset_index(drop=True)
# recode blocknr such that all rows where blocknr > 6 are set to blocknr - 1 (to make it indexed between 1 and 10)
data.loc[data.blocknr > 6, "blocknr"] = data.loc[data.blocknr > 6, "blocknr"] - 1

print(len(data["x"].dropna()))
IDs = set(data["ID"])
Nblocks = len(data["blocknr"].unique())


instr = "Welcome to the game! In this game you play the role of a sailor trying to catch fish from the ocean.\n" \
    "You can choose to go fishing in any of the squares of an 11-by-11 grid representing the ocean. The squares are indexed by their row (0-10) and their column (0-10). To select a square you provide its location like [x_index, y_index]. Once you select a square, you will be told the number of fish you caught in that square.\n" \
    "One square will be selected for you at the start of each round, and you'll be told the number of fish in that square." \
    "You will have to work out which locations are likely to contain the most fish in order to maximise your score. If one square has a high number of fish, it's likely that nearby squares will also have a lot of fish. If a square has few fish, nearby squares are likely to also have few fish.\n" \
    "You can select the same square several times. Each time you will get a similar number of fish.\n" \
    "However, there is a dangerous creature called the Kraken lurking in the ocean somewhere, which feeds on fish. You must avoid finding the Kraken. If you do, it will steal all the fish you have collected in that round! When the kraken is nearby, you will be told so in the begginning of the round. Sometimes the kraken will be somewhere else, and you won't be at risk of finding it. \n" \
    "Areas where the Kraken lurks will have very few fish as it has started to eat them. When the kraken is nearby, if you find a square with 50 fish or fewer, there is a 100 percent chance that the Kraken will be there. If you find a square with more than 50 fish, you'll always be safe. \n" \
    "The number of fish in the ocean does not decrease as the task goes on, or when you click on a square more than once."



def get_prompt(ID):
    prompt = instr

    dat = data.loc[(data["ID"] == ID)]

    for block in range(1, Nblocks+1):
        block_dat = dat.loc[dat["blocknr"] == block]
        if len(block_dat["x"].dropna()) == 0:
            continue

        prompt += "Round " + str(block) + " of " + str(Nblocks) + ".\n"

        if block_dat["krakenPres"].unique() == 0: # safe round
            prompt += "The kraken is feeding elsewhere.\n"
            ntrials = 11

        else: # risky round
            prompt += "The kraken is nearby. \n"
            # number of trials might be less than 11 if kraken is found
            ntrials = len(block_dat["x"].dropna())
        
        chosen_x = np.int64(block_dat.loc[block_dat["click"] == 1, "x"].item())
        chosen_y = np.int64(block_dat.loc[block_dat["click"] == 1, "y"].item())

        prompt += "The square [" + str(chosen_x) + ", " + str(chosen_y) + "] has already been revealed for you. It contains " + str(np.int64(block_dat.loc[block_dat["click"] == 1, "z"].item())) + " fish.\n"

        for trial in range(2,(ntrials+1)):
            chosen_x = np.int64(block_dat.loc[block_dat["click"] == trial, "x"].item())
            chosen_y = np.int64(block_dat.loc[block_dat["click"] == trial, "y"].item())
            prompt += "On trial " + str(trial-1) + " of 10 you picked the square <<[" + str(chosen_x) + ", " + str(chosen_y) + "]>> and received " + str(np.int64(block_dat.loc[block_dat["click"] == trial, "z"].item())) + " fish.\n"

        if block_dat["krakenCaught"].unique() == 1:
            prompt += "You found the kraken! It stole all fish you found on this round. The round is over.\n"
        
        else:
            prompt += "End of the round.\n"

    return prompt

print(get_prompt(1))

all_prompts = []


for ID in IDs:
#for ID in [2]:
    #choice_options = randomized_choice_options(num_choices=4)

    txt = get_prompt(ID)

    if data.loc[data["ID"] == ID, "gender"].unique().item() == 0:
        gender = "male"
    elif data.loc[data["ID"] == ID, "gender"].unique().item() == 1:
        gender = "female"
    else:
        gender = "other"

    #print(prompt)
    all_prompts.append({'text': txt,
                        'experiment': 'witte2024safe_exploration/',
                        'participant': ID,
                        'age': data.loc[data["ID"] == ID, "age"].unique().item(),
                        'gender': gender,
                        'STICSA': data.loc[data["ID"] == ID, "STICSA"].unique().item(),
                        'STICSAcog': data.loc[data["ID"] == ID, "STICSAcog"].unique().item(),
                        'STICSAsoma': data.loc[data["ID"] == ID, "STICSAsoma"].unique().item(),
                        'IUS': data.loc[data["ID"] == ID, "IUS"].unique().item(),
                        'CAPE_depressed': data.loc[data["ID"] == ID, "CAPE_depressed"].unique().item(),
                        'CAPE_positive': data.loc[data["ID"] == ID, "CAPE_positive"].unique().item(),
                        'CAPE_negative': data.loc[data["ID"] == ID, "CAPE_negative"].unique().item(),
                        'RRQ': data.loc[data["ID"] == ID, "RRQ"].unique().item(),
                        'PID5_negativeAffect': data.loc[data["ID"] == ID, "PID5_negativeAffect"].unique().item()})

with jsonlines.open('witte2024safe_exploration/prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
