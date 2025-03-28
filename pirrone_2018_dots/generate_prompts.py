import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["data_Pirrone2018_dots_Psych-201.csv"]
all_prompts = []

prompts = [
    'You will be presented with two arrays of dots.\n'
    'In this task, you need to decide which dots you want to collect by pressing the corresponding key.\n'
    'You will gain 1 CNY every 1000 dots you collect. There is no right or wrong response.\n\n',

    'You will be presented with two arrays of dots.\n'
    'In this task, you have to indicate the array with more dots by pressing the corresponding key.\n'
    'You will gain .08 CNY for a correct response, 0 CNY for a wrong response.\n\n',

    'You will be presented with two arrays of dots.\n'
    'In this task, you have to indicate the array with more dots by pressing the corresponding key.\n'
    'You will gain .04 CNY for a correct response, 0 CNY for a wrong response.\n\n'
]

for dataset in datasets:
    df = pd.read_csv(dataset)

    # Remove rows where x0 == x1 for accuracy-based task
    #df = df[~((df['task'] > 0) & (df['x0'] == df['x1']))]

    num_participants = df.participant.max() + 1
    num_tasks = df.task.max() + 1
    num_trials = df.step.max() + 1
    df['time'] = (df['time'] / 1000).round(3)

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]

        choice_options = randomized_choice_options(num_choices=2)

        participant_prompt = []

        for task in range(num_tasks):
            df_task = df_participant[(df_participant['task'] == task)]

            task_prompt = prompts[task] + f'Task {task + 1}:\n'

            for trial in range(num_trials):
                df_trial = df_task[(df_task['step'] == trial)]
                c = df_trial.choice.item() if not df_trial.empty else None
                t = df_trial.target.item() if not df_trial.empty else None
                x0 = df_trial.x0.item() if not df_trial.empty else None
                x1 = df_trial.x1.item() if not df_trial.empty else None
                rt = df_trial.time.item() if not df_trial.empty else None

                feature_information = (f'Options have {str(x0)} dots and {str(x1)} dots. '
                                       f'Press {str(choice_options[0])} for {str(x0)} dots and '
                                       f'{str(choice_options[1])} for {str(x1)} dots.')

                collected_dots = x0 if c == 0 else x1

                if task != 0:
                    line = (f"{feature_information} You press <<{str(choice_options[c])}>> in {str(rt)} seconds, "
                            f"the correct response was {str(choice_options[t])}.\n")
                else:
                    line = (f"{feature_information} You press <<{str(choice_options[c])}>> in {str(rt)} seconds, "
                            f"and you collect {str(collected_dots)} dots.\n")

                if 'None' not in line:
                    task_prompt += line

            task_prompt += '\n'

            participant_prompt.append(task_prompt)

        full_prompt = ''.join(participant_prompt)

        print(full_prompt)
        all_prompts.append({
            'text': full_prompt,
            'experiment': 'pirrone_2018_dots/' + dataset,
            'participant': participant
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
