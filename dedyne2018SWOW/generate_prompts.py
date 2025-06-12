import pandas as pd
import jsonlines
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
# Debug print to see where we are
print("Current working directory:", os.getcwd())

# Read the data with explicit separator and encoding
df = pd.read_csv('SWOW-EN.R100.20180827.csv', 
                 sep=',',  # Changed from '\t' to ','
                 on_bad_lines='warn')

# If the above doesn't work, try this alternative:
# df = pd.read_table('example.csv', encoding='utf-8')

# Read instruction text
with open('prompt.txt', 'r') as f:
    instruction_text = f.read().strip()

all_prompts = []

# Use enumeration to create sequential numbers starting at 1
for i, participant_id in enumerate(df['participantID'].unique(), start=0):
    participant_data = df[df['participantID'] == participant_id]
    
    # Start with instructions
    prompt = instruction_text + "\n\n"
    
    # Add each trial
    for _, row in participant_data.iterrows():
        # Start with the cue word
        trial_text = f'The word is "{row["cue"]}". '
        
        # Add responses only if they exist
        if pd.notna(row['R1']):
            trial_text += f'You type: <<{row["R1"]}>>. '
        if pd.notna(row['R2']):
            trial_text += f'You then type: <<{row["R2"]}>>. '
        if pd.notna(row['R3']):
            trial_text += f'You then type: <<{row["R3"]}>>. '
        
        trial_text += '\n'
        prompt += trial_text
    
    # Create prompt object with sequential number instead of participantID
    prompt_obj = {
        'text': prompt.rstrip(),
        'experiment': 'SWOW',
        'participant': i  # Using sequential number instead of participant_id
    }
    
    all_prompts.append(prompt_obj)

# Write to jsonl file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)