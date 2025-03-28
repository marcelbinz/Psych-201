import numpy as np 
import pandas as pd 
import jsonlines

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

datasets = ['../../../exp1.csv']
all_prompts = []
for dataset in datasets:
    df = pd.read_csv(dataset)
    df = df[df['task']!=-1]
    participant_list = list(set(df['participant']))
    for p,participant in enumerate(participant_list):
        df_participant = df[df['participant']==participant]

        RTs, attentions, anxieties, feedbacks = [], [], [], []

        choice_options = randomized_choice_options(num_choices=2)

        task_list = list(set(df_participant['task']))

        prompt = 'You will be given three numbers (N1, N2, N3). Your task is to make a binary selection by pressing a corresponding key to judge whether the subtraction between the first two numbers is divisible by the third number.\n'\
        'During each trial, you will answer a new question, where you may or may not receive a visual feedback to show you the time passage when you are working on the task.\n'\
        f'You should select label {choice_options[1]} when the subtraction between N1 and N2 is divisible by N3. Otherwise, You should select label {choice_options[0]}.\n'\
        'Your goal is to do your best to answer each trial as soon as possible, but be sure to prioritize your accuracy rather than your response time.\n\n'\
        
        for task in task_list:
            df_task = df_participant[df_participant['task']==task]

            prompt += 'Task ' + str(int(task) + 1) + ':\n'

            trial_list = list(set(df_task['step']))
            trial_list.sort()
            for trial in trial_list:
                df_trial = df_task[df_task['step']==trial]
                t = int(df_trial['truth'].values[0])
                accuracy = df_trial['accuracy'].values[0]
                c = t if accuracy == 1 else 1-t
                feedback = df_trial['feedback'].values[0]
                RTs.append(df_trial['resptime'].values[0]*1000)
                attentions.append(df_trial['attention'].values[0])
                anxieties.append(df_trial['anxiety'].values[0])
                feedbacks.append(feedback)
                feedback_info = 'There is no time pressure to show you the time passage when you are working on the task.' if feedback == 0 else 'There is a time pressure visual feedback to show you the time passage when you are working on the task.'

                num_1 = df_trial['num_1'].values[0]
                num_2 = df_trial['num_2'].values[0]
                num_3 = df_trial['num_3'].values[0]
                feature_information = f'N1 = {num_1}, N2 = {num_2}, N3 = {num_3}. {feedback_info}'

                prompt += 'You see ' + feature_information + ' You select <<' + choice_options[c] + '>>. The correct selection is ' + choice_options[t] + '.\n'
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)
        all_prompts.append({'text': prompt, 'experiment': 'xu2023augmenting/' + dataset, 'participant': p, 'RTs': RTs, 'attention': attentions, 'anxiety': anxieties, 'feedback':feedbacks})


with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)