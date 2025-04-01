# %% LIBRARY IMPORT

import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
import pickle
from utils import randomized_choice_options

# %% PARAMETERS

datasets = ["behavior_24-01-22_day1.pkl", "behavior_24-01-22_day2.pkl", "behavior_24-01-22_day2B.pkl", "behavior_24-01-22_day3.pkl", "behavior_24-01-22_day3B.pkl", 
            "behavior_24-01-29_day1.pkl", "behavior_24-01-29_day2.pkl", "behavior_24-01-29_day2B.pkl", "behavior_24-01-29_day3.pkl", "behavior_24-01-29_day3B.pkl",
            ]

transdiagnostics_files = ["transdiagnostics_22A.csv", "transdiagnostics_22B.csv", 
                    "transdiagnostics_29A.csv", "transdiagnostics_29B.csv"
                    ]

all_prompts = []

# %% READ IN TRANSDIAGNOSTICS DATA

transdiagnostics_df = pd.DataFrame()

for file in transdiagnostics_files:
    transdiagnostics_df = pd.concat([transdiagnostics_df, pd.read_csv(file, index_col=0)])

transdiagnostics_df
        
# %% DATASET COMPILATION

num_trials = 50
num_tasks = 9
light_names = ['blue', 'red']

for dataset in datasets:
    df = pd.read_pickle(dataset)

    if "day1" in dataset or "day2" in dataset:
        num_choices = 3
        reversal_probability = 0.1
        if "day1" in dataset:
            n_train_episodes_groups = [4, 5]
        else:
            n_train_episodes_groups = [5, 4]
        
    elif "day3" in dataset:
        num_choices = 4
        reversal_probability = 0.05
        n_train_episodes_groups = [5, 4]

    for index, participant in df.iterrows():

        ## METADATA
        index = int(index)
        transdiagnostics_participant = transdiagnostics_df.loc[index]
        group = participant['group']
        n_train_episodes = n_train_episodes_groups[group]

        ## PROMPT GENERATION
        choice_options = randomized_choice_options(num_choices=num_choices)

        if "day1" in dataset:
            prompt = "You enter a casino. You are playing a new game for the first time. " + \
                f"The game involves a table with two lights, a blue one and a red one. One of these is \"lucky\" and pays out coins if bet on correctly. " + \
                f"The \"lucky\" light may switch roughly once every {num_trials} rounds, with a {reversal_probability*100}% chance of switching after each round. You have two options each round: " + \
                "You can either bet on a light or observe to reveal the lucky light without making a bet. If a bet is placed and it's correct, a coin is earned, " + \
                f"but the result is only revealed at the end of {num_trials} rounds. Additionally, there's a chance that a bet might be placed on the wrong light due to an error, " + \
                "though this never occurs more than half of the time. " + \
                f"Your goal is to maximize the number of coins earned over the {num_trials} rounds. The best strategy " + \
                "involves balancing between betting and observing, with the optimum depending on the control over bet placement in different sets. " + \
                f"The game is played over {num_tasks} sets of {num_trials} rounds each, after each of which you will be told how many points you earned.\n" + \
                f"For the first {n_train_episodes}, you will receive a rough indication of the level of control at the start of the set; after that, you will need to infer it entirely from feedback." + \
                f"Press {choice_options[0]} to observe, {choice_options[1]} to bet on the blue light, or {choice_options[2]} to bet on the red light.\n"
        elif "day2" in dataset:
            prompt = "You enter a casino. This is your second day playing the same game, so you already have some experience but with slightly different settings and rules. " \
                f"The game involves a table with two lights, a blue one and a red one. One of these is \"lucky\" and pays out coins if bet on correctly. " + \
                f"The \"lucky\" light may switch roughly once every {num_trials} rounds, with a {reversal_probability*100}% chance of switching after each round. You have two options each round: " + \
                "You can either bet on a light or observe to reveal the lucky light without making a bet. If a bet is placed and it's correct, a coin is earned, " + \
                f"but the result is only revealed at the end of {num_trials} rounds. Additionally, there's a chance that a bet might be placed on the wrong light due to an error, " + \
                "though this never occurs more than half of the time. " + \
                f"Your goal is to maximize the number of coins earned over the {num_trials} rounds. The best strategy " + \
                "involves balancing between betting and observing, with the optimum depending on the control over bet placement in different sets. " + \
                f"The game is played over {num_tasks} sets of {num_trials} rounds each, after each of which you will be told how many points you earned.\n" + \
                f"For the first {n_train_episodes}, you will receive a rough indication of the level of control at the start of the set; after that, you will need to infer it entirely from feedback." \
                f"Press {choice_options[0]} to observe, {choice_options[1]} to bet on the blue light, or {choice_options[2]} to bet on the red light.\n"
        elif "day3" in dataset:
            prompt = "You enter a casino. You have already played a similar version of this game previously, but today will involve a new action and mechanics. " \
                f"The game involves a table with two lights, a blue one and a red one. One of these is \"lucky\" and pays out coins if bet on correctly. " + \
                f"The \"lucky\" light may switch roughly once every {num_trials} rounds, with a {reversal_probability*100}% chance of switching after each round. You have two options each round: " + \
                "You can either bet on a light, observe to reveal the lucky light without making a bet, or sleep to increase your amount of control for the rest of the set. If a bet is placed and it's correct, a coin is earned, " + \
                f"but the result is only revealed at the end of {num_trials} rounds. Additionally, there's a chance that a bet might be placed on the wrong light due to an error, " + \
                "though this never occurs more than half of the time. " + \
                f"Your goal is to maximize the number of coins earned over the {num_trials} rounds. The best strategy " + \
                "involves sleeping more when you have less control, with the optimum depending on the control over bet placement in different sets. " + \
                f"The game is played over {num_tasks} sets of {num_trials} rounds each, after each of which you will be told how many points you earned.\n" + \
                f"Press {choice_options[0]} to observe, {choice_options[1]} to bet on the blue light, {choice_options[2]} to bet on the red light, or {choice_options[3]} to sleep.\n"

        for task in range(num_tasks):
            transitions = participant['transitions_ep'][task]
            rewards = participant['rewards_tallies'][task]
            efficacy = participant['effs'][task]

            prompt += f'Set {str(task + 1)}/{num_tasks}:\n'
            if task < n_train_episodes:
                if efficacy == 0:
                    descriptor_control = 'no'
                    descriptor_machine = 'half the time (entirely unpredictably, so it is impossible to time your bets accordingly)'
                elif efficacy < 1/3:
                    descriptor_control = 'a little'
                    descriptor_machine = 'slightly more than half the time (entirely unpredictably, so it is impossible to time your bets accordingly)'
                elif efficacy < 2/3:
                    descriptor_control = 'some'
                    descriptor_machine = 'most of the time'
                elif efficacy < 1:
                    descriptor_control = 'a lot of'
                    descriptor_machine = 'almost always'
                else:
                    descriptor_control = 'complete'
                    descriptor_machine = 'always'
                prompt += f"In this set, you have {descriptor_control} control, meaning that your bets will succeed ({descriptor_machine}). "
            else:
                prompt += "In this set, you will have to infer the level of control entirely from the feedback you receive. "
            
            for trial in range(num_trials):

                light = int(transitions[trial][0])
                choice_original = transitions[trial][1]
                choice_final = transitions[trial][2]
                
                ## remap choice_index
                if choice_original == 0.5:
                    choice_index = 0
                elif choice_original == 0:
                    choice_index = 1
                elif choice_original == 1:
                    choice_index = 2
                if choice_original == -1:
                    choice_index = 3
            
                prompt += f"Round {trial+1}/{num_trials}. You press <<{choice_options[choice_index]}>>. "

                if choice_index == 0:
                    prompt += f"You observed and see the {light_names[light]} light up. \n"
                elif choice_index == 1 or choice_index == 2:
                    if choice_index == 1:
                        prompt += f"You bet on the blue light. "
                    elif choice_index == 2:
                        prompt += f"You bet on the red light. "
                    if choice_original == choice_final:
                        prompt += f"You executed this bet successfully. \n"
                    else:
                        prompt += f"You didn't execute this bet successfully and it is switched to the other light. "
                else:
                    prompt += f"You slept and increased your control. \n"

            prompt += f"You have successfully completed this set and earned {rewards} coins. \n"

        prompt = prompt[:-2]
        print(prompt)

        ## PROMPT STORAGE
        all_prompts.append({'text': prompt, 'experiment': 'sandbrink2024metacontrol/' + dataset, 'participant': int(index), 'FACSIMILE A/D': float(transdiagnostics_participant["AD"]), "FACSIMILE Compul": float(transdiagnostics_participant["Compul"]), "FACSIMILE SW": float(transdiagnostics_participant["SW"])})

print(all_prompts)
print("Number of entries: ", len(all_prompts))
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
