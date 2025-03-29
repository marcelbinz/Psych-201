import numpy as np
import pandas as pd
import jsonlines
import sys
import json
sys.path.append("..")

datasets = ["tinyalchemy.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    df["id"] = df["id"].astype(int)
    df["trial"] = df["trial"].astype(int)
    num_participants = df.id.max() + 1

    for participant in range(num_participants-1):
        print(participant)
        participant += 1
        df_participant = df[(df["id"] == participant)]
        if(len(df_participant) != 0):


            prompt = 'Explore a universe of elements! \n'\
            'This game is called "Tiny Alchemy". It is your task to dicover elements. \n'\
            'You can create elements by proposing experiments. Experiments let you combine two elements. \n'\
            'You start out with 4 base elements in your inventory. You can choose two elements to test a combination. \n'\
            'If the experiment did not create a new element, then nothing happens. If the experiments created a new element, then this element gets added to your inventory and you can use it for future experiments. \n'\
            'It is your goal to create as many elements as possible. In principle, there are 520 elements you could discover. However, no one has ever discovered all of them. You can play as long as you want. \n\n'      

            num_trials = df_participant.trial.max() + 1
            inventory = ["water", "fire", "earth", "air"]

            for trial in range(num_trials-1):
                trial += 1
                df_trial = df_participant[(df_participant['trial'] == trial)]
                e1 = df_trial["n1"].loc[df_trial.index[0]]
                e2 = df_trial["n2"].loc[df_trial.index[0]]
                out = df_trial["out"].loc[df_trial.index[0]] 

                prompt += "Your inventory contains "
                for i in range(len(inventory)):
                    if i < len(inventory)-1:
                        prompt += inventory[i] + ", "
                    else:
                        prompt += "and " + inventory[i] + ". "

                if(out == "none"):
                    prompt += "You combine <<" + e1 + ">> and <<" + e2 + ">>. You don't create an element.\n"
                elif(out in inventory):
                    prompt += "You combine <<" + e1 + ">> and <<" + e2 + ">>. You rediscover "+ out + ".\n"
                else:
                    prompt += "You combine <<" + e1 + ">> and <<" + e2 + ">>. You discover "+ out + ".\n"
                    inventory.append(out)

                prompt += '\n'
            prompt += '\n'
            all_prompts.append({'text': prompt, 'experiment': 'braendle2023empowerment/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)