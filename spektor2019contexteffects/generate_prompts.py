import numpy as np
import pandas as pd
import io
import json
import jsonlines
def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

all_prompts = []

columns_to_keep = ['subject', 'block_no', 'trial', 'choice', 'out0', 'out1', 'out2', 'RT']

datasets = {1 : pd.read_csv('data/exp1/dataset.csv', names=['subject', 'block_id', 'trial', 'RT', 'choice', 'out0', 'out1', 'out2', 'out_choice', 'total_reward', 'loc0', 'loc1', 'loc2', 'block_no']),
            2 : pd.read_csv('data/exp2/dataset.csv', names=['subject', 'block_id', 'trial', 'RT', 'choice', 'out0', 'out1', 'out2', 'out_choice', 'total_reward', 'block_no']),
            3 : pd.read_csv('data/exp3/dataset.csv', names=['subject', 'block_id', 'trial', 'RT', 'choice', 'out0', 'out1', 'out2', 'out_choice', 'total_reward', 'loc0', 'loc1', 'loc2', 'block_no']),
            '3r' : pd.read_csv('data/exp3r/dataset.csv', names=['subject', 'block_id', 'trial', 'RT', 'choice', 'out0', 'out1', 'out2', 'out_choice', 'total_reward', 'loc0', 'loc1', 'loc2', 'block_no']),
            4 : pd.read_csv('data/exp4/dataset.csv', names=['subject', 'block_id', 'trial', 'RT', 'choice', 'out0', 'out1', 'out2', 'out_choice', 'loc0', 'loc1', 'loc2'], usecols=np.arange(12)),
           }
datasets[4]['starting_block'] = datasets[4]['subject'] % 2
datasets[4]['block_no'] = (1*(datasets[4]['block_id'] != datasets[4]['starting_block']))+1

datasets_final = {}
colnames = ['subject', 'trial', 'out0', 'out1', 'choice', 'RT']
for iii in datasets.keys():
    temp_dataset = pd.read_csv(f'data/exp{iii}/dataset_training.csv', names=colnames, usecols=np.arange(len(colnames)))
    temp_dataset['out2'] = '-'
    temp_dataset['block_no'] = 0
    datasets_final[iii] = pd.concat([temp_dataset[columns_to_keep], datasets[iii][columns_to_keep]], axis=0).reset_index(drop=True).sort_values(by=['subject', 'block_no', 'trial'])
    datasets_final[iii]['block_no'] += 1
    pass

instructions = 'In the following, you will play three blocks of a decision-making task.\nEach block contains different options, and in each round, you will choose between these options.\nYour task is to select the option that appeals to you the most each time.\nAfterward, you will receive feedback on how much each displayed option was worth in that round.\nYour goal is to maximize the points you gain over the course of the experiment.\nBetween blocks, you will have the opportunity to take short breaks.'

for experiment in [1, 2, 3, '3r', 4]:
    data = datasets_final[experiment]
    participants = np.sort(data['subject'].unique())
    for participant in participants:
        participant_data = data[data['subject'] == participant]
        choice_options = randomized_choice_options(num_choices=3)
        prompt = instructions
        option_label = 'Option'
        prompt += f"\nThe {option_label.lower()}s' names are {choice_options[0]}, {choice_options[1]}, and {choice_options[2]}."
        prompt += 2*'\n'
        exp_blocks = np.sort(participant_data['block_no'].unique())
        for exp_block_no in exp_blocks:
            prompt += f'Block {exp_block_no}:\n'
            exp_block_data = participant_data[participant_data['block_no'] == exp_block_no].sort_values(by='trial').copy()
            exp_block_data['choice'] = exp_block_data['choice'].replace(dict(zip([0, 1, 2], choice_options)))
            if len(exp_block_data['out2'].unique()) != 1:
                prompt += f'There are three {option_label.lower()}s to choose from, {choice_options[0]}, {choice_options[1]}, and {choice_options[2]}.\n'
                three_opts = True
                pass
            else:
                prompt += f'There are two {option_label.lower()}s to choose from, {choice_options[0]} and {choice_options[1]}.\n'
                three_opts = False
                pass
            prompt += '\n'.join([f'You choose <<{exp_block_data.loc[iii, 'choice']}>>. {option_label} {choice_options[0]} yields {exp_block_data.loc[iii, 'out0']} points. {option_label} {choice_options[1]} yields {exp_block_data.loc[iii, 'out1']} points.' + (f' {option_label} {choice_options[2]} yields {exp_block_data.loc[iii, 'out2']} points.' if three_opts else '') for iii in exp_block_data.index])                
            prompt += '\n\n'                
            pass
        prompt = prompt[:-2]
        #print(prompt, 10*'\n')
        all_prompts.append({'text': prompt, 'experiment': f'spektor2019contexteffects/exp{experiment}.csv', 'participant': int(participant)})
        pass
    pass
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
    pass