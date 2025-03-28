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

datasets_path = "../../DataSharing_base/agency-master/"
all_prompts = []

expe_strings = ['Experiment1/passymetrieI_Suj{}.mat',
                'Experiment2/passymetrieII_Suj{}.mat',
                'Experiment3/Bias_{}.mat',
                'Experiment4/Datago_{}.mat']
subjects_per_expe = {1:range(1,25),2:range(1,25),3:range(1,30),
                     4:[1,2,3,4,5,8,9,10,11,12,13,14,15,16,17,18,19]}

for experiment in range(1,5):
    subjects = subjects_per_expe[experiment]#[k for k in range(1,subjects_per_expe[experiment-1])]
    for participant in subjects:
        dataset1 = spio.loadmat(datasets_path+expe_strings[experiment-1].format(participant))['M']
        df_participant = pd.DataFrame(data=dataset1)
        df_participant[7] = df_participant[7].astype(float)*1000 #from sec to ms
        RTs = []
        choice_options = randomized_choice_options(num_choices=8)
        if experiment <4:
            prompt = 'You have to repeatedly choose between two stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (1) or a punishment (-1), once it is selected. Your goal is to gather as many rewards as possible and avoid punishment.'
        
        if experiment == 1 or experiment == 3:
            prompt += '\nYou get feedback about the value of the chosen stimulus after each choice.\n'
        elif experiment==2:
            prompt+= '\nYou get feedback about the value of the chosen stimulus after each choice. On some trials, you will also see the outcome of the unchosen option, but you only receive points for the chosen option.\n'
        if experiment < 4:
            prompt+='\nOn some trials, you will only be able to select one of the options.\n'
        else:
            prompt = 'You have to repeatedly choose between two stimuli. You have to press a key to select the first option, and to not respond to select the second option.\nEach stimulus delivers a reward (1) or a punishment (-1), once it is selected. Your goal is to gather as many rewards as possible and avoid punishment.\nYou '
        # prompt += '\nYou are now in a learning phase.\n'
                
        for index, row in df_participant.iterrows():
            RTs.append(row[7].item())
            stims = [(row[1]-1)*2+1, row[1]*2] #wrong and right stimulus in one context
            
            choice_idx = int(row[5]) #0 worst, 1 best
            
            choice = choice_options[int(stims[choice_idx]-1)]
            
            available_options = ''
            # if (choice_idx == 0 and choice_cor==1) or (choice_idx == 1 and choice_cor==0):
            #     stims = [stims[1], stims[0]]
            stimulus0 = '' if math.isnan(stims[0]) else choice_options[int(stims[0])-1]
            stimulus1 = '' if math.isnan(stims[1]) else choice_options[int(stims[1])-1]
            
            # out = str(row[7]*2-1)
            outs = [row[4],row[3]]
            out = str(outs[choice_idx])
            cout = str(outs[1-choice_idx])
            if experiment == 1 or experiment == 3 or (experiment == 2 and (row[1]==1 or row[1]==3)):
                if row[6]==1:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '.\n'
                else:
                    prompt += 'You encounter stimuli ' +  ', '.join(stimulus0 + stimulus1) + '. You are focred to press ' + choice + '. You receive a reward of ' + out + '.\n'
            elif experiment == 2 and (row[1]==2 or row[1]==4):
                # cout = str(row[8]*2-1)
                # stimulus0_idx = '' if math.isnan(row.left_option.item()) else str(int(row.left_option))
                # stimulus1_idx = '' if math.isnan(row.right_option.item()) else str(int(row.right_option))
                unchosen_option1 = ''.join(stimulus0 + stimulus1).replace(str(choice), '')
                # unchosen_option1 = choice_options[int(unchosen_idx[0])]
                if row[6] == 1:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + out + '. You would have received ' + cout + ', had you pressed ' + str(unchosen_option1) + '.\n'
                else:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You are forced to press ' + choice + '. You receive a reward of ' + out + '. You would have received ' + cout + ', had you pressed ' + str(unchosen_option1) + '.\n'
            elif experiment == 4:
                go=int(row[6]) #-1 is a go trial, 1 is no go
                if go==-1:
                    action = 'You <<click>>'
                else:
                    action = 'You <<withhold response>>'
                if (go == 1 and choice_idx==0) or (go == -1 and choice_idx == 1):
                    [stimulus0, stimulus1]=[stimulus1, stimulus0]
                    stims = [row[1]*2, (row[1]-1)*2+1] #right and wrong stimulus in one pair 
                    
                    choice_idx = int(row[5]) #0 worst, 1 best
                    
                    choice = choice_options[int(stims[choice_idx]-1)]
                #     if choice_idx == 0:
                #         [stimulus0, stimulus1]=[stimulus1, stimulus0] #invert the order of stimuli  
                # else:
                #     action = 'You <<withhold response>>'
                #     if choice_idx == 1:
                #         [stimulus0, stimulus1]=[stimulus1, stimulus0] #invert the order of stimuli
                prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. '+action+', hence selecting <<'+choice+'>>. You receive a reward of '+out+'.\n'
                
        #%% Finalize prompt
        prompt = prompt[:-1]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'chambon2020feedback/'+str(experiment), 'participant': str(participant),'RTs':RTs})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)