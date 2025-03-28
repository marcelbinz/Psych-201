import pandas as pd
import jsonlines

# load data
df = pd.read_csv('comprehension_questions_cleaned.csv')

# creating new column "experiment" extracting the substring betweeen the first and the second "_" in the "participant" column
df['experiment'] = df['participant'].apply(lambda x: x.split('_')[1])

# sort df by participant and trial index
df = df.sort_values(by=['participant'])

# create trial index variable for each participant
df['trial_index'] = df.groupby('participant').cumcount()+1

# map participant number to 1:len(df.participant.value_counts())
df['participant'] = df['participant'].map({p: i+1 for i, p in enumerate(df.participant.unique())})

# Separate data for each experiment
exp1 = df[df['experiment'] == '1word']
exp2 = df[df['experiment'] == 'open']

# create empty list to store all prompts
all_prompts = []


################
# Experiment 1 #
################
# Define number of participants and trials
participants_exp1 = exp1["participant"].unique()
trials_exp1 = range(exp1["trial_index"].max() + 1)

# define initial prompt
instruction1 = 'In the following study, you will see 66 sentences with questions. Your task is to read these sentences carefully and then answer the questions. Please answer using only one word.\n'\
'You can work at your own pace, and make pauses whenever you want to.\n'\


# Experiment1: Generate individual prompts for participants
for participant in participants_exp1:
    exp1_participant = exp1[exp1["participant"] == participant]
    participant = participant.item()
    individual_prompt = instruction1
    rt_list = []
    for trial in trials_exp1:
        exp1_trial = exp1_participant.loc[exp1_participant["trial_index"] == trial]
        if not exp1_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp1_trial["stimulus"].iloc[0]
            response = exp1_trial["response"].iloc[0]
            datapoint = f"{stimulus.strip()}. You enter <<{response}>>.\n"
            individual_prompt += datapoint
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024comprehension/condition1",
            "participant": participant,
        }
    )
    
    
################
# Experiment 2 #
################
# Define number of participants and trials for experiment 2
participants_exp2 = exp2["participant"].unique()
trials_exp2 = range(exp2["trial_index"].max() + 1)

# Define initial prompt for experiment 2
instruction2 = 'In the following study, you will see 66 sentences with questions. Your task is to read these sentences carefully and then answer the questions.\n'\
'You can work at your own pace, and make pauses whenever you want to.\n'

# Experiment2: Generate individual prompts for participants
for participant in participants_exp2:
    exp2_participant = exp2[exp2["participant"] == participant]
    participant = participant.item()
    individual_prompt = instruction2
    rt_list = []
    for trial in trials_exp2:
        exp2_trial = exp2_participant.loc[exp2_participant["trial_index"] == trial]
        if not exp2_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp2_trial["stimulus"].iloc[0]
            response = exp2_trial["response"].iloc[0]
            datapoint = f"{stimulus.strip()}. You enter <<{response}>>.\n"
            individual_prompt += datapoint
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024comprehension/condition2",
            "participant": participant,
        }
    )


# Save all prompts to JSONL file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
