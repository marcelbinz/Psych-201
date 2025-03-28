import numpy as np
import pandas as pd
import json
import jsonlines
def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

all_prompts = []

instructions = 'Dear participant,\nIn this experiment, we want to get to know your preferences.\nIn each trial, you will be shown two 50%-50% lotteries.\nEach lottery has two outcomes, each occurring with 50% chance (e.g., like flipping a coin).\nIn each trial, your task is to indicate which of the two lotteries you prefer (even if you dislike both lotteries, there should be one you find preferable).\nNote there are no right or wrong responses here. We simply want to get to know your preferences.\nYou will get a bonus payment that depends on the choices that you make.\nAt the end of the experiment, one of your choices will be selected at random and the decision that you made will be played out for the bonus payment.'
exp_settings = {1 : {'sorting' : ['participant', 'trial'], 'subject_col' : 'participant', 'replacement' : ['Left', 'Right'],  'option_values' : ['ul', 'dl', 'ur', 'dr'], 'RT' : ['okrt', 1000]},
                2 : {'sorting' : ['subject_id', 'session_no', 'trial_no'], 'subject_col' : 'subject_id', 'replacement' : ['X', 'Y'],  'option_values' : ['Xout1', 'Xout2', 'Yout1', 'Yout2'], 'RT' : ['RT', 1]},
                3 : {'sorting' : ['participant', 'Session', 'trial'], 'subject_col' : 'participant', 'replacement' : ['X', 'Y'],  'option_values' : ['Xout1', 'Xout2', 'Yout1', 'Yout2'], 'RT' : ['okrt', 1000]},}

for experiment in [1, 2, 3]:
    dataset = pd.read_csv(f'data/exp{experiment}.csv')
    dataset = dataset.sort_values(by=exp_settings[experiment]['sorting']).reset_index(drop=True)
    if experiment == 1:
        dataset['session_no'] = 2-(dataset['trial'] == dataset['trialWithinBlocks'])
        pass
    if experiment == 3:
        dataset['session_no'] = dataset['Session']
        dataset['choice'] = dataset['rsp']
        pass
    participants = dataset[exp_settings[experiment]['subject_col']].unique()
    for participant in participants:
        participant_data = dataset[dataset[exp_settings[experiment]['subject_col']] == participant].copy()
        choice_options = randomized_choice_options(num_choices=2)
        participant_data['choice'] = participant_data['choice'].replace({exp_settings[experiment]['replacement'][0] : choice_options[0], exp_settings[experiment]['replacement'][1] : choice_options[1]})
        prompt = instructions
        prompt += f"\nThe lotteries' names are {choice_options[0]} and {choice_options[1]}."
        prompt += 2*'\n'
        for block in np.sort(participant_data['session_no'].unique()):
            prompt += f'Session {block}:\n'
            block_data = participant_data[participant_data['session_no'] == block]
            for trial in block_data.index:
                trial_outcomes = block_data.loc[trial, exp_settings[experiment]['option_values']].values
                choice = block_data.loc[trial, 'choice']
                prompt += f'The outcomes of lottery {choice_options[0]} are {trial_outcomes[0]} with 50% chance and {trial_outcomes[1]} with 50% chance. The outcomes of lottery {choice_options[1]} are {trial_outcomes[2]} with 50% chance and {trial_outcomes[3]} with 50% chance. You choose <<{choice}>>.\n'
                pass
            prompt += '\n'
            pass
        prompt = prompt[:-2]
        all_prompts.append({'text': prompt, 'experiment': f'spektor2024lossaversion/exp{experiment}.csv', 'participant': int(participant), 'RTs' : [int(xxx) for xxx in (participant_data[exp_settings[experiment]['RT'][0]]*exp_settings[experiment]['RT'][1]).round().astype(int).values]})
        pass
    pass
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
    pass