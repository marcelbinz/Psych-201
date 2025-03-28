import pandas as pd
import jsonlines
import random
import string

# Randomize choice options: function to draw n random letters from the alphabet without replacement
def random_letters(n):
    return ''.join(random.sample(string.ascii_uppercase, n))


# Load lexical decision task data from CSV file
df = pd.read_csv('LDT_compounds_cleaned.csv')

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
    
    # Instruction text
    prompt = 'In the following study, you will see complex words such as airport or warzone in the browser window. You will have to judge for each word whether it exists as an English word or not.\n'\
        'For example, airport is an existing word, while saddleolive does not exist in the English language. Please respond as fast, but most importantly as accurately as possible.\n'\
        'We sincerely want to ask you to be as diligent as possible in making these judgements. For our study, we cannot analyse data only consisting of random answers.\n'\
        'You will see these words one after another. If the word presented to you exists, press the ' + choices[0] + ' key on your keyboard. If the word does not exist, press the ' + choices[1] + ' key. You are free to write these button assignments down if it helps you remembering them.\n'\
        'The study will not continue unless you give a response. Thus, if you want to pause the study, you can delay your response until you want to continue.\n'\
        'By pressing the ESC key, you will end the fullscreen mode. This does not hinder you from continuing the experiment, but you cannot switch back to fullscreen mode. If possible, we want to ask you to stay in fullscreen mode for the whole duration of the experiment.\n'
    
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_index'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            datapoint = f'{word}. You press <<{response}>>.\n'
            prompt += datapoint
            
            # Store reaction time
            rt = df_trial['RTs'].iloc[0].item()
            rt_list.append(rt)
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2020LDT',
        'participant': participant,
        'RTs': rt_list,
        'age': age
    })

# Save all prompts to JSONL file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
