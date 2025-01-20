import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options
import rdata

parsed_mturk = rdata.parser.parse_file('/Users/milena.rmus/Desktop/Haines_2020_CPS/Data/Preprocessed/1_preprocessed_DDT_trait_descriptive_MTURK.rds')
parsed_rep = rdata.parser.parse_file('/Users/milena.rmus/Desktop/Haines_2020_CPS/Data/Preprocessed/1_preprocessed_DDT_trait_descriptive_REP.rds')
parsed_tal = rdata.parser.parse_file('/Users/milena.rmus/Desktop/Haines_2020_CPS/Data/Preprocessed/1_preprocessed_DDT_trait_descriptive_TAL.rds')

converted_mturk = rdata.conversion.convert(parsed_mturk)['survey_dat']
converted_rep = rdata.conversion.convert(parsed_rep)['survey_dat']
converted_tal = rdata.conversion.convert(parsed_tal)['survey_dat']

datasets = ["/Users/milena.rmus/Desktop/haines_dataset.csv"] # TODO EXPERIMENT 2
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)

    num_tasks = len(df.session.unique())

    for participant in df['sub'].unique():


        df_participant = df[(df['sub'] == participant)].reset_index(drop=True)


        if df_participant.sample_type[0] == 'TAL':
            stats = converted_tal
        elif df_participant.sample_type[0] == 'REP':
            stats = converted_rep
        else:
            stats = converted_mturk


        print([participant,df_participant.sample_type[0]])
        if participant == 'A2UC2ETY':
            print('stop')

        if stats[stats.ID == participant].reset_index().shape[0] == 0:
            age = 'N/A'
            stai = 'N/A'
            bis = 'N/A'
            AUDIT = 'N/A'
            DAST = 'N/A'
        else:

            age = stats[stats.ID == participant].reset_index().age[0]
            stai = stats[stats.ID == participant].reset_index().stai_s[0]
            bis = stats[stats.ID == participant].reset_index().bis_noplan[0]
            AUDIT = stats[stats.ID == participant].reset_index().AUDIT[0]
            DAST = stats[stats.ID == participant].reset_index().DAST[0]
        choice_options = randomized_choice_options(num_choices=2)

        # prompt = "Insert"
        prompt = "In this task, you have to repeatedly choose between two options labeled " + choice_options[0] + " and " +  choice_options[1] + ".\n"\
         "You can choose an option by pressing its corresponding key.\n"\
         "Each option will show you the amount of money you can get from it, and the amount of time you would need to wait to receive that money.\n" \
         f"You will play {num_tasks} sessions in total, each with a different pair of options.\n\n"

        # "The average amount of money associated with each option may either be stable or fluctuating over time.\nYou will be informed about this before every session.\n"\



        for task in range(num_tasks):
            df_task = df_participant[(df_participant['session'] == f'session{task+1}')].reset_index(drop=True)
            num_trials = df_task.trialNum.max() + 1

            prompt += 'Session ' + str(task+1) + ':\n'
            for trial in range(num_trials):
                df_trial = df_task[(df_task['trialNum'] == trial)].reset_index(drop=True)

                left_value = df_trial.leftValue[0]
                left_time = df_trial.leftTime[0]

                right_value = df_trial.rightValue[0]
                right_time = df_trial.rightTime[0]

                choice = df_trial.choice[0]

                prompt += f'Choice option {choice_options[0]} value is: {left_value} dollars. You can receive it in {left_time} days. Choice option {choice_options[1]} value is {right_value} dollars. You can receive it in {right_time} days. You press <<{choice_options[choice]}>>.\n'
            prompt += '\n'

        # prompt = prompt[:-2]
        # print(prompt)

        all_prompts.append({'text': prompt,
            'experiment': 'haines2020/intertemporal_choice',
            'participant': participant,
            'age': str(age),
            'STAI': str(stai),
            'BIS': str(bis),
            'AUDIT': str(AUDIT),
            'DAST': str(DAST),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)