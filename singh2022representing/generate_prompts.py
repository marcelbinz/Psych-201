import numpy as np
import pandas as pd
import jsonlines
import sys
from tqdm import tqdm

all_prompts = []

df = pd.read_csv('behavior_propensity_data_remapped_pids.csv')

for participant in tqdm(df.PID.unique()):
    prompt = 'You will be presented with a series of behavior phrases.\n' \
        'For each behavior phrase X, you will be asked to rate the statement "Relative to others, I am likely to X."\n' \
        'Please respond with a whole number from 1 (meaning strongly disagree) to 7 (meaning strongly agree).\n' \
        'Try to compare yourself against the general population, rather than solely your peers, while evaluating the statements.\n\n'

    df_participant = df[df['PID'] == participant]

    for index, row in df_participant.iterrows():
        prompt += 'Relative to others, I am likely to ' + row['Phrase'] + '.\n'
        prompt += 'You respond with <<' + str(row['Ratings non-Z']) + '>>.\n\n'

    prompt = prompt[:-2]
    print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'singh2022representing/exp.csv', 'participant': str(participant)})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
