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

datasets = ["../../WEIRD__CDep_NoExclusions.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    df.ChoseLorR = df.ChoseLorR/2 + 0.5 #renormalize between 0 and 1
    df.ResponseTime = df.ResponseTime.astype(float)
    for participant in df.ParticipantID.unique():
        df_participant = df[(df['ParticipantID'] == participant)]
        choice_options = randomized_choice_options(num_choices=10)
        RTs = []
        for phase in range(4):
            df_phase = df_participant[(df_participant['WhichPhase'] == phase)]
            if phase==0:
                prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward (0, 1 or 10) once it is selected.\nYou get feedback about the values of all encountered stimuli after each choice.\n'
            if phase == 0:
                prompt += '\nYou are now in a training phase that familiarizes you with the response modalities:\n'
            if phase == 1:
                prompt += '\nYou are now in a learning phase:\n'
            if phase == 2:
                prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'
            if phase == 3:
                prompt += 'Now, you will be shown the possible reward of each option alongside its probability.\nYou get feedback about the value of all encountered stimuli after each choice.\n'

            for index, row in df_phase.iterrows():
                RTs.append(row['ResponseTime'])
                available_options = ''
                stimulus0 = '' if math.isnan(row.SymbolLeft) else choice_options[int(row.SymbolLeft)]
                stimulus1 = '' if math.isnan(row.SymbolRight) else choice_options[int(row.SymbolRight)]

                if int(row.ChoseLorR) == 0:
                    choice_idx = int(row.SymbolLeft)
                    reward = row.RewardGoodorBad * row.Magnitude1
                    unchosen_reward = row.OtherRewardGoodorBad * row.Magnitude2
                if int(row.ChoseLorR) == 1:
                    choice_idx = int(row.SymbolRight)
                    reward = row.RewardGoodorBad * row.Magnitude2
                    unchosen_reward = row.OtherRewardGoodorBad * row.Magnitude1
                    
                choice = choice_options[choice_idx]

                if phase < 2:
                    stimulus0_idx = '' if math.isnan(row.SymbolLeft) else str(int(row.SymbolLeft))
                    stimulus1_idx = '' if math.isnan(row.SymbolRight) else str(int(row.SymbolRight))
                    unchosen_idx = ''.join(stimulus0_idx + stimulus1_idx).replace(str(choice_idx), '')
                    unchosen_option1 = choice_options[int(unchosen_idx[0])]
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>. You receive a reward of ' + str(reward) + '. You would have received ' + str(unchosen_reward) + ', had you pressed ' + str(unchosen_option1) + '.\n'
                elif phase==2:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1) + '. You press <<' + choice + '>>.\n'
                else:
                    try:
                        [proba0, mag0] = row.Option1.strip('[]').split(',')
                        [proba1, mag1] = row.Option2.strip('[]').split(',')
                        stimulus0_idx = '' if math.isnan(row.SymbolLeft) else str(int(row.SymbolLeft))
                        stimulus1_idx = '' if math.isnan(row.SymbolRight) else str(int(row.SymbolRight))
                        unchosen_idx = ''.join(stimulus0_idx + stimulus1_idx).replace(str(choice_idx), '')
                        unchosen_option1 = choice_options[int(unchosen_idx[0])]
                        prompt += f'You can choose between option {stimulus0} which gives a reward of {mag0} with probability {proba0}, and option {stimulus1} which gives a reward of {mag1} with probability {proba1}. You press <<' + choice + '>>. You receive a reward of ' + str(reward) + '. You would have received ' + str(unchosen_reward) + ', had you pressed ' + str(unchosen_option1) + '.\n'
                    except:
                        if int(row.ChoseLorR) == 0:
                            choice = 'left'
                            unchosen_option1='right'
                        else:
                            choice = 'right'
                            unchosen_option1='left'
                        prompt += f'You can choose between the left option which gives a reward of {mag0} with probability {proba0}, and the right option which gives a reward of {mag1} with probability {proba1}. You press <<' + choice + '>>. You receive a reward of ' + str(reward) + '. You would have received ' + str(unchosen_reward) + ', had you pressed ' + str(unchosen_option1) + '.\n'
        prompt = prompt[:-1]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'anllo2024weird', 'participant': str(participant), 'RTs': RTs, 'nationality':row.Country, 'age':str(row.Age)})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
