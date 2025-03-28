import math
import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["exp1.csv", "exp2.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)

    for participant in df.participant.unique():
        df_participant = df[(df['participant'] == participant)]
        choice_options = randomized_choice_options(num_choices=10)
        prompt = 'You have to repeatedly choose between multiple stimuli by pressing their corresponding key.\nEach stimulus delivers a reward between 0 and 100 once it is selected.\nYou get feedback about the values of all encountered stimuli after each choice.\n'

        for phase in range(3):
            df_phase = df_participant[(df_participant['phase'] == phase)]

            if phase == 0:
                prompt += '\nYou are now in a training phase that familiarizes you with the response modalities:\n'
            if phase == 1:
                prompt += '\nYou are now in a learning phase:\n'
            if phase == 2:
                prompt += '\nYou are now in a transfer phase where you are presented with pairs of stimuli taken from the learning phase. Not all pairs would have been necessarily displayed together before. No more feedback is provided. Please indicate which of the stimuli was the one with the highest value by pressing the corresponding key:\n'

            for index, row in df_phase.iterrows():
                available_options = ''
                stimulus0 = '' if math.isnan(row.left_option.item()) else choice_options[int(row.left_option)]
                stimulus1 = '' if math.isnan(row.middle_option.item()) else choice_options[int(row.middle_option)]
                stimulus2 = '' if math.isnan(row.right_option.item()) else choice_options[int(row.right_option)]

                if row.choice.item() == 0:
                    choice_idx = int(row.left_option)
                if row.choice.item() == 1:
                    choice_idx = int(row.middle_option)
                if row.choice.item() == 2:
                    choice_idx = int(row.right_option)
                choice = choice_options[choice_idx]

                if phase < 2:
                    stimulus0_idx = '' if math.isnan(row.left_option.item()) else str(int(row.left_option))
                    stimulus1_idx = '' if math.isnan(row.middle_option.item()) else str(int(row.middle_option))
                    stimulus2_idx = '' if math.isnan(row.right_option.item()) else str(int(row.right_option))
                    unchosen_idx = ''.join(stimulus0_idx + stimulus1_idx + stimulus2_idx).replace(str(choice_idx), '')
                    if len(unchosen_idx) == 1:
                        unchosen_option1 = choice_options[int(unchosen_idx[0])]
                        unchosen_reward1 = row.reward_unchosen_1.item()
                        prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1 + stimulus2) + '. You press <<' + choice + '>>. You receive a reward of ' + str(row.reward.item()) + '. You would have received ' + str(unchosen_reward1) + ', had you pressed ' + str(unchosen_option1) + '.\n'
                    else:
                        unchosen_option1 = choice_options[int(unchosen_idx[0])]
                        unchosen_reward1 = row.reward_unchosen_1.item() if int(unchosen_idx[0]) < int(unchosen_idx[1]) else row.reward_unchosen_2.item()
                        unchosen_option2 = choice_options[int(unchosen_idx[1])]
                        unchosen_reward2 = row.reward_unchosen_2.item() if int(unchosen_idx[0]) < int(unchosen_idx[1]) else row.reward_unchosen_1.item()
                        prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1 + stimulus2) + '. You press <<' + choice + '>>. You receive a reward of ' + str(row.reward.item()) + '. You would have received ' + str(unchosen_reward1) + ', had you pressed ' + str(unchosen_option1) + '. You would have received ' + str(unchosen_reward2) + ', had you pressed ' + str(unchosen_option2) + '.\n'
                else:
                    prompt += 'You encounter stimuli ' + ', '.join(stimulus0 + stimulus1 + stimulus2) + '. You press <<' + choice + '>>.\n'

        prompt = prompt[:-1]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'bavard2023functional/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
