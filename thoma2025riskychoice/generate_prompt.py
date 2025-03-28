import numpy as np
import pandas as pd
import jsonlines

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

all_prompts = []
df = pd.read_csv('data_thoma_et_al_2025.csv')


instr_repeated = "In this experiment, we will ask you to make ten predictions in the same funfair game. Only at the end of the task you will find out how often you made correct and incorrect predictions. \n" \
    "In each trial, you will be presented with ten objects. Seven objects are marked with one letter, three objects are marked with a different letter. \n" \
    "The letters disappear, the objects will be shuffled, and one of them is randomly drawn. \n" \
    "You will be then presented with a choice between the two letter markings. Which letter marking does the randomly drawn object have?\n" \
    "After each choice, you will move on to the next trial until you made all ten predictions.\n" \
    "Please try to make as many correct predictions as you can.\n" \

instr_unique = "In this experiment, we will ask you to make ten predictions in ten different funfair games. Only at the end of the task you will find out how often you made correct and incorrect predictions." \
    "In each trial, you will be presented with ten objects. Seven objects are marked with one letter, three objects are marked with a different letter. \n" \
    "The letters disappear, the objects will be shuffled, and one of them is randomly drawn. \n" \
    "You will be then presented with a choice between the two letter markings. Which letter marking does the randomly drawn object have?\n" \
    "After each choice, you will move on to the next trial until you made all ten predictions.\n" \
    "Please try to make as many correct predictions as you can.\n" \

num_trials = df.trial.max()
colors = ["red", "black", "blue", "pink", "purple", "green", "brown", "orange", "yellow", "white"]
color_mapping = dict(zip(colors, randomized_choice_options(len(colors))))

for participant in df['id'].unique():
    df_participant = df[df['id'] == participant]
    age = df_participant.age.iloc[0]
    cond = df_participant.cond.iloc[0]
    gender = df_participant.gender.iloc[0]
    choice_options = randomized_choice_options(2)

    if cond == "unique": 
        prompt = instr_unique
    else:
        prompt = instr_repeated
    

    for trial in range(1, num_trials):  # Ensure trials start at 1
        df_trial = df_participant[df_participant['trial'] == trial]
        if df_trial.empty:
            continue
                
        game = df_trial.game.iloc[0]
        highColor = color_mapping[df_trial.highColor.iloc[0]]
        lowColor = color_mapping[df_trial.lowColor.iloc[0]]
        lowLoc = df_trial.lowLoc.iloc[0]
        highLoc = df_trial.highLoc.iloc[0]
        choice = color_mapping[df_trial.choice.iloc[0]]
                        
        if game == "Cards":
            prompt += "You are presented with a deck of ten cards.\n"
            if highLoc == "left":
                prompt += f"Seven cards are marked '{highColor}' and three cards are marked '{lowColor}'. One card is randomly drawn. Is the randomly drawn card marked '{highColor}' or marked '{lowColor}'? You predict <<{choice}>>.\n"
            elif highLoc == "right":
                prompt += f"Three cards are marked '{lowColor}' and seven cards are marked '{highColor}'. One card is randomly drawn. Is the randomly drawn card marked '{lowColor}' or marked '{highColor}'? You predict <<{choice}>>.\n"
        elif game == "Sticks":
            prompt += "You are presented with ten small sticks in a container.\n"
            if highLoc == "left":
                prompt += f"Seven sticks are marked '{highColor}' and three sticks are marked '{lowColor}'. One stick is randomly drawn. Is the randomly drawn stick marked '{highColor}' or marked '{lowColor}'? You predict <<{choice}>>.\n"
            elif highLoc == "right":
                prompt += f"Three sticks are marked '{lowColor}' and seven sticks are marked '{highColor}'. One stick is randomly drawn. Is the randomly drawn stick marked '{lowColor}' or marked '{highColor}'? You predict <<{choice}>>.\n"
        elif game == "Bingo":
            prompt += "You are presented with ten balls in a bingo machine.\n"
            if highLoc == "left":
                prompt += f"Seven balls are marked '{highColor}' and three balls are marked '{lowColor}'. One ball is randomly drawn. Is the randomly drawn ball marked '{highColor}' or marked '{lowColor}'? You predict <<{choice}>>.\n"
            elif highLoc == "right":
                prompt += f"Three balls are marked '{lowColor}' and seven balls are marked '{highColor}'. One ball is randomly drawn. Is the randomly drawn ball marked '{lowColor}' or marked '{highColor}'? You predict <<{choice}>>.\n"
        elif game == "Coins":
            prompt += "You are presented with ten coins in a bag.\n"
            if highLoc == "left":
                prompt += f"Seven coins are marked '{highColor}' and three coins are marked '{lowColor}'. One coin is randomly drawn. Is the randomly drawn coin marked '{highColor}' or marked '{lowColor}'? You predict <<{choice}>>.\n"
            elif highLoc == "right":
                prompt += f"Three coins are marked '{lowColor}' and seven coins are marked '{highColor}'. One coin is randomly drawn. Is the randomly drawn coin marked '{lowColor}' or marked '{highColor}'? You predict <<{choice}>>.\n"
        elif game == "Wheel":
            prompt += "You are presented with a wheel of fortune with ten sections.\n"
            if highLoc == "left":
                prompt += f"Seven sections are marked '{highColor}' and three sections are marked '{lowColor}'. The wheel is spun. Is the section that the wheel stops on marked '{highColor}' or marked '{lowColor}'? You predict <<{choice}>>.\n"
            elif highLoc == "right":
                prompt += f"Three sections are marked '{lowColor}' and seven sections are marked '{highColor}'. The wheel is spun. Is the section that the wheel stops on marked '{lowColor}' or marked '{highColor}'? You predict <<{choice}>>.\n"

    all_prompts.append({
        'text': prompt,
        'experiment': 'Thoma_et_al_2025_risky_choice',
        'participant': str(participant),
        'age': str(age),
        'gender': str(gender),
        'condition': str(cond)
    })
    

print(all_prompts)
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)