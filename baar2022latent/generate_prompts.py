import pandas as pd
import numpy as np
import jsonlines

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

df = pd.read_csv('Study1_MTurk/Data/Cleaned/gameDat.csv')
print(df.columns)
print(len(df.subID.unique()))

all_prompts = []
for subject in df.subID.unique():
    choice_options = randomized_choice_options(2)
    trial_types = []

    prompt = "You will take part in a Social Prediction Game.\n"\
        "You will observe a Player playing against an Opponent in different games.\n"\
        "In each game, the Player and the Opponent simultaneously choose between option " + choice_options[0] + " and option " + choice_options[1] + ".\n"\
        "The Player and the Opponent win points based on their choices.\n"\
        "The rules change between games, and you will be informed about them before each game.\n"\
        "The Player varies between blocks but is consistent across games within a block.\n"\
        "The Opponent switches in each game.\n"\
        "Your task is to predict the choices made by the Player and rate your confidence in this prediction on an 11-point scale from 0 to 100 (in increments of 10).\n"\
        "You get feedback after each game on whether your prediction was correct or not.\n\n"\

    df_sub = df[df['subID'] == subject]
    for block in range(4):
        prompt += 'Block ' + str(block + 1) + ' starts now.\n\n'
        df_block = df_sub[df_sub['Block'] == block]
        for trial in range(16):
            df_trial = df_block[df_block['Trial'] == trial]

            # 0 co-operate, 1 defect
            T = df_trial['T'].item()
            S = df_trial['S'].item()
            conf = df_trial['ConfidenceNum'].item()
            human_response = choice_options[1] if df_trial['GivenAns'].item() == 'def' else choice_options[0]
            correct = 'correct' if df_trial['GivenAns'].item() ==  df_trial['CorrAns'].item() else 'incorrect'

            trial_types.append(df_trial['Type_Total'].item())

            prompt += "The rules of the game are as follows:\n"\
                "If Player chooses option " + choice_options[0] + " and Opponent chooses option " + choice_options[0] + ", then Player wins 10 points and Opponent wins 10 points.\n"\
                "If Player chooses option " + choice_options[0] + " and Opponent chooses option " + choice_options[1] + ", then Player wins " + str(S) + " points and Opponent wins " + str(T) + " points.\n"\
                "If Player chooses option " + choice_options[1] + " and Opponent chooses option " + choice_options[0] + ", then Player wins " + str(T) + " points and Opponent wins " + str(S) + " points.\n"\
                "If Player chooses option " + choice_options[1] + " and Opponent chooses option " + choice_options[1] + ", then Player wins 5 points and Opponent wins 5 points.\n"\
                "You predict that Player will choose option <<" + human_response + ">>. You indicate a confidence of <<" + str(conf) + ">>. Your prediction was " + correct + ".\n\n"

    prompt = prompt[:-2]
    print(prompt)
    all_prompts.append({
        'text': prompt,
        'experiment': 'baar2021latent/exp1.csv',
        'participant': str(subject),
        'trial_types': trial_types,
    })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
