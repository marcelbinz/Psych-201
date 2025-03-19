import pandas as pd
import jsonlines

datasets = ["choices_diagno.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    
    # Process each participant separately
    for participant_id in df['ID'].unique():
        df_participant = df[df['ID'] == participant_id].copy()
        diagnosis = df_participant['diag'].iloc[0]
        
        # Define a mapping for renaming choices: CSV "R1" becomes "L", "R2" becomes "R"
        mapping = {"R1": "L", "R2": "R"}
        
        # Build the header/instruction text
        prompt = "In this task, you have to choose between two options: L and R.\n"
        prompt += "Each choice is associated with a probability of earning a food reward.\n"
        prompt += "If the choice is rewarded, the button you selected will turn green, if not rewarded, a grey circle will appear on the screen.\n"
        prompt += "The task consists of 12 blocks, each lasting 40 seconds. You can complete as many trials as possible within each block.\n\n"
        
        # Process each row (each trial) of the participant's data (block info is not printed)
        for idx, row in df_participant.iterrows():
            trial = row['trial']
            original_choice = row['choice']  # e.g., "R1" or "R2"
            # Map the original choice to the new label ("L" or "R")
            renamed_choice = mapping.get(original_choice, original_choice)
            reward_val = row['reward']
            
            prompt += f"Trial {trial}: "
            if reward_val == 0:
                prompt += f"You pressed <<{renamed_choice}>> and received a food reward.\n"
            elif reward_val == 1:
                prompt += f"You pressed <<{renamed_choice}>> and received no food reward.\n"
            else:
                prompt += f"You pressed <<{renamed_choice}>> and received an unknown outcome.\n"
        
        record = {
            "text": prompt,
            "experiment": "dezfouli/" + dataset,
            "participant": str(participant_id),
            "diagnosis": diagnosis
        }
        all_prompts.append(record)

with jsonlines.open("prompts.jsonl", mode="w") as writer:
    writer.write_all(all_prompts)

print("Done!")
