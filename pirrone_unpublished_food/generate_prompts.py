import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["data_Pirrone_food_Psych-201.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    
    num_participants = df.participant.max() + 1
    num_tasks = 1
    num_trials = df.step.max() + 1
    df['time'] = (df['time'] / 1000).round(3)

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]

        choice_options = randomized_choice_options(num_choices=2)

        num_features = 2
        num_features_str = 'two'

        prompts = [
            'You will choose from two items to consume, each has a different value from ratings that you previously assigned to the items individually.\n'
        ]

        for task in range(num_tasks):
            df_task = df_participant
            prompt = prompts[task]

            for trial in range(num_trials):
                df_trial = df_task[(df_task['step'] == trial)]
                c = df_trial.choice.item() if not df_trial.empty else None
                t = df_trial.target.item() if not df_trial.empty else None
                x0 = df_trial.x0.item() if not df_trial.empty else None
                x1 = df_trial.x1.item() if not df_trial.empty else None
                rt = df_trial.time.item() if not df_trial.empty else None
                x = [df_trial.x0.item() if not df_trial.empty else None, df_trial.x1.item() if not df_trial.empty else None]

                feature_information = ''
                feature_information += 'Press ' + str(choice_options[0]) + ' to select option with value ' + str(x0) + ' or press ' + str(choice_options[1]) + ' to select option with value ' + str(x1)

                line = f"{feature_information}. You press <<{str(choice_options[c])}>> in {str(rt)} seconds.\n"
                
						
                if 'None' not in line:
                    prompt += line
            prompt += '\n'

        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'pirrone_unpublished_food/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
