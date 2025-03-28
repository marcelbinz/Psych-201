import numpy as np
import pandas as pd
import math as math
import jsonlines
import sys
sys.path.append(".")
from utils import randomized_choice_options

all_prompts = []
df = pd.read_csv('data/nussenbaum_twostep.csv')

#count number of unique participants
num_participants = df.subject_id.max()

for participant in range(num_participants):
    df_participant = df[(df['subject_id'] == participant + 1)]
    age = df_participant.age.iloc[0]
    num_trials = len(df_participant)
    all_choices = randomized_choice_options(num_choices=8)
    stage1_choice_options = all_choices[0:2] 
    stage2_choice_options = all_choices[2:4] 
    stage2_aliens = all_choices[4:8]

    prompt = 'In this game, you will be taking a spaceship from earth to look for space treasure on two different planets. \n'
    prompt += 'Each planet has two aliens on it. And each alien has its own space treasure mine. \n'
    prompt += 'On each planet, you will pick one alien to ask for space treasure. These aliens are nice, so if an alien just brought treasure up from the mine, it will share it with you. \n'
    prompt += 'For each choice, choose one alien by pressing the ' + stage2_choice_options[0] + ' key and the other alien by pressing the' + stage2_choice_options[1] +  'key. The choice you make will be highlighted. \n'
    prompt += 'After you choose an alien, you will find out whether you got treasure. \n'
    prompt += 'If the alien couldn\'t bring treasure up this time you\'ll see an empty circle. \n'
    prompt += 'If an alien has a good mine that means it can easily dig up space treasure and it will be very likely to have some to share.\n'
    prompt += 'It might not have treasure EVERY time you ask, but it will most of the time. Another alien might have a bad mine that is hard to dig through at the moment, and won\'t have treasure to share most times you ask. \n'
    prompt += 'Every alien has treasure in its mine, but they can\'t share every time. Some will be more likely to share because it is easier to dig right now.\n'
    prompt += 'Which side an alien appears on does not matter. For instance, left is not luckier than right. \n'
    prompt += 'Each alien is like a game of chance, you can never be sure but you can guess. \n'
    prompt += 'The treasure an alien can give will change during the game. \n'
    prompt += 'Those with a good mine might get to a part of the mine that is hard to dig. Those with little to share might find easier treasure to dig. Any changes in an alien\'s mine will happen slowly, so try to focus to get as much treasure as possible. \n'
    prompt += 'While the chance an alien has treasure to share changes over time, it changes slowly. So an alien with a good treasure mine right now will stay good for a while. To find the alien with the best mine at each point in time, you must concentrate. \n'
    prompt += 'Now that you know how to pick aliens, you can learn to play the whole game. You will travel from earth to one of two planets. \n'
    prompt += 'First you need to choose which spaceship to take. The spaceships can fly to either planet, but one will fly mostly to the green planet, and the other mostly to the yellow planet. \n'
    prompt += 'For each choice, choose one spaceship by pressing the ' + stage1_choice_options[0] + ' key and the other spaceship by pressing the' + stage1_choice_options[1] +  'key.  \n'
    prompt += 'The planet a spaceship goes to most won\'t change during the game. Pick the one that you think will take you to the alien with the best mine, but remember, sometimes you\'ll go to the other planet! \n'
    prompt += 'Remember, you want to find as much space treasure as you can by asking an alien to share with you. \n'
    prompt += 'The aliens share somewhat randomly, but you can find the one with the best mine at any point in the game by asking it to share! \n'
    prompt += 'How much bonus money you make is based on how much space treasure you find. \n'
    prompt += 'You will have three seconds to make each choice. If you are too slow, you will see a large X appear on each rocket or alien and that choice will be over. \n'
    prompt += 'Don\'t feel rushed, but please try to make a choice every time. \n'
    prompt += 'The game is hard, so you will need to concentrate, but don\'t be afraid to trust your instincts. Here are three hints on how to play the game. \n'
    prompt += 'Hint 1: Remember which aliens have treasure. How good a mine is changes slowly, so an alien that has a lot of treasure to share now will probably be able to share a lot in the near future. \n'
    prompt += 'Hint 2: Remember, each alien has its own mine.  Just because one alien has a bad mine and can\'t share very often, does not mean another has a good mine. Also, there are no funny patterns in how an alien shares, like every other time you ask, or depending on which spaceship you took. The aliens are not trying to trick you. \n'
    prompt += 'Hint 3: The spaceship you choose is important because often an alien on one planet may be better than the ones on another planet. You can find more treasure by finding the spaceship that is most likely to take you to right planet. \n'
    prompt += 'Ready?  Now its time to play the game!  Good luck space traveler! \n'
 
    for trial in range(num_trials):
        df_trial = df_participant.iloc[trial]
        
        #convert to integers    
        c1 = df_trial.c1.item()
        state = df_trial.s.item()
        c2 = df_trial.c2.item()
        reward = df_trial.r.item()
        
        if state == 0: 
            if c2 == 0:
                alien_choice = 0
            else:
                alien_choice = 1
        else: 
            if c2 == 0:
                alien_choice = 2
            else:
                alien_choice = 3
                
        if not isinstance(c1, (int, float)) or (isinstance(c1, float) and math.isnan(c1)):
            prompt += 'You were too slow to select a spaceship. \n'
        elif not isinstance(state, (int, float)) or (isinstance(state, float) and math.isnan(state)): 
            c1 = int(c1)
            prompt += 'You press <<' + stage1_choice_options[c1] + '>> but you were too slow to select a spaceship so you did not see the planet you arrived at. \n'
        else:
            c1 = int(c1)
            prompt += 'You press <<' + stage1_choice_options[c1] + '>> and arrive at planet ' + str(int(state)) + '.' + '\n'
            
        if not isinstance(c2, (int, float)) or (isinstance(c2, float) and math.isnan(c2)):
            prompt += 'You were too slow to select an alien. \n'
        else:
            c2 = int(c2)
            prompt += 'You press <<' + stage2_choice_options[c2] + '>> to ask alien ' + stage2_aliens[alien_choice] + ' for space treasure. \n'
        
        if not isinstance(reward, (int, float)) or (isinstance(reward, float) and math.isnan(reward)):
            prompt += 'You were too slow to select an alien so you did not see the treasure you received. \n'
        else:
            reward = int(reward)
            prompt += 'The alien gives you ' + str(reward) + ' treasure. \n'
        
    prompt = prompt[:-2]
    print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'nussenbaum2020twostep', 'participant': int(participant), 'age': float(age)})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)