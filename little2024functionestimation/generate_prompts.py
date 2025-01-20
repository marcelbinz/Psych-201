import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")

datasets = ["little2024functionestimation.csv"]
sampling_rate = 40
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)

    num_participants = df.participant.max() + 1
    num_tasks = df.task.max() + 1

    for participant in range(1, num_participants+1):
        df_participant = df[(df['participant'] == participant)]

        prompt =  'In this experiment, you will be shown a series of graphs containing some data points. Your task is to'\
            'estimate the function that generated the data points.'\
            'Each graph gives data from a different fictional experiment. These data are not real but you should treat'\
            'them as if they were data from an actual scientific experiment. You can think of each set of data as'\
            'caused by some underlying process which relates the X‐axis (the input) to the Y‐axis (the output).  In the'\
            'data that you will see, the exact causal relationship is unknown, but you will try to guess it solely on the'\
            'basis of the data we provide you in the graph.'\
            'It is important to note that, as in all science, the observations are not always accurate. We say the'\
            'data are ‘noisy’.  Hence, the data can be thought of as being sampled from some underlying process but'\
            'won’t necessarily match that process exactly.'\
            'Your task is predict the output, y values, for different inputs, x values, based on what you believe to be the true function which generated the data. \n'  
        
        for task in range(1, num_tasks+1):
            df_task = df_participant[(df_participant['task'] == task)]
            
            # add train points to the prompt
            df_task_train = df_task[df_task['type'] == 'train']
            num_datapoints_str = 'twenty-four' if len(df_task_train)==24 else 'six'
            if len(df_task_train) == 0:
                continue
            prompt += '\nIn task ' + str(task) + ', the ' + num_datapoints_str + ' input-output pairs you saw on the graph were as follows:\n'
            prompt += ''.join(['x={}, y={}\n'.format(x, y) for x, y in zip(df_task_train['x'].values, df_task_train['y'].values)])

            # prediction for test points
            data_task_test = df_task[df_task['type'] == 'test']
            prompt += 'Now, you predict the values for outputs, y, for different values of input, x:\n'
            test_x_values, test_y_values = data_task_test['x'].values[::sampling_rate], data_task_test['y'].values[::sampling_rate]
            prompt += ''.join(['x={}, you predict y = <<{}>>.\n'.format(str(float(x_value)), str(float(y_value))) for x_value, y_value in zip(test_x_values, test_y_values)])
           
            prompt += '\n\n'
            prompt = prompt[:-2]
            print(prompt)
            all_prompts.append({'text': prompt, 'experiment': 'little2024functionestimation/' + dataset, 'participant': participant})
            
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
