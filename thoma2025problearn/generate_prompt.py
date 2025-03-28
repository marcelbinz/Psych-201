import numpy as np
import pandas as pd
import jsonlines

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

all_prompts = []
df = pd.read_csv('behavioral_data.csv')

num_trials = df.trial.max() 

for participant in df['id'].unique():
    df_participant = df[df['id'] == participant]
    age = df_participant.age.iloc[0]
    cond = df_participant.cond.iloc[0]
    gender = df_participant.gender.iloc[0]
    choice_options = randomized_choice_options(2)

    instr_dyn = f"Welcome to the experiment! All animals have escaped from the zoo and are now hiding in the city. We need your help to find them. \n" \
        f"In this experiment you will repeatedly see two houses labeled '{choice_options[0]}' and {choice_options[1]}' and have to predict behind which house an animal will hide next. \n" \
        "In each trial, an animal can hide behind one house, two houses or none. \n" \
        f"You can indicate your choice by tapping on either house '{choice_options[0]}' or house '{choice_options[1]}'.\n" \
        "After each choice, you will receive feedback about where the animal was hiding. You will receive a reward for each correct prediction.\n" \
        "Please try to make as many correct choices as you can.\n"\

    instr_stat = "Welcome to the experiment! All animals have escaped from the zoo and are now hiding in the city. We need your help to find them. \n" \
        f"In this experiment you will repeatedly see two houses labeled '{choice_options[0]}' and {choice_options[1]}' and have to predict behind which house an animal will hide next. \n" \
        "In each trial, an animal hides behind one of the houses. \n" \
        f"You can indicate your choice by tapping on either house '{choice_options[0]}' or house '{choice_options[1]}'.\n" \
        "After each choice, you will receive feedback about where the animal was hiding. You will receive a reward for each correct prediction.\n" \
        "Please try to make as many correct choices as you can.\n" \

    if cond == "ecol_dyn": 
        prompt = instr_dyn
    else:
        prompt = instr_stat
    

    for trial in range(1, num_trials):  # Ensure trials start at 1
        df_trial = df_participant[df_participant['trial'] == trial]
        if df_trial.empty:
            continue
                
        target_left = df_trial.target_left.iloc[0]
        target_right = df_trial.target_right.iloc[0]
        button_pressed = int(df_trial.button_pressed.iloc[0]) 
        correct = df_trial.correct.iloc[0]
                        
        prompt += (
            f"Trial {trial}: You choose house <<{choice_options[button_pressed]}>>. {"At house '" + choice_options[0] + "', there is an animal hiding" if target_left == 1 else "At house '" + choice_options[0] + "', there is no animal hiding"}. {"At house '" + choice_options[1] + "', there is an animal hiding" if target_right == 1 else "At house '" + choice_options[1] + "', there is no animal hiding"}.\n"
            f"Your choice was {'correct and you receive a reward' if correct == 1 else 'incorrect and you do not receive a reward'}.\n"
        )
        
    all_prompts.append({
        'text': prompt,
        'experiment': 'Thoma_et_al_2025_probability_learning',
        'participant': str(participant),
        'age': str(age),
        'gender': str(gender),
        'condition': str(cond)
    })
    

print(all_prompts)
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)