import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["march2020", "april2020", "june2020", "nov2020"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv('data/' + dataset + '_covid_problems.csv')
    df_survey = pd.read_csv('data/' + dataset + '_covid_survey.csv')
    print(df)

    for participant in df['sid'].unique():

        df_participant = df[(df['sid'] == participant)]
        df_survey_participant = df_survey[(df_survey['sid'] == participant)]

        assert len(df_survey_participant) == 1

        age = df_survey_participant.age.iloc[0]
        gender = df_survey_participant.gender.iloc[0]
        education = df_survey_participant.education.iloc[0]
        stress_health = df_survey_participant.stress_health.iloc[0]
        stress_finance = df_survey_participant.stress_finance.iloc[0]

        choice_options = randomized_choice_options(num_choices=2)

        prompt = "In this task, you have to repeatedly choose between two options labeled " + choice_options[0] + " and " +  choice_options[1] + ".\n"\
         "You can choose an option by pressing its corresponding key.\n"\
         "Each option would hypothetically lead to you earning a specified amount of money in a specified amount of time.\n\n"
        for index, row in df_participant.iterrows():
            c = int(row['right_picked'])
            left_val = round(row['left_val'], 2)
            right_val = round(row['right_val'], 2)
            left_time = round(row['left_time'], 2)
            right_time = round(row['right_time'], 2)
            absolute_value_diff = round(row['absolute_value_diff'], 2)
            condition = row['condition']
            if condition == 0:
                if left_time < right_time:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(left_val) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(left_val) + ' dollars plus ' + str(absolute_value_diff) + ' dollars in ' + str(right_time) + ' days.\n'
                else:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(right_val) + ' dollars plus ' + str(absolute_value_diff) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(right_val) + ' dollars in ' + str(right_time) + ' days.\n'

            elif condition == 1:
                relative_value_diff = round((row['relative_value_diff'] - 1) * 100, 2)
                if left_time < right_time:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(left_val) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(left_val) + ' dollars plus ' + str(relative_value_diff) + '% in ' + str(right_time) + ' days.\n'
                else:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(right_val) + ' dollars plus ' + str(relative_value_diff) + '% in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(right_val) + ' dollars in ' + str(right_time) + ' days.\n'

            elif condition == 2:
                prompt += 'Option ' +  choice_options[0] + ': ' + str(left_val) + ' dollars in ' + str(left_time) + ' days.\n'
                prompt += 'Option ' +  choice_options[1] + ': ' + str(right_val) + ' dollars in ' + str(right_time) + ' days.\n'

            elif condition == 3:
                if left_time < right_time:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(right_val) + ' dollars minus ' + str(absolute_value_diff) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(right_val) + ' dollars in ' + str(right_time) + ' days.\n'
                else:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(left_val) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(left_val) + ' dollars minus ' + str(absolute_value_diff) + ' dollars in ' + str(right_time) + ' days.\n'

            elif condition == 4:
                relative_value_diff = round((1 - (1 / row['relative_value_diff'])) * 100, 2)
                if left_time < right_time:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(right_val) + ' dollars minus ' + str(relative_value_diff) + '% in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(right_val) + ' dollars in ' + str(right_time) + ' days.\n'
                else:
                    prompt += 'Option ' +  choice_options[0] + ': ' + str(left_val) + ' dollars in ' + str(left_time) + ' days.\n'
                    prompt += 'Option ' +  choice_options[1] + ': ' + str(left_val) + ' dollars minus ' + str(relative_value_diff) + '% in ' + str(right_time) + ' days.\n'
            else:
                assert False

            prompt += 'You press <<' + choice_options[c] + '>>.\n'
            prompt += '\n'

        prompt = prompt[:-2]

        print(prompt)


        all_prompts.append({'text': prompt,
            'experiment': 'agrawal2024stress/' + dataset + '_covid_problems.csv',
            'participant': str(participant),
            'age': str(age),
            'gender': str(gender),
            'education': str(education),
            'stress_health': str(stress_health),
            'stress_finance': str(stress_finance),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
