import pandas as pd
import jsonlines

# load data
exp = pd.read_csv('associations_individual_cleaned.csv')

# combine the response variable
exp['response'] = exp['response1'] + ', ' + exp['response2'] + ', ' + exp['response3'] + ', ' + exp['response4'] + ', ' + exp['response5'] + ', ' + exp['response6'] + ', ' + exp['response7'] + ', ' + exp['response8'] + ', ' + exp['response9'] + ', ' + exp['response10']


# Define number of participants and trials
participants_exp = exp['participant'].unique()
trials_exp = range(exp['trial_index'].max() + 1)

# define initial prompt
instruction = 'On the top of the screen a word will appear. Enter the first 10 words that come to mind when reading this word.\n'\
    'Please enter 10 different words for each word presented to you.\n'\
    'Please take this task seriously, and enter actual words. We kindly ask you to ensure that these words are spelled correctly.\n'\
    'Some hints\n'\
    'Only give associations to the word on top of the screen (not to your previous responses!)\n'\
    'Please only enter single words; otherwise, you will receive an error message.\n'

# define trial instruction
trial_instruction = 'Please enter the first 10 different words that come to your mind.'

# create empty list to store all prompts
all_prompts = []

# Generate individual prompts for participants
for participant in participants_exp:
    exp_participant = exp[exp['participant'] == participant]
    participant = participant.item()
    age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    rt_list = []
    for trial in trials_exp:
        exp_trial = exp_participant.loc[exp_participant['trial_index'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            datapoint = f'{stimulus}. {trial_instruction} You enter <<{response}>>.\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'guenther2024associations_individual', 'participant': participant, 'age': age})

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
