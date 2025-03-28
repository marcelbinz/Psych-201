import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

all_prompts = []
df = pd.read_csv('exp.csv')

num_participants = df.participant.max() + 1

for participant in range(num_participants):
    df_participant = df[(df['participant'] == participant)]
    num_trials = int(df_participant.trial.max() + 1)
    choice_options = randomized_choice_options(num_choices=2)

    prompt = 'You are repeatedly presented with a safe option and a risky option.\n'
    prompt += 'In each round, you have to select one of the two options.\n'
    prompt += 'The safe option always leads to the same outcome (OS).\n'
    prompt += 'The risky option can lead to two possible outcomes (O1 or 02).\n'
    prompt += 'You can select the safe option by pressing ' + choice_options[0] + ' and the risky option by pressing ' + choice_options[1] + '.\n'
    prompt += 'Following your selection, you observe an outcome and collect the points associated with it.\n'
    prompt += 'Your goal is to maximize the amount of collected points across the entire experiment.\n\n'

    for trial in range(num_trials):
        df_trial = df_participant[(df_participant['trial'] == trial)]
        if df_trial.outcome_reached.item() == 1:
            observed_outcome = 'O1'
        elif df_trial.outcome_reached.item() == 2:
            observed_outcome = 'O2'
        elif df_trial.outcome_reached.item() == 3:
            observed_outcome = 'OS'
        p_O1 = round(100 * df_trial.p_o1.item(), 4)
        p_O2 = round(100 * (1-df_trial.p_o1.item()), 4)
        prompt += 'The safe option always results in outcome OS associated with ' + str(df_trial.safe_val.item()) + ' points.\n'
        prompt += 'The risky option either results in outcome O1 associated with ' + str(df_trial.o1_val.item()) + ' points or in outcome O2 associated with ' + str(df_trial.o2_val.item()) + ' points. '
        prompt += 'The chance of observing outcome O1 is ' + str(p_O1) + '%. The chance of observing outcome O2 is ' + str(p_O2) + '%.\n'
        prompt += 'You press <<' + str(choice_options[df_trial.choice.item()]) + '>>. You observe outcome ' + observed_outcome + ' and receive ' + str(df_trial.reward.item()) +' points.\n'
        prompt += '\n'

    prompt = prompt[:-2]
    print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'russek2024heuristics/exp.csv', 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
