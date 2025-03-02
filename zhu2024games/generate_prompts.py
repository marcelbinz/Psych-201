import pickle
import numpy as np
import pandas as pd
import jsonlines

filename = '2p2kgames_individual_level_data.pickle'
with open(filename, 'rb') as f:
    df_ind = pickle.load(f)
    
pIds = np.unique(df_ind.participant_id.values)

def permutate_game_matrix(M, row, col):
    if row==1: # row of the game matrix M has been switched
        M = [M[2], M[3], M[0], M[1], M[6], M[7], M[4], M[5]]
    if col==1: # col of the game matrix M has been switched
        M = [M[1], M[0], M[3], M[2], M[5], M[4], M[7], M[6]]
    return M

all_prompts = []
for pId in pIds: # loop through all participants
    df = df_ind[df_ind.participant_id == pId]
    for tId in range(1,21,1): # loop through all 20 games this paprticipant have played
        M = df[df.trial_id == tId].row_form_matrix.values[0] # game matrix
        row_switch = df[df.trial_id == tId].row_switch.values[0]
        col_switch = df[df.trial_id == tId].col_switch.values[0]
        up_choice = df[df.trial_id == tId].up_choice.values[0]
        
        M_on_screen = permutate_game_matrix(M, row_switch, col_switch) # game matrix displayed on participant's screen
        if row_switch == 1: 
            up_choice = 1-up_choice # rowA=1, rowB=0
        
        prompt = "You've been matched with a new player for a game. You are designated as the 'row player'.\n" +\
        "You can choose between two options: Row A and Row B. Your opponent will simultaneously choose between Column C and Column D.\n" +\
        "Your payoff, and your opponent's payoff, depend on the combination of choices:\n" +\
        f"If you choose Row A and your opponent chooses Column C, you receive {M_on_screen[0]} and your opponent receives {M_on_screen[4]}.\n" +\
        f"If you choose Row A and your opponent chooses Column D, you receive {M_on_screen[1]} and your opponent receives {M_on_screen[5]}.\n" +\
        f"If you choose Row B and your opponent chooses Column C, you receive {M_on_screen[2]} and your opponent receives {M_on_screen[6]}.\n" +\
        f"If you choose Row B and your opponent chooses Column D, you receive {M_on_screen[3]} and your opponent receives {M_on_screen[7]}.\n" +\
        f"You press <<{'Row A' if up_choice==1 else 'Row B'}>>."

        all_prompts.append({'text': prompt, 'experiment': 'zhu2024games', 'participant': int(pId)})
        
print(len(all_prompts))
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)