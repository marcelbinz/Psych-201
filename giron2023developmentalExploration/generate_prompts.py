import numpy as np
import pandas as pd
import jsonlines
#from utils import randomized_choice_options

data_path = "/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/giron2023.csv"
data = pd.read_csv(data_path)

print(len(data["x"].dropna())) # get total number of choices
IDs = set(data["id"])


instr = "Welcome to the game! In this game you will select locations on a 8-by-8 grid trying to gain as many points as possible. \n" \
    "To select a location on the grid, provide its x and y coordinates as such: [x_position, y_position]. Once you select a location, you will be told the number of points you obtained at that location. \n" \
    "One location will be selected for you at the start of each round, and you'll be told the number of points in that location. \n" \
    "You will have to work out which locations are likely to contain the most points in order to maximise your score. If one location has a high number of points, it's likely that nearby locations will also have a lot of points. If a location has few points, nearby locations are likely to also have few points.\n" \
    "You can select the same location several times. Each time you will get a similar number of points.\n"



def get_prompt(ID):
    prompt = instr

    dat = data.loc[(data["id"] == ID)]
    Nblocks = len(dat["round"].unique()) # differs by participant
    ntrials = 25
    for block in range(2, Nblocks+1):
        block_dat = dat.loc[dat["round"] == block]
        if len(block_dat["x"].dropna()) == 0: # if there are no choices in this block
            continue

        prompt += "Round " + str(block-1) + " of " + str(Nblocks-1) + ".\n"
        
        chosen_x = np.int64(block_dat.loc[block_dat["trial"] == 0, "x"].item())
        chosen_y = np.int64(block_dat.loc[block_dat["trial"] == 0, "y"].item())

        prompt += "The location [" + str(chosen_x) + ", " + str(chosen_y) + "] has already been revealed for you. It contains " + str(np.int64(block_dat.loc[block_dat["trial"] == 1, "z"].item())) + " points.\n"

        for trial in range(1,(ntrials+1)):
            chosen_x = np.int64(block_dat.loc[block_dat["trial"] == trial, "x"].item())
            chosen_y = np.int64(block_dat.loc[block_dat["trial"] == trial, "y"].item())
            prompt += "On trial " + str(trial) + " of 25 you picked the location <<[" + str(chosen_x) + ", " + str(chosen_y) + "]>> and received " + str(np.int64(block_dat.loc[block_dat["trial"] == trial, "z"].item())) + " points.\n"

        
        prompt += "End of the round.\n"

    return prompt

print(get_prompt(1))

all_prompts = []


for ID in IDs:
#for ID in [2]:
    #choice_options = randomized_choice_options(num_choices=4)

    txt = get_prompt(ID)

    #print(prompt)
    all_prompts.append({'text': txt,
                        'experiment': data.loc[data["id"] == ID, "experiment"].unique().item(),
                        'participant': ID,
                        'age': data.loc[data["id"] == ID, "age_years"].unique().item(),
                        'gender': data.loc[data["id"] == ID,"gender"].unique().item()})

print(all_prompts)
with jsonlines.open('giron2023developmentalExploration/prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
