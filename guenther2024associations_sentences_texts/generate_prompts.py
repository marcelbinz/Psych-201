import pandas as pd
import jsonlines

# load data
exp1 = pd.read_csv('associations_sentences_cleaned_LS.csv')
exp2 = pd.read_csv('associations_texts_cleaned_LS.csv')

# create empty list to store all prompts
all_prompts = []


###########################
# Experiment 1: Sentences #
###########################


# Experiment 1: Define number of participants and trials
participants_exp1 = exp1['participant'].unique()
trials_exp1 = range(exp1['trial_index'].max() + 1)

# Instructions
# Experiment 1: Block 1 instructions
instruction_block1_exp1 = 'You will first read a sentence describing events or personalities. After you have read the sentence, you will be asked to list the 3 first associations that come to your mind when you think about these events or personalities.\n'\
    'Try not to think too much and type in the first words that you thought of. Ensure they are different from each other. Do not try to remember what you know but follow your first impulse.\n'\ 
    'Once you have read the sentence and proceeded to the next screen to type in the associations, you cannot go back to the previous screen with the sentence. Please pay attention during the reading and try to come up with the associations right after you finished reading the sentence.\n'\
    'You will not be able to type in the words used in the sentence. If you do, you will be asked to match the requested format.\n'\
    'Use letters only, no digits, spaces or punctuation marks.\n'\
    'Do not use words from the sentence or repeat the same word twice.\n'\
    'Please remember, your task is to:\n'\
    '- read the sentence.\n'\
    '- think of 3 first words that come to your mind when you think about the events or personalities described.\n'\
    'Do not try to remember what you know about these events or people but follow your first impulse.\n'\
    'Do not use the words from the sentence or repeat the same word twice. Use letters only.\n'\


# Experiment 1: Block 2 instructions
instruction_block2_exp1 = 'That concludes the main part experiment!\n'\
    'In the post-experiment task, you will be asked to once again read the sentences about events or personalities that you read in the main part and to rate these events or personalities on a scale from "very bad" to "very good". Do not think too much but follow your first intuition.\n'\
    'Please do not skip reading the sentences! This will ensure the data we collect from you is of high quality.\n'\
    'Do not rush, for the first question, the scale will be disabled for the first 4 seconds after the sentence presentation.\n'


# Experiment 1: Generate individual prompts for participants
for participant in participants_exp1:
    exp_participant = exp1[exp1['participant'] == participant]
    participant = participant.item()
    age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction_block1_exp1
    rt_list = []
    for trial in trials_exp1:
        exp_trial = exp_participant.loc[exp_participant['trial_index'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            trial_instruction = exp_trial['trial_instruction'].iloc[0]
            trial_index = exp_trial['trial_index'].iloc[0]
            # add the instruction for the block2 trials before trial 21
            if trial_index == 21:
                datapoint = f'{instruction_block2_exp1} {stimulus} {trial_instruction} You enter <<{response}>>.\n'
            else:
                datapoint = f'{stimulus} {trial_instruction} You enter <<{response}>>.\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'guenther2024associations/experiment1', 'participant': participant, 'age': age})



#######################
# Experiment 2: Texts #
#######################

# Experiment 2: Define number of participants and trials
participants_exp2 = exp2['participant'].unique()
trials_exp2 = range(exp2['trial_index'].max() + 1)

# Instructions
# Experiment 2: Block 1 instructions
instruction_block1_exp2 = 'You will first read a text describing historical events or personalities. These events or personalities will always be introduced in the first sentence and referred to using pronouns (e.g., they or it) in each subsequent sentence.\n'\
    'After you have read the text, you will be asked to list the 3 first associations that come to your mind when you think about these events or personalities. Try not to think too much and type in the first but different words that you think of. Do not try to remember what you know about the events or people described but follow your first impulse.\n'\
    'Once you have read the text and proceeded to the next screen to type in the associations, you cannot go back to the previous screen with the text. Please pay attention during the reading and try to come up with the associations right after you finished reading the text.\n'\
    'You will not be able to type in the words used in the text. If you do, you will be asked to match the requested format.\n'\
    'Use letters only, no digits, spaces or punctuation marks.\n'\
    'Do not use words from the text or repeat the same word twice.\n'\
    'Please remember, your task is to:\n'\
    '- read the text\n'\
    '- think of 3 first words that come to your mind when you think about the events or personalities described\n'\
    '- press the button to type in the associations\n'\
    'Do not try to remember what you know about these events or people but follow your first impulse.\n'\
    'Do not use the words from the text or repeat the same word twice. Use letters only.\n'\
    'Press "Enter" to verify your input and proceed to the next line.\n'

# Experiment 2: Block 2 instructions
instruction_block2_exp2 = 'That concludes the main part experiment!\n'\
    'In the post-experiment task, you will be asked to once again read the texts about political events or personalities that you read in the main part and to rate these events or personalities on a scale from "very bad" to "very good". Do not think too much but follow your first intuition.\n'\
    'Please do not skip reading the text! This will ensure the data we collect from you is of high quality.\n'

# Experiment 2: Generate individual prompts for participants
for participant in participants_exp2:
    exp_participant = exp2[exp2['participant'] == participant]
    participant = participant.item()
    age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction_block1_exp2
    rt_list = []
    for trial in trials_exp2:
        exp_trial = exp_participant.loc[exp_participant['trial_index'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            trial_instruction = exp_trial['trial_instruction'].iloc[0]
            trial_index = exp_trial['trial_index'].iloc[0]
            # add the instruction for the block2 trials before trial 21
            if trial_index == 21:
                datapoint = f'{instruction_block2_exp2} {stimulus} {trial_instruction} You enter <<{response}>>.\n'
            else:
                datapoint = f'{stimulus} {trial_instruction} You enter <<{response}>>.\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'guenther2024associations/experiment2', 'participant': participant, 'age': age})


# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
