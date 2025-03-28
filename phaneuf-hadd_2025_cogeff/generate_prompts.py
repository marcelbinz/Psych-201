import pandas as pd
import jsonlines # needed to run in console: pip install jsonlines
import os
print("Current working directory:", os.getcwd())
nd = "/Users/camillephaneuf/Desktop/ANDL/CogEff/phaneuf-hadd_2025_cogeff_PrepSpace/attempt2"
os.chdir(nd)
print("New working directory:", os.getcwd())

# set all prompt shell
all_prompts = []
all_prompts2 = []

# read in data
df = pd.read_csv("study1.csv")
df2 = pd.read_csv("study2.csv")

# get number of participants and trials
num_participants = 150
num_trials = df.trial_num.max() # should be 240

# iterate through participants
for participant in range(num_participants):
    
    # get participant's data
    subid = participant + 1 # subids are 1-150 in study 1
    df_participant = df[(df['participant'] == subid)]
    df_participant.reset_index(drop=True, inplace=True)

    # set instructions, modified from human participants (because of no visuals)
    prompt = 'In this game, you will be asked to sort aliens according to what they look like. Your goal is to describe what the aliens look like as correctly and as quickly as possible. '\
    'Your job is simple. Every time you see an alien, you will need to tell us what color it is OR what pattern is on its stomach. '\
    'If you need to tell us what color the alien is, you will see a blue and orange bar at the top of your screen. Press f for blue; press j for orange. '\
    'If you need to tell us what pattern is on the alien\'s stomach, you will see a striped and solid bar at the top of your screen. Press f for striped; press j for solid. '\
    'Each block, before you see an alien, you will briefly see how much bonus money you can earn for saying the correct color or pattern. If you also say the correct color pattern fast, you will win an extra bonus at the end. '\
    'You can earn 10 cents or 1 cent for each correct choice. You will earn 0 cents for each incorrect choice. '\
    'Each block, before you see an alien, you will briefly see either planets or moons. '\
    'The planets and moons tell you what kind of galaxy the aliens that come after are in. You may notice differences between the planet and moon galaxies.\n\n'

    # set difficulty info in prompt
    dif = "none"

    # iterate through trials
    for trial in range(num_trials):
        
        # get trial number
        trial_temp = trial + 1
        
        # update difficulty info in prompt
        if (trial_temp - 1) % 20 == 0:
            dif = df_participant.iloc[trial]['planet_name']
        else:
            dif = dif
        
        # set reward info in prompt
        rew = df_participant.iloc[trial]['reward']
            
        # set stimulus info in prompt
        typ = df_participant.iloc[trial]['trial_type']
        col = df_participant.iloc[trial]['alien_body_color']
        pat = df_participant.iloc[trial]['alien_stomach_pattern']
        typ_str = "none"
        if typ == "color":
            typ_str = "This is a color trial (the bar at the top of the screen is blue and orange). "
        else:
            typ_str = "This is a pattern trial (the bar at the top of the screen is striped and solid). "
        col_str = "none"
        if col == "blue":
            col_str = "The alien's body is blue. "
        else:
            col_str = "The alien's body is orange. "
        pat_str = "none"
        if pat == "striped":
            pat_str = "The alien's stomach is striped. "
        else:
            pat_str = "The alien's stomach is solid. "
                
        # set response info in prompt
        res = df_participant.iloc[trial]['keyTrial.keys']
        acc = df_participant.iloc[trial]['resp_type']
        if pd.isna(res):
            res = "nothing"
            acc = "too slow"
        else:
            res = res
            acc = acc
            
        # construct prompt
        if (trial_temp - 1) % 20 == 0:
            prompt += 'On the screen, you see ' + dif + 's and a ' + str(rew) + ' cent coin.\n\n'
            prompt += 'Now you are in a ' + dif + ' and ' + str(rew) + ' cent block. ' + typ_str + col_str + pat_str + 'You press <<' + res + '>> to make a ' + acc + ' response.\n\n'
        else:
            prompt += 'You are still in a ' + dif + ' and ' + str(rew) + ' cent block. ' + typ_str + col_str + pat_str + 'You press <<' + res + '>> to make a ' + acc + ' response.\n\n'
        print(prompt)
            
    # get rts and age
    rt_col = df_participant['keyTrial.rt'].tolist()
    age = df_participant.iloc[0]['age']
    
    # append prompt
    all_prompts.append({'text': prompt, 'experiment': 'phaneuf-hadd_2025_cogeff/study1.csv', 'participant': subid, 'RTs': rt_col, 'age': age})
    
# get number of participants and trials
num_participants2 = 150
num_trials2 = df2.trial_num.max() # should be 240

# iterate through participants
for participant in range(num_participants2):
    
    # get participant's data
    subid = participant + 151 # subids are 151-300 in study 2
    df_participant = df2[(df2['participant'] == subid)]
    df_participant.reset_index(drop=True, inplace=True)

    # set instructions, modified from human participants (because of no visuals)
    prompt = 'In this game, you will be asked to sort aliens according to what they look like. Your goal is to describe what the aliens look like as correctly and as quickly as possible. '\
    'Your job is simple. Every time you see an alien, you will need to tell us what color it is OR what pattern is on its stomach. '\
    'If you need to tell us what color the alien is, you will see a blue and orange bar at the top of your screen. Press f for blue; press j for orange. '\
    'If you need to tell us what pattern is on the alien\'s stomach, you will see a striped and solid bar at the top of your screen. Press f for striped; press j for solid. '\
    'Each block, before you see an alien, you will briefly see how much bonus money you can earn for saying the correct color or pattern. If you also say the correct color pattern fast, you will win an extra bonus at the end. '\
    'You can earn 10 cents or 1 cent for each correct choice. You will earn 0 cents for each incorrect choice. '\
    'Each block, before you see an alien, you will briefly see either planets or moons. '\
    'The planets and moons tell you what kind of galaxy the aliens that come after are in. The planet and moon galaxies are different. '\
    'The planet galaxies are easier than the moon galaxies. This means you have to switch between saying the color and pattern a little in the planet galaxies, but you have to switch between saying the color and pattern a lot in the moon galaxies.\n\n'

    # set difficulty info in prompt
    dif = "none"
    
    # iterate through trials
    for trial in range(num_trials2):
        
        # get trial number
        trial_temp = trial + 1

        # update difficulty info in prompt
        if (trial_temp - 1) % 20 == 0:
            dif = df_participant.iloc[trial]['planet_name']
        
        # set reward info in prompt
        rew = df_participant.iloc[trial]['reward']
            
        # set stimulus info in prompt
        typ = df_participant.iloc[trial]['trial_type']
        col = df_participant.iloc[trial]['alien_body_color']
        pat = df_participant.iloc[trial]['alien_stomach_pattern']
        typ_str = "none"
        if typ == "color":
            typ_str = "This is a color trial (the bar at the top of the screen is blue and orange). "
        else:
            typ_str = "This is a pattern trial (the bar at the top of the screen is striped and solid). "
        col_str = "none"
        if col == "blue":
            col_str = "The alien's body is blue. "
        else:
            col_str = "The alien's body is orange. "
        pat_str = "none"
        if pat == "striped":
            pat_str = "The alien's stomach is striped. "
        else:
            pat_str = "The alien's stomach is solid. "
                
        # set response info in prompt
        res = df_participant.iloc[trial]['keyTrial.keys']
        acc = df_participant.iloc[trial]['resp_type']
        if pd.isna(res):
            res = "nothing"
            acc = "too slow"
        else:
            res = res
            acc = acc
            
        # construct prompt
        if (trial_temp - 1) % 20 == 0:
            prompt += 'On the screen, you see ' + dif + 's and a ' + str(rew) + ' cent coin.\n\n'
            prompt += 'Now you are in a ' + dif + ' and ' + str(rew) + ' cent block. ' + typ_str + col_str + pat_str + 'You press <<' + res + '>> to make a ' + acc + ' response.\n\n'
        else:
            prompt += 'You are still in a ' + dif + ' and ' + str(rew) + ' cent block. ' + typ_str + col_str + pat_str + 'You press <<' + res + '>> to make a ' + acc + ' response.\n\n'
        print(prompt)
            
    # get rts and age
    rt_col = df_participant['keyTrial.rt'].tolist()
    age = df_participant.iloc[0]['age']
    
    # append prompt
    all_prompts2.append({'text': prompt, 'experiment': 'phaneuf-hadd_2025_cogeff/study2.csv', 'participant': subid, 'RTs': rt_col, 'age': age})
    
total_prompts = all_prompts + all_prompts2
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(total_prompts)
