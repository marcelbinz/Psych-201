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
import scipy.io as spio

datasets_path = "../../DataSharing_base/Online Scripts/data/"
all_prompts = []

expe1 = [k for k in range(1,21)]
expe2 = [k for k in range(21,41)]

subjects = np.concatenate([expe1,expe2])

for participant in subjects:
    dataset1 = spio.loadmat(datasets_path+f'Test{participant}_Session1.mat')['data']
    dataset2 = spio.loadmat(datasets_path+f'Test{participant}_Session2.mat')['data']
    df_participant = pd.DataFrame(data=np.concatenate([dataset1, dataset2]))
    # rts = df_participant[6].astype(float)
    rts = []
    df_participant[7][df_participant[7]==0]=-1 #negative outcomes have value -1
    
    # df.Stimuli = [[int(x[0]), int(x[1])] for x in df.Stimuli.str.split(';')]
    # df.Outcomes = [[float(x[0]), float(x[1])] for x in df.Outcomes.str.split(';')]

    choice_options = randomized_choice_options(num_choices=8)
    prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (1) or a punishment (-1), once it is selected. Your goal is to gather as many rewards as possible and avoid punishment.'
    if participant in expe1:
        prompt += '\nYou get feedback about the value of the chosen stimulus after each choice.\n'
    else:
        prompt+= '\nYou get feedback about both the value of the chosen stimulus and the alternative after each choice, but you only receive points for the chosen option.\n'
    # prompt += '\nYou are now in a learning phase.\n'
            
    for index, row in df_participant.iterrows():
        rts.append(row[6].item())
        if not (row[3]==4 and row[2]>12):
            stims = [(row[3]-1)*2+1, row[3]*2] #wrong and right stimulus in one context
        else:
            stims = [row[3]*2,(row[3]-1)*2+1] #after a reversal, wrong and right options are inverted
        
        choice_idx = row[4]/2+0.5 #0 left, 1 right
        choice_cor = row[5]
        
        choice = choice_options[stims[choice_cor]-1]
        
        available_options = ''
        if (choice_idx == 0 and choice_cor==1) or (choice_idx == 1 and choice_cor==0):
            stims = [stims[1], stims[0]]
        stimulus0 = '' if math.isnan(stims[0]) else choice_options[int(stims[0])-1]
        stimulus1 = '' if math.isnan(stims[1]) else choice_options[int(stims[1])-1]
        
        out = str(row[7]*2-1)
        if participant in expe1:
            prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '.\n'
        else:
            cout = str(row[8]*2-1)
            # stimulus0_idx = '' if math.isnan(row.left_option.item()) else str(int(row.left_option))
            # stimulus1_idx = '' if math.isnan(row.right_option.item()) else str(int(row.right_option))
            unchosen_option1 = ''.join(stimulus0 + stimulus1).replace(str(choice), '')
            # unchosen_option1 = choice_options[int(unchosen_idx[0])]
            prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '. You would have received ' + cout + ', had you pressed ' + str(unchosen_option1) + '.\n'
       

    #%% Finalize prompt
    prompt = prompt[:-1]
    print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'palminteri2017confirmation', 'participant': str(participant),'RTs':rts})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)