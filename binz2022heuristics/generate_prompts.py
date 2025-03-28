import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

datasets = ["exp1.csv", "exp2.csv", 'exp4.csv']
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)

    num_participants = df.participant.max() + 1
    num_tasks = df.task.max() + 1
    num_trials = df.step.max() + 1

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]

        choice_options = randomized_choice_options(num_choices=2)

        num_features = 2 if dataset == 'exp4.csv' else 4
        num_features_str = 'two' if dataset == 'exp4.csv' else 'four'
        if dataset == 'exp1.csv':
            side_information = 'The attributes are arranged based on their importance (attribute 1 is the most important to predict the winner).\n'
        if dataset == 'exp2.csv':
            side_information = 'High attributes make it more likely to win in a competition.\n'
        if dataset == 'exp4.csv':
            side_information = ''

        prompt = 'You will be visiting different planets on which you repeatedly have to predict a winner in an athletic competition between two aliens, labelled ' + choice_options[0] + ' and ' + choice_options[1] + '.\n'\
        'In each round, you have to indicate the winner by pressing the corresponding key.\n'\
        'Your goal is to be as accurate as possible.\n'\
        'To aid your decision process, you are provided with ' +  num_features_str  + ' attributes of the two aliens.\n' + side_information + ''\
        'You receive feedback telling you which alien won after you have made a choice.\n'\
        'You have to make ten predictions per planet.\nFor each prediction, you encounter a new pair of aliens.\n'\
        'You are beamed to a new planet after making ten predictions, where you have to make predictions about a new and different athletic competition.\n\n'

        for task in range(num_tasks):
            df_task = df_participant[(df_participant['task'] == task)]
            prompt += 'Planet ' + str(task + 1) + ':\n'

            for trial in range(num_trials):
                df_trial = df_task[(df_task['step'] == trial)]
                c = df_trial.choice.item()
                t = df_trial.target.item()
                x0 = df_trial.x0.item()
                x1 = df_trial.x1.item()
                if dataset != 'exp4.csv':
                    x = [df_trial.x0.item(), df_trial.x1.item(), df_trial.x2.item(), df_trial.x3.item()]
                else:
                    x = [df_trial.x0.item(), df_trial.x1.item()]

                feature_information = ''
                for num_feature in range(num_features):
                    if x[num_feature] > 0:
                        feature_information += 'Alien ' + choice_options[0] + ' scores ' + str(x[num_feature]) + ' higher on attribute ' + str(num_feature + 1) + '. '
                    else:
                        feature_information += 'Alien ' + choice_options[1] + ' scores ' + str(-x[num_feature]) + ' higher on attribute ' + str(num_feature + 1) + '. '
                feature_information = feature_information[:-2]
                prompt += '' + feature_information + '. You press <<' + choice_options[c] + '>>. Alien ' + choice_options[t] + ' wins.\n'
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'binz2022heuristics/' + dataset, 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
