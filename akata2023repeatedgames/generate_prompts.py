import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

def calculate_other_score(game_type, action, coordination):
    if game_type == 0:
        if coordination:
            return 8 if action == 0 else 5
        else:
            return 10 if action == 0 else 0
    elif game_type == 1:
        if coordination:
            return 7 if action == 0 else 10
        else:
            return 0

datasets = ["repgames.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)

    num_tasks = 2
    num_trials = 10

    for participant in df['id'].unique():

        df_participant = df[(df['id'] == participant)]

        choice_options = randomized_choice_options(num_choices=2)

        prompt_pd = "\nYou are playing a new game repeatedly with another player. In this game, you can choose between Option " + choice_options[0] + " and Option " + choice_options[1] + ". "\
            f"You will play {num_trials} rounds in total with the same player. "\
            "The rules of the game are as follows:\n"\
            "If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[0] + ", then you win 8 points and the other player wins 8 points.\n"\
            "If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[1] + ", then you win 0 points and the other player wins 10 points.\n"\
            "If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[0] + ", then you win 10 points and the other player wins 0 points.\n"\
            "If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[1] + ", then you win 5 points and the other player wins 5 points.\n\n"

        prompt_bos = "\nYou are playing a new game repeatedly with another player. In this game, you can choose between Option " + choice_options[0] + " and Option " + choice_options[1] + ". "\
            f"You will play {num_trials} rounds in total with the same player. "\
            "The rules of the game are as follows:\n"\
            "If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[0] + ", then you win 10 points and the other player wins 7 points.\n"\
            "If you choose Option " + choice_options[0] + " and the other player chooses Option " + choice_options[1] + ", then you win 0 points and the other player wins 0 points.\n"\
            "If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[0] + ", then you win 0 points and the other player wins 0 points.\n"\
            "If you choose Option " + choice_options[1] + " and the other player chooses Option " + choice_options[1] + ", then you win 7 points and the other player wins 10 points.\n\n"

        prompt = "You will play two different 2x2 games. This means both games are played with 2 players and each player get to choose between 2 available options."\
            " Which option you choose is up to you and each of them may earn you a different number of points depending on the game rules and your opponent's moves."\
            " Each game consists of 10 rounds in total. On each round, you will have a chance to choose from the provided two options.\n"

        for task in range(0, num_tasks):
            if task == 0:
                prompt += prompt_pd
            else:
                prompt += prompt_bos

            for trial in range(0, num_trials):
                # print(trial)
                game = df_participant['game'].iloc[task*10 + trial]
                action = df_participant['action'].iloc[task*10 + trial]
                score = df_participant['score'].iloc[task*10 + trial]
                coordination = df_participant['coordination'].iloc[task*10 + trial]

                action_other = action if coordination == 1 else 1 - action
                score_other = calculate_other_score(task, action, coordination)

                prompt += f"In round {trial+1}, you chose Option <<" + choice_options[action] + ">> and the other player chose Option " + choice_options[action_other] + f". Thus, you won {score} points and the other player won {score_other} points.\n"

            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)

        all_prompts.append({'text': prompt,
            'experiment': 'akata2023repeatedgames/' + dataset,
            'participant': str(participant),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)