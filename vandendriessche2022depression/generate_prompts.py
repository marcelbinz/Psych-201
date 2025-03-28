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

datasets_path = "../../DataSharing_base/"
all_prompts = []

controls = [2, 3, 4, 24, 26, 28, 30, 31, 36, 38, 39, 41, 42, 43, 44, 45, 46,
            47, 48, 49, 50, 51, 52, 53, 54, 55]
patients = [6, 7, 8, 9, 10, 11, 14, 15, 16, 18, 20, 33, 34, 35, 37, 40, 60, 61,
            63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 75]

subjects = np.concatenate([controls, patients])

for participant in subjects:
    dataset1 = pd.read_csv(datasets_path+f'Test{participant}_Session1.csv', header=None)
    dataset2 = pd.read_csv(datasets_path+f'Test{participant}_Session2.csv', header=None)
    df_participant = pd.concat([dataset1, dataset2])
    df_participant[6] = df_participant[6].astype(float)
    df_participant[7][df_participant[7]==0]=-1 #negative outcomes have value -1
    RTs = []
    # df.Stimuli = [[int(x[0]), int(x[1])] for x in df.Stimuli.str.split(';')]
    # df.Outcomes = [[float(x[0]), float(x[1])] for x in df.Outcomes.str.split(';')]

    choice_options = randomized_choice_options(num_choices=8)
    prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (1) or a punishment (-1), once it is selected. Your goal is to gather as many rewards as possible.'
    prompt += '\nYou get feedback about the value of the chosen stimulus after each choice.\n'
    prompt += '\nYou are now in a learning phase.\n'
       
        # elif phase == 1:
        #     prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
                
    for index, row in df_participant.iterrows():
        RTs.append(row[6].item())
        stims = [int((row[3]-1)*2+1), int(row[3]*2)] #wrong and right stimulus in one context
        choice_idx = row[4]/2+0.5 #0 left, 1 right
        choice_cor = int(row[5])
        
        choice = choice_options[stims[choice_cor]-1]
        
        available_options = ''
        if (choice_idx == 0 and choice_cor==1) or (choice_idx == 1 and choice_cor==0):
            stims = [stims[1], stims[0]]
        stimulus0 = '' if math.isnan(stims[0]) else choice_options[int(stims[0])-1]
        stimulus1 = '' if math.isnan(stims[1]) else choice_options[int(stims[1])-1]
        
        out = str(row[7])
        prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '.\n'

        # print(out)
    #%% Then add the transfer phase
    prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
    
    df_participant = pd.read_csv(datasets_path+f'PostTraining{participant}.csv', header=None)
    
    for index, row in df_participant.iterrows():
        RTs.append(row[6].item())
        stimulus0 = '' if math.isnan(row[2]) else choice_options[int(row[2])-1]
        stimulus1 = '' if math.isnan(row[3]) else choice_options[int(row[3])-1]
        choice_idx = int(row[5]/2+0.5)
        stims = [stimulus0,stimulus1]
        choice = stims[choice_idx]
        prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>.\n'

    #%% Finalize prompt
    prompt = prompt[:-1]
    print(prompt)
    if participant in patients:
        all_prompts.append({'text': prompt, 'experiment': 'vandendriessche2022depression', 'participant': str(participant),'RTs':RTs, 'diagnosis':'depression'})
    else:
        all_prompts.append({'text': prompt, 'experiment': 'vandendriessche2022depression', 'participant': str(participant),'RTs':RTs})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)