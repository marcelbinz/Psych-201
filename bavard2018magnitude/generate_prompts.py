# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:29:54 2025
magnitude experiments to natural language
@author: IsabHox
"""

import math
import numpy as np
import pandas as pd
import jsonlines
import json
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["../../Magnitude_Data_expe1.csv","../../Magnitude_Data_expe2.csv"]
all_prompts = []


for d in range(len(datasets)):
    dataset = datasets[d]
    df = pd.read_csv(dataset)
    df.Stimuli = [[int(x[0]), int(x[1])] for x in df.Stimuli.str.split(';')]
    df.Outcomes = [[float(x[0]), float(x[1])] for x in df.Outcomes.str.split(';')]


    for participant in df.Agent.unique():
        df_participant = df[(df['Agent'] == participant)]
        choice_options = randomized_choice_options(num_choices=8)
        prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (0, 0.1€ or 1€), or a punishment (-0.1€ or -1€) once it is selected. Your goal is to gather as many rewards and avoid loss as much as possible.'
        
        
            
        for phase in range(2):
            df_phase = df_participant[(df_participant['IsTransfer'] == phase)]

            # feedback = feedbacks[np.unique(df_phase.Experiment)[0]%4-1][phase_ix]
            if phase == 0:
                if d == 2:
                    prompt += '\nYou get feedback about the values of the chosen stimulus after each choice. On some trials, you will additionally receive information about the outcome of the other option\n'
                elif d==1 :
                    prompt += '\nYou get feedback about the value of the chosen stimulus after each choice.\n'

                prompt += '\nYou are now in a learning phase.\n'
           
            elif phase == 1:
                prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
                    
            for index, row in df_phase.iterrows():
                
                available_options = ''
                stimulus0 = '' if math.isnan(row.Stimuli[0]) else choice_options[int(row.Stimuli[0])-1]
                stimulus1 = '' if math.isnan(row.Stimuli[1]) else choice_options[int(row.Stimuli[1])-1]


                choice =choice_options[int(row.Choice)-1]

                choice_idx = row.Stimuli.index(row.Choice)
                
                
                feedback = np.count_nonzero(np.isnan(row.Outcomes))

                if feedback == 0:
                    # stimulus0_idx = '' if math.isnan(row.left_option.item()) else str(int(row.left_option))
                    # stimulus1_idx = '' if math.isnan(row.right_option.item()) else str(int(row.right_option))
                    unchosen_option1 = ''.join(stimulus0 + stimulus1).replace(str(choice), '')
                    out = str(float(row.Outcomes[choice_idx]))
                    cout= str(float(row.Outcomes[1-choice_idx]))
                    # unchosen_option1 = choice_options[int(unchosen_idx[0])]
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '. You would have received ' + cout + ', had you pressed ' + str(unchosen_option1) + '.\n'
                elif feedback == 1:
                    out = str(float(row.Outcomes[choice_idx]))
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '.\n'
                else:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>.\n'

        prompt = prompt[:-1]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'bavard2018magnitude/' + json.dumps(f'Experiment{d}'), 'participant': str(participant)})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)