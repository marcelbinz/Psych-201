import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["data_Marshall2022_birghtness_Psych-201.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    

    num_participants = df.participant.max() + 1
    num_tasks = 1
    num_trials = df.step.max() + 1
    df['time'] = (df['time'] / 1000).round(3)

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]

        choice_options = randomized_choice_options(num_choices=3)

        prompt = 'You will be presented with three stimuli of different brightness, brightness varies from 0 (lowest brightness) to 1 (maximum brightness).\n'\
        'You need to decide which stimulus is the brightest by pressing the corresponding key.\n'\
        'Try to be as fast and accurate as possible.\n\n'

        for task in range(num_tasks):
            df_task = df_participant

            for trial in range(num_trials):
                df_trial = df_task[(df_task['step'] == trial)]
                c = df_trial.choice.item() if not df_trial.empty else None
                x0 = df_trial.x0.item() if not df_trial.empty else None
                x1 = df_trial.x1.item() if not df_trial.empty else None
                x2 = df_trial.x2.item() if not df_trial.empty else None
                rt = df_trial.time.item() if not df_trial.empty else None         
                x = [df_trial.x0.item() if not df_trial.empty else None, df_trial.x1.item() if not df_trial.empty else None]

                feature_information = ''
                feature_information += 'If you think that the option with a brightness value of ' + str(x0) + ' is the brightest press ' + str(choice_options[0]) + '. If you think that the option with brightness value of ' + str(x1) + ' is the brightest press ' + str(choice_options[1]) + '. If you think that the option with brightness value of ' + str(x2) + ' is the brightest press ' + str(choice_options[2]) 

                line = f"{feature_information}. You press <<{str(choice_options[c])}>> in {str(rt)} seconds.\n"
						
                if 'None' not in line:
                    prompt += line
            prompt += '\n'

        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'marshall_2022_brightness/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
