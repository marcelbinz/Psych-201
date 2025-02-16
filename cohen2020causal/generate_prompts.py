import numpy as np
import pandas as pd
import jsonlines
import sys
import os
sys.path.append("..")


# Define function to make randomized choices
def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

# Set working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

datasets = ["anonymized_mining_data.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)

    num_tasks = df.block_num.max() + 1
    num_trials = df.trial_in_block.max() + 1
    territory = {1: "robber", 2 : "millionaire", 3: "sheriff"}
    no_yes = {0: "no", 1: "yes"}
    rocks_gold = {0: "rocks", 1: "gold"}

    for participant in df['subject'].unique():
        RTs = []

        df_participant = df[(df['subject'] == participant)]
        age = df_participant.age.iloc[0]

        choice_options = randomized_choice_options(num_choices=2)

        prompt = "In this task you are mining for gold in the Wild West. You earn a bonus money each time you find gold and lose bonus each time you find rocks.\n"\
                "On each trial, you are presented with two different mines, and have to select one at which to dig for gold by pressing its corresponding buttons " + choice_options[0] + " or " +  choice_options[1] + ".\n"\
                "After making each selection, you are presented with either gold or rocks. Within each block, you should try to discover and continue to select the mine that is likely to provide gold.\n"\
                "You will complete three blocks of 50 trials each. Critically, each block takes place within a different territory, in which a different hidden agent intervenes on the mines in a small number of trials.\n"\
                "In millionaire territory, a nice millionaire sometimes puts gold in both mines, such that both mines contain gold.\n"\
                "In robber territory, a mean robber sometimes replaces the gold in both mines with rocks, such that both mines contain rocks.\n"\
                "In sheriff territory, a sneaky sheriff sometimes randomly put rocks and gold in either mine.\n"\
                "After picking a mine and being presented with either gold or rocks, you will be asked to indicate whether you believe it was caused by the hidden agent with a “yes” or “no” response.\n\n"

        for task in range(1, num_tasks):
            df_task = df_participant[(df_participant['block_num'] == task)] 
            condition = df_task.condition.iloc[0]

            prompt += 'You are in the ' + territory[condition] + ' territory:\n'

            # Loop through trials
            for trial in df_task.trial_in_block:
                df_trial = df_task[(df_task['trial_in_block'] == trial)]
                c = df_trial.subj_choice.item()
                r = df_trial.feedback.item()
                RTs.append(df_trial.choice_RT.item())
                prompt += 'You press <<' + choice_options[c] + '>> and get ' + rocks_gold[r] + '. Do you think this was caused by the hidden agent? You choose <<' + no_yes[df_trial.latent_guess.item()]+ ">>.\n"
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)

        all_prompts.append({'text': prompt,
            'experiment': 'cohen2020causal/',
            'participant': str(participant),
            'RTs': RTs,
            'age': str(age)
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)