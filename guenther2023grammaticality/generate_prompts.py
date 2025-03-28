import pandas as pd
import jsonlines
import random
import string

# Randomize choice options: function to draw n random letters from the alphabet without replacement
def random_letters(n):
    return ''.join(random.sample(string.ascii_uppercase, n))


# load data
df = pd.read_csv('grammaticality_judgments_cleaned.csv')

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant', 'trial_index'])

# Remap participant IDs to sequential integers starting from 1
df['participant'] = df['participant'].map({p: i+1 for i, p in enumerate(df.participant.unique())})

# Get unique participants and trial indices
participants = df['participant'].unique()
trials = range(df['trial_index'].max() + 1)



# Generate individual prompts for each participant
all_prompts = []
for participant in participants:
    # Get data for current participant
    df_participant = df[df['participant'] == participant]
    participant = participant.item()
    age = df_participant['age'].iloc[0].item()
    rt_list = []

    # generate two choice options
    choices = random_letters(2)
    
    # Update response column using loc
    df_participant.loc[df_participant["response"] == "c", "response"] = choices[0]
    df_participant.loc[df_participant["response"] == "n", "response"] = choices[1]
    
    # instruction text
    prompt = 'In the following study, you will see 110 sentences. Your task is to indicate whether these sentences are grammatically correct in English.\n'\
        'Press the ' + choices[0] + ' key on your keyboard if the sentence is grammatically correct, and the ' + choices[1] + ' key if it is not grammatically correct.\n'\
        'You can work at your own pace, and make pauses whenever you want to.\n'\
        'Is this sentence grammatically correct in English?\n'\
        'Press ' + choices[0] + ' if it is correct, and ' + choices[1] + ' if it is not correct.\n'
    
    
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_index'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            datapoint = f'{word}. You press <<{response}>>.\n'
            prompt += datapoint
            # reaction time
            rt = df_trial['RTs'].iloc[0].item()
            rt_list.append(rt)
    
    prompt += '\n'
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2023Grammaticality',
        'participant': participant,
        'age': age,
        'RTs': rt_list
    })

# Save all prompts to JSONL file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
