import numpy as np
import pandas as pd
import jsonlines
import sys
import zipfile
sys.path.append("..")
#from utils import randomized_choice_options

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

dataset = "zika2023_df.csv"
all_prompts = []


df = pd.read_csv(dataset)
#df = df[df["study_str"] == "study_3"]
df = df[df["Subjective_Probability"] <= 1] #filter out invalid probabilities
print(df["Subjective_Probability"].isna().sum())
print(df["Response_Time"].isna().sum())

print(df["Subjective_Probability"].isnull().sum())
print(df["Response_Time"].isnull().sum())
print(pd.unique(df["Trial_Type"]))




for participant in df['id'].unique():
    participant_mask = df["id"] == participant
    df_participant = df[(df['id'] == participant)]
    RTs = []
    reversal_prob = []
    learning_phase = []



    choice_options = randomized_choice_options(num_choices=3)

    prompt = ( "In this task, you have to indicate the probability of receiving a painful electric shock after having seen a cue.\n"\
               "There are three distinct cues and each cue is associated with a different probability of receiving a shock.\n"\
               "The cues are labeled as follows: " + choice_options[0] + ', ' + choice_options[1] + ', ' + choice_options[2] + "\n"\
                "Pay attention to all cues as they may or may not change their probability signaling the painful electric shock.\n"\
                "Note that your rating has no influence on outcome probabilities\n")

    for _, row in df_participant.iterrows():
        probability = row["Subjective_Probability"]
        if row["Outcome_Type"] == 0:
            shock_str = "no shock"
        elif row["Outcome_Type"] == 1:
            shock_str = "a shock"
        if row["Trial_Type"] == 1:
            cue = choice_options[0]
        elif row["Trial_Type"] == 2:
            cue = choice_options[1]
        elif row["Trial_Type"] == 3:
            cue = choice_options[2]
        prompt += ('You are presented with cue ' + str(cue) + '. You indicate a probability of receiving a shock of <<' + str(probability) +
                   '>> and you receive ' + shock_str + '.\n' )\

        RTs.append(row["Response_Time"]*1000) #convert to ms
        reversal_prob.append(row["Reversl_Prob"])
        learning_phase.append(row["Learning_Phase"])
    #print(len(RTs) == len(learning_phase))


    prompt += '\n'

    prompt = prompt[:-2]

    all_prompts.append({'text': prompt,
                        'experiment': dataset,
                        'participant': str(participant),
                        'RTs': RTs,
                        'reversal_prob': reversal_prob,
                        'learning_phase': learning_phase
                        })
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
with zipfile.ZipFile('prompts.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('prompts.jsonl')