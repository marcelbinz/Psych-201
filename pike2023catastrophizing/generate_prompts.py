import numpy as np
import pandas as pd
import jsonlines
import sys
import os
sys.path.append("..")


# Define function to make randomized choices
def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

# Set working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

datasets = ["bart_lc_modeldata_main.txt", "bart_hc_modeldata_main.txt"]
all_prompts = []
demographics = pd.read_csv("main_data.csv")

for dataset in datasets:
    df = pd.read_csv(dataset, sep="\t")
    num_trials = 30

    # Loop through participant and check if demographics data is also available
    for participant in df['subjID'].unique():
        if participant in demographics.id.unique():

            choice_options = randomized_choice_options(num_choices=2)
            df_participant = df[(df['subjID'] == participant)]
            dem_participant = demographics.loc[demographics.id == participant]
            participant_points = 0
            
            # For low cost block
            if dataset == "bart_lc_modeldata_main.txt":
                prompt = "Your aim in this task is to win points by pumping the balloon up. You may pump the balloon up as many times as you wish by pressing the " + choice_options[0] + " button on your keyboard: every pump will give you more points, but it also increases the risk of the balloon bursting.\n"\
                        "The speed at which you pump does not affect the likelihood of the balloon bursting. In this block, if you burst the balloon you lose the points from that balloon.\n"\
                        "You can stop pumping the balloon up at any point and collect the points you have earnt, by pressing the " + choice_options[1] + " button. There are 30 balloons in this block.\n\n"
            # For high cost block
            elif dataset == "bart_hc_modeldata_main.txt":
                prompt = "Your aim in this task is to win points by pumping the balloon up. You may pump the balloon up as many times as you wish by pressing the " + choice_options[0] + " button on your keyboard: every pump will give you more points, but it also increases the risk of the balloon bursting.\n"\
                        "The speed at which you pump does not affect the likelihood of the balloon bursting.\n"\
                        "In this block, if you burst the balloon you lose the points from that balloon, and another 1000 points as a penalty. You can stop pumping the balloon up at any point and collect the points you have earnt, by pressing the " + choice_options[1] + " button on your keyboard. There are " + str(df_participant.shape[0]) + " balloons in this block.\n\n"

            # Loop through trials
            for trial in range(df_participant.shape[0]):
                prompt += f'Balloon {trial+1}:\n'
                df_trial = df_participant.iloc[trial]

                # Loop through pumps
                for pump in range(df_trial.pumps):
                    trial_points = (pump+1)*10
                    prompt += 'You press <<' + choice_options[0] + '>> to pump up the balloon and get +10 points. You could collect ' + str(trial_points) + ' points.\n'
                # If the trial ends in explosion
                if df_trial.explosion:
                    # You loose all yours points in low cost condition
                    if dataset == "bart_lc_modeldata_main.txt":
                        participant_points += 0
                        prompt += 'You press <<' + choice_options[0] + '>> to pump up the balloon. The balloon bursts and you loose all your points from this balloon. You have ' + str(participant_points) + ' points in total.\n'
                    # You loose all your points and another thousand points in high cost condition
                    elif dataset == "bart_hc_modeldata_main.txt":
                        participant_points -= 1000
                        prompt += 'You press <<' + choice_options[0] + '>> to pump up the balloon. The balloon bursts and you loose all your points from this balloon and another 1000 points. You have ' + str(participant_points) + ' points in total.\n'

                # If it doesn't end in explosion, you just get your points
                else:
                    participant_points += trial_points
                    prompt += 'You press <<' + choice_options[1] + '>> to collect your ' + str(trial_points) + ' points. You have ' + str(participant_points) + ' points in total.\n'
            prompt += '\n'

            prompt = prompt[:-2]
            print(prompt)

            all_prompts.append({'text': prompt,
                'experiment': 'pike2023catastrophizing/',
                'participant': str(participant),
                'age': 'NaN' if np.isnan(dem_participant.age.values[0]) else int(dem_participant.age.values[0]),
                'stai': int(dem_participant.total_stai.values[0]),
                'gad7': int(dem_participant.total_gad7.values[0]),
                'phq8': int(dem_participant.total_phq8.values[0]),
                'pswq': int(dem_participant.total_pswq.values[0]),
            })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)