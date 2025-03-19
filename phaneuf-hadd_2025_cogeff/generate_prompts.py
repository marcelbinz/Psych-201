import pandas as pd
import jsonlines # needed to run in console: pip install jsonlines
import os
print("Current working directory:", os.getcwd())
nd = "/Users/camillephaneuf/Desktop/ANDL/CogEff/phaneuf-hadd_2025_cogeff_PrepSpace"
os.chdir(nd)
print("New working directory:", os.getcwd())

# set all prompt shell
all_prompts = []
all_prompts2 = []

# read in data
df = pd.read_csv("study1.csv")
df2 = pd.read_csv("study2.csv")

# get number of participants and trials
num_participants = df.participant.max() # should be 150
num_trials = df.trial.max() + 1 # should be 240

# iterate through participants
for participant in range(num_participants):
    
    # get participant's data
    subid = participant + 1
    df_participant = df[(df['participant'] == subid)]

    # set instructions, modified from human participants (because of no visuals)
    prompt = 'In this game, you will be asked to sort aliens according to what they look like. Your goal is to describe what the aliens look like as correctly and as quickly as possible. '\
    'Your job is simple. Every time you see an alien, you will need to tell us what color it is OR what pattern is on its stomach. '\
    'Each block, before you see an alien, you will briefly see how much bonus money you can earn for saying the correct color or pattern. If you also say the correct color pattern fast, you will win an extra bonus at the end. '\
    'You can earn 10 cents or 1 cent for each correct choice. You will earn 0 cents for each incorrect choice. '\
    'Each block, before you see an alien, you will briefly see either planets or moons. '\
    'The planets and moons tell you what kind of galaxy the aliens that come after are in. You may notice differences between the planet and moon galaxies.\n\n'

    # iterate through trials
    for trial in range(num_trials):
        
        # set difficulty info in prompt
        dif = "none"
        if df_participant.iloc[trial]['difficulty'] == "Easy":
            dif = "planet"
        else:
            dif = "moon"
        
        # set reward info in prompt
        rew = df_participant.iloc[trial]['reward']
            
        # set switch info in prompt
        swi = "none"
        if df_participant.iloc[trial]['switch'] == 0:
            swi = "On this trial, you did not switch from the previous color vs. pattern trial type."
        else:
            swi = "On this trial, you did switch from the previous color vs. pattern trial type."
                
        # set response info in prompt
        res = df_participant.iloc[trial]['response']
            
        # construct prompt
        prompt += 'You are in a ' + dif + ' and ' + str(rew) + ' cent block. ' + swi + ' You made a ' + res + ' response.\n\n'
        print(prompt)
            
    # get rts and age
    rt_col = df_participant['RT'].tolist()
    age = df_participant.iloc[0]['age']
    
    # append prompt
    all_prompts.append({'text': prompt, 'experiment': 'phaneuf-hadd_2025_cogeff/study1.csv', 'participant': participant, 'RTs': rt_col, 'age': age})

with jsonlines.open('prompts1.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
    
# get number of participants and trials
num_participants2 = df2.participant.max() # should be 150
num_trials2 = df2.trial.max() + 1 # should be 240

# iterate through participants
for participant in range(num_participants2):
    
    # get participant's data
    subid = participant + 1
    df_participant = df2[(df2['participant'] == subid)]

    # set instructions, modified from human participants (because of no visuals)
    prompt = 'In this game, you will be asked to sort aliens according to what they look like. Your goal is to describe what the aliens look like as correctly and as quickly as possible. '\
    'Your job is simple. Every time you see an alien, you will need to tell us what color it is OR what pattern is on its stomach. '\
    'Each block, before you see an alien, you will briefly see how much bonus money you can earn for saying the correct color or pattern. If you also say the correct color pattern fast, you will win an extra bonus at the end. '\
    'You can earn 10 cents or 1 cent for each correct choice. You will earn 0 cents for each incorrect choice. '\
    'Each block, before you see an alien, you will briefly see either planets or moons. '\
    'The planets and moons tell you what kind of galaxy the aliens that come after are in. The planet and moon galaxies are different. '\
    'The planet galaxies are easier than the moon galaxies. This means you have to switch between saying the color and pattern a little in the planet galaxies, but you have to switch between saying the color and pattern a lot in the moon galaxies.\n\n'

    # iterate through trials
    for trial in range(num_trials2):
        
        # set difficulty info in prompt
        dif = "none"
        if df_participant.iloc[trial]['difficulty'] == "Easy":
            dif = "planet"
        else:
            dif = "moon"
        
        # set reward info in prompt
        rew = df_participant.iloc[trial]['reward']
            
        # set switch info in prompt
        swi = "none"
        if df_participant.iloc[trial]['switch'] == 0:
            swi = "On this trial, you did not switch from the previous color vs. pattern trial type."
        else:
            swi = "On this trial, you did switch from the previous color vs. pattern trial type."
                
        # set response info in prompt
        res = df_participant.iloc[trial]['response']
            
        # construct prompt
        prompt += 'You are in a ' + dif + ' and ' + str(rew) + ' cent block. ' + swi + ' You made a ' + res + ' response.\n\n'
        print(prompt)
            
    # get rts and age
    rt_col = df_participant['RT'].tolist()
    age = df_participant.iloc[0]['age']
    
    # append prompt
    all_prompts2.append({'text': prompt, 'experiment': 'phaneuf-hadd_2025_cogeff/study2.csv', 'participant': participant, 'RTs': rt_col, 'age': age})

with jsonlines.open('prompts2.jsonl', 'w') as writer:
    writer.write_all(all_prompts2)
