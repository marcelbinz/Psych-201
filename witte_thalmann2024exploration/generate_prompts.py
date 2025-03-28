import numpy as np
import pandas as pd
import jsonlines
from utils import randomized_choice_options

data_path = "/Users/kristinwitte/Documents/GitHub/exploration-psychometrics/data"

datasets = ["fullHorizon.csv", "full2AB.csv", 'fullRestless.csv']

orders = pd.read_csv(data_path + '/orders.csv')

horizon = pd.read_csv(data_path + '/fullHorizon.csv')
IDs = set(horizon["ID"])
NblocksH = len(horizon["block"].unique())

sam = pd.read_csv(data_path + '/full2AB.csv')
NblocksS = len(sam["block"].unique())

restless = pd.read_csv(data_path + '/fullRestless.csv')

horizon_instr = "In this game, you will choose between two slot machines that give different average rewards.\n" \
    "The average rewards for each machine stay the same within a round, but some noise is added. This means that if you play a slot machine several times, you will get approximately the same reward each time.\n"\
    "At the start of each round, the computer will make 4 pre-determined choices for you. After these 4 intial pre-determined choices, you get to make either 1 or 6 free choices. " \
    "You will be told whether you are in a 'Short round' when you can only make one free choice or in a 'Long round' when you can make 6 free choices. \n"\
    "You will play " + str(NblocksH)+" rounds of this game. And as always, when a new round starts, you get new slot machines with new rewards that you need to learn again.\n"

sam_instr = "In this game you will choose between two slot machines that give different average rewards. \n"\
    "Sometimes, the average rewards for one or both of the machines changes over time. You can choose either machine at any time. Try to get as many points as possible.\n"\
    "You will play "+ str(NblocksS)+ " rounds of this game consisting of 10 choices each.\n" \
    "As always, when a new round starts, you get new slot machines and need to learn their rewards again.\n"

restless_instr = "In this game you will choose between four slot machines that give different average rewards. Importantly, the average reward of each slot machine changes over time. \n"\
    "Thus, a slot machine that gives low rewards at first can give high rewards later on and vice-versa. You can choose any machine at any time. In this game, you will only play one round consisting of 200 choices.\n" 

def get_horizon_prompt(ID, session, choice_options):
    horizon_str = horizon_instr

    dat = horizon.loc[(horizon["ID"] == ID) & (horizon["session"] == session)]
    for block in range(1, NblocksH+1):
        block_dat = dat.loc[dat["block"] == block]
        horizon_str += "Round " + str(block) + " of " + str(NblocksH) + ".\n"

        if block_dat["Horizon"].unique() == 5:
            horizon_str += "Short round: You can make 1 free choice. \n"
            ntrials = 5

        else:
            horizon_str += "Long round: You can make 6 free choices. \n"
            ntrials = 10

        for trial in range(1,5):# fixed choices
            chosen = np.int64(block_dat.loc[block_dat["trial"] == trial, "chosen"].item())
            horizon_str += "On trial " + str(trial) + " of "+ str(ntrials) + " the computer picked slot machine " + str(choice_options[chosen]) + " and you got " + str(np.int64(block_dat.loc[block_dat["trial"] == trial, "reward"].item())) + " points.\n"

        horizon_str += "End of the predetermined choices. You can now make " + str(ntrials-4) + " free choice(s).\n"

        for trial in range(5,(ntrials+1)):# free choice(s)
            chosen = np.int64(block_dat.loc[block_dat["trial"] == trial, "chosen"].item())
            horizon_str += "On trial " + str(trial) + " of "+ str(ntrials) + " you picked slot machine <<" + str(choice_options[chosen]) + ">> and got " + str(np.int64(block_dat.loc[block_dat["trial"] == trial, "reward"].item())) + " points.\n"

        horizon_str += "End of the round.\n"

    return horizon_str

#get_horizon_prompt(2,1)

def get_sam_prompt(ID, session, choice_options):
    
    sam_str = sam_instr

    dat = sam.loc[(sam["ID"] == ID) & (sam["session"] == session)]

    for block in range(1, NblocksS+1):

        block_dat = dat.loc[dat["block"] == block]
        sam_str += "Round " + str(block) + " of " + str(NblocksS) + ".\n"

        for trial in range(1,11):
            chosen = np.int64(block_dat.loc[block_dat["trial"] == trial, "chosen"].item())
            sam_str += "On trial " + str(trial) + " of "+ str(10) + " you picked slot machine <<" + str(choice_options[chosen]) + ">> and got " + str(np.int64(block_dat.loc[block_dat["trial"] == trial, "reward"].item())) + " points.\n"

        sam_str += "End of the round.\n"

    return sam_str

#get_sam_prompt(2,1)

def get_restless_prompt(ID, session, choice_options):
    
    restless_str = restless_instr

    dat = restless.loc[(restless["ID"] == ID) & (restless["session"] == session)]

    for trial in range(1, 201):
        chosen = np.int64(dat.loc[dat["trial"] == trial, "chosen"].item())
        restless_str += "On trial " + str(trial) + " of 200 you picked slot machine <<" + str(choice_options[chosen]) + ">> and got " + str(np.int64(dat.loc[dat["trial"] == trial, "reward"].item())) + " points.\n"

    return restless_str


#get_restless_prompt(2,1)


all_prompts = []


for ID in IDs:
#for ID in [2]:
    choice_options = randomized_choice_options(num_choices=4)

    for session in [1,2]:

        if session == 1:
            prompt = "This study consists of two sessions. This means that you will participate in one study session today and then repeat the second study session in 6 weeks time. \n"\
            "In each session, you will play three casino games. In these casino games, you will have to choose between playing different slot machines across a series of rounds. Each slot machine gives you a different average reward.\n"\
            "Your goal is to earn as many points as possible. You will play 3 different games. Each game consists of several rounds, in which the slot machines have different rewards. Thus, if a new round starts, the average rewards of the slot machines have changed and you need to learn them again! \n"

        else:
            prompt += "Welcome back to the second session of the study. 6 weeks have passed. You will now repeat the experiment you did in the first session. \n"

        order = orders.loc[orders["ID"] == ID, "order"].item()
        
        if order == 1:
            tasks = ["horizon", "sam", "restless"]
        elif order == 2:
            tasks = ["horizon", "restless", "sam"]
        elif order == 3:
            tasks = ["sam", "horizon", "restless"]
        elif order == 4:
            tasks = ["sam", "restless", "horizon"]
        elif order == 5:
            tasks = ["restless", "horizon", "sam"]
        elif order == 6:
            tasks = ["restless", "sam", "horizon"]


        # get choices for all the tasks
        for ind, task in enumerate(tasks):
            if task == "horizon":
                txt = get_horizon_prompt(ID, session, choice_options)
                prompt += txt
            elif task == "sam":
                txt = get_sam_prompt(ID, session, choice_options)
                prompt += txt
            elif task == "restless":
                txt = get_restless_prompt(ID, session, choice_options)
                prompt += txt
            
            if ind < 2:
                prompt += "End of game number " + str(ind+1) + ". You will now move on to the next game.\n"

            else:
                prompt += "End of the casino games."


    #print(prompt)
    all_prompts.append({'text': prompt, 'experiment': 'witte_thalmann2024exploration/', 'participant': ID})

with jsonlines.open('witte_thalmann2024exploration/prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
