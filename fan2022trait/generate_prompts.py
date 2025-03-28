import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["exp1_bandit_task_scale.csv"] # TODO EXPERIMENT 2
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)

    num_tasks = df.block.max() + 1
    num_trials = df.trial.max() + 1


    for participant in df['sub'].unique():
        RTs = []

        df_participant = df[(df['sub'] == participant)]
        age = df_participant.age.iloc[0]
        STICSAT_total_Somatic = df_participant['STICSAT_total_Somatic'].iloc[0]
        STICSAT_total_Cognitive = df_participant['STICSAT_total_Cognitive'].iloc[0]
        STAIT_total_present = df_participant['STAIT_total_present'].iloc[0]
        STAIT_total_absent = df_participant['STAIT_total_absent'].iloc[0]

        choice_options = randomized_choice_options(num_choices=2)

        prompt = "In this task, you have to repeatedly choose between two slot machines labeled " + choice_options[0] + " and " +  choice_options[1] + ".\n"\
         "You can choose a slot machine by pressing its corresponding key.\n"\
         "When you select one of the machines, you will win or lose points.\n"\
         "The machines will not always give you the same points when you select them again.\n"\
         "The machines' average points may either be stable or fluctuating over time.\nYou will be informed about this before every game.\n"\
         "Your goal is to choose the slot machines that will give you the most points.\n"\
         "You will receive feedback about the outcome after making a choice.\n"\
         "You will play 30 games in total, each with a different pair of slot machines.\nEach game will consist of 10 trials.\n\n"

        for task in range(1, num_tasks):
            df_task = df_participant[(df_participant['block'] == task)]
            condition = df_task.cond.iloc[0]

            prompt += 'Game ' + str(task) + ':\n'
            if condition == 1:
                prompt += "Machine's " + choice_options[0] + " average points are fluctuating. Machine's " + choice_options[1] + " average points are stable.\n"
            elif condition == 2:
                prompt += "Machine's " + choice_options[0] + " average points are stable. Machine's " + choice_options[1] + " average points are fluctuating.\n"
            elif condition == 3:
                prompt += "Machine's " + choice_options[0] + " average points are fluctuating. Machine's " + choice_options[1] + " average points are fluctuating.\n"
            elif condition == 4:
                prompt += "Machine's " + choice_options[0] + " average points are stable. Machine's " + choice_options[1] + " average points are stable.\n"

            for trial in range(1, num_trials):
                df_trial = df_task[(df_task['trial'] == trial)]
                c = df_trial.C.item()
                r = df_trial.reward.item()
                RTs.append(df_trial.rt.item())
                prompt += 'You press <<' + choice_options[c] + '>> and get ' + str(r) + ' points.\n'
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)
        #print(RTs)

        all_prompts.append({'text': prompt,
            'experiment': 'fan2022trait/' + dataset,
            'participant': str(participant),
            'RTs': RTs,
            'age': str(age),
            'STICSA-T somatic': str(STICSAT_total_Somatic),
            'STICSA-T cognitive': str(STICSAT_total_Cognitive),
            'STAI-T present': str(STAIT_total_present),
            'STAI-T absent': str(STAIT_total_absent),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
