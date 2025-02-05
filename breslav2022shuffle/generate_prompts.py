import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
import pandas as pd
import torch
import h5py
from utils import randomized_choice_options

filename = "cgt_data.h5"
adv_cards = pd.read_hdf(filename, key='adv_cards')
choices = pd.read_hdf(filename, key='choices')
dis_cards = pd.read_hdf(filename, key='dis_cards')

all_prompts = []


subjects = choices.index.get_level_values('subject').values
participants = list(set(subjects.tolist()))

num_participants = len(participants)
num_trials=50
adv_wins = np.abs(adv_cards['win'].values).tolist()
adv_losses =np.abs(adv_cards['lose'].values).tolist()
dis_wins = np.abs(dis_cards['win'].values).tolist()
dis_losses = np.abs(dis_cards['lose'].values).tolist()


adv_dict = dict(adv_cards)
dis_dict = dict(dis_cards)


for participant in participants:
    
    
    choice_options = randomized_choice_options(num_choices=2)
    df_participant = choices.loc[participant]
    age = int(np.floor(df_participant['age_years'].values[0])) # floor the continuous age variable to round down to their 'conventional' age

    # we fix the second choice to be the suboptimal one here
    demo_string_adv = f'The first three cards from deck {choice_options[0]} are: '
    for i in range(1, 4):
        suffix1 = '' if adv_wins[i-1] == 1 else 's'
        suffix2 = '' if adv_losses[i-1] == 1 else 's'
        demo_string_adv += f'{i}) {adv_wins[i-1]} smiling face{suffix1} and {adv_losses[i-1]} frowning face{suffix2}. '

    
    demo_string_dis = f'The first three cards from deck {choice_options[1]} are: '
    for i in range(1, 4):
        suffix1 = '' if dis_wins[i-1] == 1 else 's'
        suffix2 = '' if dis_losses[i-1] == 1 else 's'
        demo_string_dis += f'{i}) {dis_wins[i-1]} smiling face{suffix1} and {dis_losses[i-1]} frowning face{suffix2}. '
    
    # shuffle order of which one you demonstrate first
    demo_strings_idx = np.random.permutation([0, 1])
    demo_strings = [demo_string_adv, demo_string_dis]
    demostring = demo_strings[demo_strings_idx[0]] + demo_strings[demo_strings_idx[1]]

    introduction_idx =np.random.permutation([0, 1])
    prompt ='In front of you there are two decks of face-down cards labeled ' + choice_options[introduction_idx[0]] + ' and ' +  choice_options[introduction_idx[1]] + '.\n'\
            'You will make 50 choices between the two decks of cards. After picking a card, it will be turned to reveal a number of smiling and frowning faces.\n'\
            'You get an initial endowment of 10 M&Ms.\n'\
            'You can gain or lose M&Ms from your endownment based on the net difference between the number of smiling and frowning faces.\n'\
            'To demonstrate, we will show you the first three cards from both decks, and remove them from the decks for the subsequent experiment.\n'\
            f'{demostring}'\
            'At the end of the experiment you get to keep the remainding M&Ms in your possession.\n'
    
    for trial in range(num_trials):
        chose_adv = int(df_participant['choose_adv'].values[trial])
        adv_top_card = df_participant['adv_top_card'].values[trial]
        dis_top_card = df_participant['dis_top_card'].values[trial]
        if chose_adv:
            card_win = adv_dict['win'][adv_top_card]
            card_loss = -adv_dict['lose'][adv_top_card]
            #card_win, card_loss = adv_wins[trial+3], adv_losses[trial+3]
        else:
            card_win = dis_dict['win'][dis_top_card]
            card_loss = -dis_dict['lose'][dis_top_card]

        suffix1 = '' if card_win == 1 else 's'
        suffix2 = '' if card_loss == 1 else 's'

        gain = card_win - card_loss # we take the sum since losses are negative
        abs_gain = np.abs(gain)
        #print(trial, int(df_participant['win'].values[trial]), card_win,  int(df_participant['lose'].values[trial]), card_loss, '    ', gain, int(df_participant['net_outcome'].values[trial]))
        #print(gain, int(df_participant['net_outcome'].values[trial]))
        if trial != 49:
            assert gain == int(df_participant['net_outcome'].values[trial])
        if card_loss > card_win:
            outcome = 'lose'
        else:
            outcome = 'gain'
            #card_win, card_loss = dis_wins[trial+3], dis_losses[trial+3]
        prompt += f'You choose deck <<{choice_options[1-chose_adv]}>>. You see {card_win} smiling face{suffix1} and {card_loss} frowing face{suffix2}. You {outcome} {abs_gain} M&Ms.\n'
        #continue
    prompt = prompt[:-2]
    all_prompts.append({'text': prompt,
            'experiment': 'breslav2022shuffle/' + 'exp1',
            'participant': str(participant),
            'age': str(age),
        })


print(prompt)
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)