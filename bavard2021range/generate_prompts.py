# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:19:05 2025
range dataset to natural language
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

datasets = ["../../range.csv"]
all_prompts = []
keys=['participant','phase','trial','context','left_option','right_option',
      'choice','accuracy','outcome','coutcome','rt','cumulated',
      'agent','experiment','order']
feedbacks = [['partial','no'],
             ['partial','partial'],
             ['complete','no'],
             ['complete','complete']]
context_values = [10,10,1,1]

for dataset in datasets:
    df = pd.read_csv(dataset,names=keys)
    df.choice = df.choice/2+0.5
    #clean dataset out of misrecorded trials
    df=df.dropna(subset=['right_option','left_option'])

    for participant in df.participant.unique():
        df_participant = df[(df['participant'] == participant)]
        choice_options = randomized_choice_options(num_choices=9)
        prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (0, 1 or 10) once it is selected.'
        RTs = []
        
            
        for phase in range(3):
            df_phase = df_participant[(df_participant['phase'] == phase)]
            if phase == 0:
                phase_ix = 0
            else:
                phase_ix = phase-1
            feedback = feedbacks[np.unique(df_phase.experiment)[0]%4-1][phase_ix]
            if phase == 0:
                if feedback == 'complete':
                    prompt += '\nYou get feedback about the values of all encountered stimuli after each choice.\n'
                elif feedback == 'partial':
                    prompt += '\nYou get feedback about the value of the chosen stimulus after each choice.\n'
                else:
                    prompt += '\nNo feedback is provided. \n'
                prompt += '\nYou are now in a training phase that familiarizes you with the response modalities:\n'
           
            if phase == 1:
                prompt += '\nYou are now in a learning phase:\n'
            if phase == 2:
                if feedback == 'complete':
                    prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before.You get feedback about the values of all encountered stimuli after each choice. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
                if feedback == 'partial':
                    prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before.You get feedback about the value of the chosen stimulus after each choice. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
                else:
                    prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
                    
            for index, row in df_phase.iterrows():
                RTs.append(row.rt.item())
                available_options = ''
                stimulus0 = '' if math.isnan(row.left_option.item()) else choice_options[int(row.left_option)]
                stimulus1 = '' if math.isnan(row.right_option.item()) else choice_options[int(row.right_option)]

                if row.choice.item() == 0:
                    choice_idx = int(row.left_option)
                if row.choice.item() == 1:
                    choice_idx = int(row.right_option)
                choice = choice_options[choice_idx]
                
                if row.context.item()<5:
                    out = str(int(row.outcome.item()*context_values[int(row.context.item()-1)]))
                    cout= str(int(row.coutcome.item()*context_values[int(row.context.item()-1)]))
                else:
                    out = str(int(row.outcome.item()*(10*(row.accuracy.item()==1)+row.accuracy.item()==0)))
                    cout= str(int(row.outcome.item()*(10*(row.accuracy.item()==0)+row.accuracy.item()==1)))

                if feedback == 'complete':
                    stimulus0_idx = '' if math.isnan(row.left_option.item()) else str(int(row.left_option))
                    stimulus1_idx = '' if math.isnan(row.right_option.item()) else str(int(row.right_option))
                    unchosen_idx = ''.join(stimulus0_idx + stimulus1_idx).replace(str(choice_idx), '')
                    unchosen_option1 = choice_options[int(unchosen_idx[0])]
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '. You would have received ' + cout + ', had you pressed ' + str(unchosen_option1) + '.\n'
                elif feedback == 'partial':
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '.\n'
                else:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>.\n'

        prompt = prompt[:-1]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'bavard2021range/' + json.dumps(float(df_participant.experiment.iloc[0])), 'participant': str(participant), 'RTs':RTs})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)