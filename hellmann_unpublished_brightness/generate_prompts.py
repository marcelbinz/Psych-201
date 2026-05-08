import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")

dataset = "data_Hellmann_unpublished_LuMagConf.csv"
all_prompts = []

df = pd.read_csv(dataset)
print(df)

num_trials = df.trial.max() + 1


for participant in df['participant'].unique():
    RTs = []

    df_participant = df[(df['participant'] == participant)]
    age = df_participant.age.iloc[0]

    prompt = 'You see two discs in each trial, varying in brightness. Always focus your eyes on the red cross in the center and decide whether the LEFT or the RIGHT disc appears brighter on average. Press the left or right arrow key to choose the respective disc. Try to be as accurate and as fast as possible.\nAfter your response, indicate how confident you are in your decision, on a scale from -1 to 1, by moving the joystick up or down and confirm with the back button.\nWhen you made an error, the word "Error" will briefly appear.\n\n'

    for trial in range(1, num_trials):
        df_trial  = df_participant[(df_participant['trial'] == trial)]
        lum_left  = str(df_trial.lum_left.item())
        lum_right = str(df_trial.lum_right.item())
        correct   = df_trial.correct.item()
        response  = df_trial.response.item()
        conf      = str(df_trial.Rating.item())
        rt1       = df_trial.responseRT.item()
        rt2       = df_trial.RatingRT.item()

        RTs.append(rt1)
        RTs.append(rt2)
        prompt += 'Left disc has brightness '+lum_left+', right disc has brightness '+lum_right+'. '
        prompt += 'You press <<' + response + '>> after '+ str(rt1) +'ms. You rate your confidence with <<'+ conf + '>> after '+str(rt2)+'ms.'
        if correct==-1:
          prompt += ' You see the word "Error"'
        prompt += '\n'

    prompt = prompt[:-2]
    print(prompt)
    #print(RTs)

    all_prompts.append({'text': prompt,
        'experiment': 'hellmann_unpublished_brightness/' + dataset,
        'participant': str(participant),
        'RTs': RTs,
        'age': str(age)
    })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
