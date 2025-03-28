import numpy as np
import pandas as pd
import jsonlines
import ipdb

datasets = ["exp1.csv", "exp2.csv", "exp3.csv", "exp4.csv"]
all_prompts = []
machine_types = {'neg': 'green', 'pos': 'green',
                 'even': 'blue', 'odd': 'blue',
                 'negeven':'connected green-blue', 'poseven': 'connected green-blue',
                 'negodd': 'connected green-blue', 'posodd': 'connected green-blue',
                 'oddneg': 'connected blue-green', 'oddpos': 'connected blue-green',
                 'evenneg': 'connected blue-green', 'evenpos': 'connected blue-green'}


for dataset in datasets:
    df = pd.read_csv(dataset)

    num_participants = df.participant.max() + 1
    num_tasks = df.task.max() + 1

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]
        num_trials = int(df_participant.trial_within_subtask.max()) + 1 # participant specific number of trials

        # each with three different features
        prompt = "You are going to be a gambler visiting the fictional town of Bandit City.\n"\
        "Bandit City has several casinos lined up next to one another.\n"\
        "You will visit all 20 casinos in the city.\n"\
        "Every casino has two slot machines, a green one and a blue one.\n"\
        "Each slot machine has 6 options, represented by the keys 1 to 6.\n"\
        "You can select an option by pressing the corresponding key.\n"\
        "The number of coins you can get is different for the different keys of the slot machine.\n"\
        "You have 5 trials on each slot machine and your goal is to win as many coins as possible.\n"\
        "During his visit to Bandit City last weekend, a friend of yours noticed that slot machines of the same color behaved somewhat similarly.\n"\
        "Machines of one color always showed either a rising or a falling pattern.\n"\
        "He could either get more coins as he went from option 1 to 6 (rising) or fewer coins as he went from option 1 to 6 (falling).\n"\
        "Machines of the other color always showed an alternating pattern.\n"\
        "He saw that every other option was highly rewarding so either options (1, 3, 5) or (2, 4, 6) could be more rewarding.\n"\
        "Unfortunately, your buddy only remembers the patterns but does not recollect which color belongs to which pattern.\n"\

        if dataset == 'exp1.csv' or dataset == 'exp3.csv':
            prompt += "After you finish playing against the two slot machines, casino owners will connect the green and blue machines together and ask you to play against the connected slot machine.\n"\

            if dataset == 'exp1.csv': # add and compositional
                prompt += "The machines are connected such that pressing an option on one will result in pressing the same option on the other.\n"\
			    "This connected machine will be referred to as a connected green-blue machine.\n"\
			    "The total coins you earn by choosing an option on the connected machine is the sum of the coins from the two slot machines.\n"\
			    "Essentially, you will be playing three slot machines (green, blue, and connected green-blue) in each casino today.\n\n"
            else: # changepoint and compositional
                prompt += "The machines are connected such that it has blocks of three options, either (1, 2, 3) or (4, 5, 6), from the previously played slot machines.\n"\
                "Three options for such a connected machine will be green and the remaining in blue indicating the slot machine they are from.\n"\
                "This connected machine will be referred to as a connected green-blue or blue-green machine depending on the order of the options.\n"\
                "The coins for an option is expected to be roughly equal to that of the same colored option previously seen in the casino.\n"\
                "Essentially, you will be playing three slot machines (green, blue, and connected green-blue or blue-green) in each casino today.\n\n"
        else:
            prompt += '\n'


        for task in range(num_tasks):
            df_task = df_participant[(df_participant['task'] == task)]
            prompt += 'You are playing in casino ' + str(task + 1) + ':\n'
            num_subtasks = df_task.subtask.max() + 1

            for subtask in range(num_subtasks):
                df_subtask = df_task[(df_task['subtask'] == subtask)]

                for trial in range(num_trials):
                    df_trial = df_subtask[(df_task['trial_within_subtask'] == trial)]
                    if (dataset == 'exp1.csv' or dataset == 'exp3.csv') and trial==0: # include subtask information for compositional tasks
                        prompt += f'You are interacting with the {machine_types[df_trial.function.item()]} slot machine.\n'
                    c = df_trial.choice.item()
                    reward = df_trial.reward.item()
                    prompt += 'You press <<' + str(c+1) + '>> and get ' + str(round(reward, 2)) + ' coins.\n'
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'jagadish2023zero/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
