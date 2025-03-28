import pandas as pd
import json
import zipfile

# List to store all prompts (each prompt is a dictionary)
all_prompts = []

##################### Extract Psychometric Rating Prompts (Experiment 1) #####################

# Load experiment 1 data (ratings on 9 psychometric dimensions of risk perception)
exp_1 = pd.read_csv('psych_individual.csv', low_memory=False)
exp = 'psychRatings'

# Define high-level prompt components
exp_1_instructs = 'This study aims to investigate how people judge various aspects of potential sources of risk.\n'
exp_1_items = {
    # Participants either received the psychometric items in this order (FL_10) or the reverse (FL_23)
    'voluntary': 'On a scale from 1 (Voluntary) to 7 (Involuntary), how voluntarily are individuals exposed to this risk?: ',
    'delayed': 'On a scale from 1 (Immediate) to 7 (Delayed), is death from this risk immediate or delayed?: ',
    'known_sci': 'On a scale from 1 (Known to Science) to 7 (Unknown to science), is this risk known or unknown to science?: ',
    'known': 'On a scale from 1 (Known) to 7 (Unknown), is this risk known or unknown to the individuals exposed to the risk?: ',
    'controllable': 'On a scale from 1 (Controllable) to 7 (Uncontrollable), is risk controllable or uncontrollable to the individuals exposed to the risk?: ',
    'old': 'On a scale from 1 (New) to 7 (Old), is this risk new or old?: ',
    'catastrophic': 'On a scale from 1 (Chronic) to 7 (catastrophic), is this a risk that kills one person at a time (chronic) or a risk that kills large numbers of people at once (catastrophic)?: ',
    'dread': 'On a scale from 1 (Calm) to 7 (Dread), is this a risk that individuals can reason about calmly or is it one that they have great dread for?: ',
    'fatal': 'On a scale from 1 (Not Fatal) to 7 (Fatal), how fatal are the consequences of this risk?: ',
}

# Template for accessing item-stimuli pairs in the columns of exp_1 (stimuli are not yet defined in {})
exp_1_item_temp = {
    'voluntary': '[Field-counter] / 180 Questions Complete    [Field-1]     Are individuals exposed to this risk voluntarily or involuntarily? - {} - Click to write Statement 1',
    'fatal': '[Field-counter] / 180 Questions Complete    [Field-1]     How fatal are the consequences of this risk? - {} - How fatal are the consequences of this risk?',
    'delayed': '[Field-counter] / 180 Questions Complete    [Field-1]     Is death from this risk immediate or delayed? - {} - Click to write Statement 1',
    'dread': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this a risk that individuals can reason about calmly or is it one that they have great dread for? - {} - Is this a risk that individuals can reason about calmly or is it one that they have great dread for?',
    'catastrophic': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this a risk that kills one person at a time (chronic) or a risk that kills large numbers of people at once (catastrophic)? - {} - Is this a risk that kills one person at a time (chronic) or a risk that kills large numbers of people at once (catastrophic)?',
    'controllable': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this risk controllable or uncontrollable for the individual exposed to this risk? - {} - Is this risk controllable or uncontrollable for the individual exposed to this risk?',
    'known_sci': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this risk known or unknown to science? - {} - Click to write Statement 1',
    'known': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this risk known or unknown to the individuals exposed to this risk? - {} - .',
    'old': '[Field-counter] / 180 Questions Complete    [Field-1]     Is this risk new or old? - {} - Is this risk new or old?'
}

# Iterate over participants to generate prompts
for participant_i in range(len(exp_1)):
    dat_i = exp_1.iloc[participant_i]

    # Get ordered stimuli
    stimuli_blk_1 = dat_i['Multi-Choice Hack 1 - Display Order'].split('|')
    stimuli_blk_2 = dat_i['Multi-Choice Hack 2 - Display Order'].split('|')

    if isinstance(dat_i['FL_10 - Block Randomizer - Display Order'], str):  # If not np.nan
        blk_randomizer = dat_i['FL_10 - Block Randomizer - Display Order']
    else:
        blk_randomizer = dat_i['FL_23 - Block Randomizer - Display Order']

    if blk_randomizer in ['FL_13|FL_14', 'FL_24|FL_27']:
        ordered_stimuli = stimuli_blk_1 + stimuli_blk_2
    else:
        ordered_stimuli = stimuli_blk_2 + stimuli_blk_1

    # Get ordered psychometric items
    item_randomizer = dat_i['FL_22 - Block Randomizer - Display Order']
    if item_randomizer == 'FL_10':
        ordered_items = list(exp_1_items.keys())
    else:
        ordered_items = list(exp_1_items.keys())[::-1]  # reverse order

    # Extract text
    texts = []
    for stimulus in ordered_stimuli:
        for item in ordered_items:
            choice = dat_i[exp_1_item_temp[item].format(stimulus)]  # Accessing item-stimulus pair
            if isinstance(choice, str):
                choice = choice.split('=')[0]
            texts.append(exp_1_items[item] + stimulus + '. ' + f'<<{int(choice)}>>.')
    text = '\n'.join(texts)
    text = exp_1_instructs + '\n' + text

    # Extracting participant data
    participant = exp + str(participant_i)
    age = dat_i['Age']
    nationality = dat_i['Nationality']

    # Append to all_prompts
    all_prompts.append({
        'text': text,
        'participant': participant,
        'age': age,
        'nationality': nationality,
        'experiment': exp,
    })


##################### Extract Risk Rating Prompts (Experiment 2) #####################

# Load the risk choice data (ratings on 1 dimension: risk)
exp_2 = pd.read_csv('risk_individual.csv')
exp = 'riskRatings'

# Define high-level prompt components
exp_2_instructs = 'This study aims to investigate how people perceive various potential sources of risk.\n'
exp_2_item = 'On a scale from -100 (Safe) to 100 (Risky), how risky is the following?: '

# Iterate over participants to generate prompts
for participant_i in range(len(exp_2)):
    dat_i = exp_2.iloc[participant_i]

    # Get ordered stimuli
    stimuli_blk_1 = dat_i['Multi-Choice Hack 1 - Display Order'].split('|')
    stimuli_blk_2 = dat_i['Multi-Choice Hack 2 - Display Order'].split('|')
    blk_randomizer = dat_i['FL_26 - Block Randomizer - Display Order']
    if blk_randomizer == 'FL_47|FL_48':
        ordered_stimuli = stimuli_blk_1 + stimuli_blk_2
    else:
        ordered_stimuli = stimuli_blk_2 + stimuli_blk_1

    # Extract text and RT data
    texts, RTs = [], []
    for stimulus in ordered_stimuli:
        choice = dat_i[
            f'[Field-counter] / 100 Questions Complete   How safe or risky is the following?:    [Field-1] - {stimulus} - 1'
        ]
        RT = dat_i[f'Timing - {stimulus} - Timing - Page Submit']
        texts.append(exp_2_item + stimulus + '. ' + f'<<{int(choice)}>>.')
        RTs.append(float(RT) * 1000)    # Convert from s to ms
    text = '\n'.join(texts)  # Joining each line
    text = exp_2_instructs + '\n' + text

    # Extract participant data
    participant = exp + str(participant_i)
    age = dat_i['Age']
    nationality = dat_i['Nationality']

    # Append to all_prompts
    all_prompts.append({
        'text': text,
        'participant': participant,
        'RTs': RTs,
        'age': age,
        'nationality': nationality,
        'experiment': exp,
    })

##################### Save Prompts to JSONL File #####################

# Print the number of participants (lines)
print(f"Number of participants: {len(all_prompts)}")

# Print the number of choices
print("Number of choices: ", sum([prompt['text'].count("<<") for prompt in all_prompts]))

# Save all_prompts to a JSONL file
with open("prompts.jsonl", "w", encoding="utf-8") as f:
    for prompt in all_prompts:
        json.dump(prompt, f, ensure_ascii=False)
        f.write("\n")

# Compress the JSONL file into a ZIP file
with zipfile.ZipFile("prompts.jsonl.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("prompts.jsonl")