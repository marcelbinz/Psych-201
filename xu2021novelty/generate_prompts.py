import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

dataset = "exp.csv"
all_prompts = []

df = pd.read_csv(dataset)

num_participants = df.participant.max() + 1
num_tasks = df.task.max() + 1


goal_reached_text = 'You reach the goal state! Let us play the game one more time from the start.\n'
goal_reached_final = 'You reach the goal state!\n'
for participant in range(num_participants):
    df_participant = df[(df['participant'] == participant)]

    choice_options = randomized_choice_options(num_choices=4)
    prompt = 'You are playing a game where you are exploring an environment with 11 different states.\nYour task is to find the goal state as quickly as possible.\n'\
             f'In each state you can choose among 4 different actions. These actions have the following labels: {choice_options[0]}, {choice_options[1]}, {choice_options[2]}, and {choice_options[3]}.\nYou choose an action by pressing the corresponding key.\n'\
             'Upon choosing an action, you may arrive at a new state or one that you already visited, depending on the chosen action.\n'\
             'You will play the game for 10 rounds.\n\n'\



    for task in range(num_tasks):
        df_task = df_participant[(df_participant['task'] == task)]
        prompt += 'Round ' + str(task + 1) + ':\n'
        num_trials = df_task.trial.max() + 1  # get the number of trials of this specific task
        for trial in range(num_trials):
            df_trial = df_task[(df_task['trial'] == trial)]
            choice = df_trial.choice.item()
            r = df_trial.reward.item()
            s = df_trial.state.item()
            s_prime = df_trial.next_state.item()

            prompt += 'You are currently in state ' + str(s) + ' and you press <<' + str(choice_options[choice-1]) + '>>. You arrive at state ' + str(s_prime) + '.\n'
            if r > 0:
                if task == (num_tasks - 1):
                    prompt += goal_reached_final
                else:
                    prompt += goal_reached_text

        prompt += '\n'

    prompt = prompt[:-2] # remove the last line break
    print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'xu2021novelty/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
