import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["patent_investments_743subs.csv"]
lsas_data_file = "mergedcovars.csv"
lsas_df = pd.read_csv(lsas_data_file)

all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)

    num_trials = 80

    for participant in df['sub'].unique():

        df_participant = df[(df['sub'] == participant)]
        ravens_value = lsas_df.loc[lsas_df['sub'] == participant, 'ravens'].iloc[0]
        lsas_value = lsas_df.loc[lsas_df['sub'] == participant, 'lsas'].iloc[0]
        iq_value = lsas_df.loc[lsas_df['sub'] == participant, 'iq'].iloc[0]
        age_value = lsas_df.loc[lsas_df['sub'] == participant, 'age'].iloc[0]

        prompt = f"\nYou are playing the Patent Race. In this game, you and your opponent compete for a prize by choosing an investment from your respective endowments. "\
        f"You will play {num_trials} rounds in total. In each round, you are endowed with 4 dollars, your opponent is endowed with 5 dollars, and the prize you are competing for is 10 dollars. " \
        f"The player who invests more wins the prize, and the other player loses. In the event of a tie, both players lose the prize. Regardless of the outcome, both players lose " \
        f"the amount that they invest.\n"\

        for trial in range(0, num_trials):
            # print(trial)
            investment_own = df_participant['s1'].iloc[trial]
            investment_other = df_participant['s2'].iloc[trial]
            reward = df_participant['r'].iloc[trial]

            if investment_own > investment_other:
                result = "Thus, you won" 
            elif investment_own < investment_other:
                result = "Thus, you lost"
            else:
                result = "Thus, you tied"    

            prompt += f"In round {trial+1}, you invested <<{investment_own-1}>> dollars and the other player invested {investment_other-1} dollars. " + result + f" and your final endowment for this round was {reward} dollars.\n"

        prompt = prompt[:-2]
        print(prompt)

        all_prompts.append({
            'text': prompt,
            'experiment': 'hunter2021increased/' + dataset,
            'participant': str(participant),
            'ravens': str(ravens_value),
            'lsas': str(lsas_value),
            'iq': str(iq_value),
            'age': str(age_value),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)