import math
import numpy as np
import pandas as pd
import jsonlines
from tqdm import tqdm
import sys
sys.path.append("..")
from utils import randomized_choice_options

role2txt = {
    "Person": ["person", "people", "a person", ],
    "Woman": ["woman", "women", "a woman", ],
    "Man": ["man", "men", "a man", ],
    "Stroller": ["stroller", "strollers", "a stroller", ],
    "Girl": ["girl", "girls", "a girl", ],
    "Boy": ["boy", "boys", "a boy", ],
    "Pregnant": ["pregnant woman", "pregnant women", "a pregnant woman", ],
    "OldWoman": ["elderly woman", "elderly women", "an elderly woman", ],
    "OldMan": ["elderly man", "elderly men", "an elderly man", ],
    "LargeWoman": ["large woman", "large women", "a large woman", ],
    "LargeMan": ["large man", "large men", "a large man", ],
    "FemaleAthlete": ["female athlete", "female athletes", "a female athlete", ],
    "MaleAthlete": ["male athlete", "male athletes", "a male athlete", ],
    "Executive": ["executive", "executives", "an executive"],
    "FemaleExecutive": ["female executive", "female executives", "a female executive", ],
    "MaleExecutive": ["male executive", "male executives", "a male executive", ],
    "FemaleDoctor": ["female doctor", "female doctors", "a female doctor", ],
    "MaleDoctor": ["male doctor", "male doctors", "a male doctor", ],
    "Homeless": ["homeless person", "homeless people", "a homeless person", ],
    "Criminal": ["criminal", "criminals", "a criminal", ],
    "Dog": ["dog", "dogs", "a dog", ],
    "Cat": ["cat", "cats", "a cat", ],
    "Animal": ["animal", "animals", "a animal", ],
}

cnt2txt = 'zero one two three four five six seven eight nine ten'.split()

def verbalize_cnt_and_role(cnt, role, cnt_en=True):
    if cnt == 1:
        expression = role2txt[role][-1]
    else:
        role_en = role2txt[role][1]
        if cnt_en:
            # cnt_str = self.inflect_engine.number_to_words(cnt)
            cnt_str = cnt2txt[cnt]
        else:
            cnt_str = str(cnt)
        sep = ' '
        expression = sep.join([cnt_str, role_en])
    return expression

def verbalize_a_list(ls, and_word=True):
    if and_word:
        if len(ls) > 1:
            ls[-1] = 'and ' + ls[-1]
    expr = ', '.join(ls)
    return expr

def text_based_problem(df_trial, choice_options):
    choice = df_trial.iloc[0]['Saved'].item()

    full_str = ''

    categories = ["Man", "Woman", "OldMan", "OldWoman", "Pregnant", "Stroller", "Boy", "Girl",
              "Homeless", "LargeWoman", "LargeMan", "Criminal", "MaleExecutive", "FemaleExecutive", "FemaleAthlete",
              "MaleAthlete", "FemaleDoctor", "MaleDoctor", "Dog", "Cat"]

    for row in [0, 1]:
        # get people dying in this outcome
        try:
            people = df_trial.iloc[row][categories].astype(float).astype(int)
        except:
            return None
        role_and_cnts = people.to_dict()
        role_and_cnts = {k: v for k, v in role_and_cnts.items() if v}
        role_and_cnts = sorted(role_and_cnts.items(), key=lambda i: list(role2txt).index(i[0]))
        exprs = [verbalize_cnt_and_role(cnt, role) for role, cnt in role_and_cnts]
        dead_str = verbalize_a_list(exprs)

        type_dead_str = 'passenger' if df_trial.iloc[row]['Barrier'] == 1 else 'pedestrian'
        intervention_str = 'swerve' if df_trial.iloc[row]['Intervention'] == 1 else 'continue ahead'

        if df_trial.iloc[row]['Barrier'] == 1:
            barrier_str = 'crash into a concrete barrier'
        else:
            if df_trial.iloc[row]['Intervention'] == 1:
                barrier_str = 'drive through a pedestrian crossing in the other lane'
            else:
                barrier_str = 'drive through a pedestrian crossing ahead'

        outcome = 'Outcome ' + choice_options[row] + ': In this case, the self-driving car with a sudden brake failure will ' + intervention_str + ' and ' + barrier_str + '. This will result in the following ' + type_dead_str + ' deaths: ' + dead_str + '.'
        if df_trial.iloc[row]['CrossingSignal'] == 1:
            outcome += ' Note that the affected pedestrians are abiding by the law by crossing on the green signal.'
        elif df_trial.iloc[row]['CrossingSignal'] == 2:
            outcome += ' Note that the affected pedestrians are flouting the law by crossing on the red signal.'
        outcome += '\n'
        full_str += outcome

    return full_str + 'You select outcome <<' + choice_options[choice] + '>>.\n\n'

all_prompts = []

# get only first full sessions
first_session_ids = pd.read_csv('SharedResponsesFullFirstSessions.csv')['ExtendedSessionID'].unique()
df = pd.read_csv('SharedResponses.csv')
df_subset = df[df.ExtendedSessionID.isin(first_session_ids.tolist())]

# get only USA
df_subset = df_subset[df_subset['UserCountry3'] == 'USA']
print(len(df_subset))

grouped = df_subset.groupby(['ExtendedSessionID'])

for participant, df_participant in tqdm(grouped):
    choice_options = randomized_choice_options(num_choices=2)
    prompt = 'You are presented with a series of dilemmas in which an autonomous vehicle must decide between two different outcomes.\n' \
        'Your task is to decide what the self-driving car should do.\n' \
        'You can select your chosen outcome by pressing the corresponding button.\n\n'
    for scenario in range(1, df_participant['ScenarioOrder'].max() + 1):
        df_trial = df_participant[df_participant['ScenarioOrder'] == scenario]
        if len(df_trial) == 2:
            trial_prompt = text_based_problem(df_trial, choice_options)
            if trial_prompt is not None:
                prompt += trial_prompt

    prompt = prompt[:-2]
    if "<<" in prompt:
        all_prompts.append({'text': prompt, 'experiment': 'awad2018moral/SharedResponses.csv', 'participant': participant})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
