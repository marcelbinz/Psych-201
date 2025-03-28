# Get the absolute path of the utils script
import sys
import os
utils_dir = os.path.dirname(os.path.abspath("utils.py"))
sys.path.append(utils_dir)

from utils import randomized_choice_options
import pandas as pd
import numpy as np
import jsonlines

# Link to data hosted on GitHub
path = 'https://raw.githubusercontent.com/jpheffne/NC_emotion_classify/refs/heads/main/data/behavioral/'
# Codebook https://github.com/jpheffne/NC_emotion_classify/blob/main/analysis/emo_classify_supp.Rmd


################
# Ultimatum game
################

# Load data
ulg = pd.read_csv(path + "ug_data.csv")

# The study participant rejects the offer if choice 1 and accepts if choice is 0
ulg["decision"] = np.where(ulg["choice"] == 1, "reject", "accept")

# The unfairness variable refers to the amount of money kept by the partner
ulg["keep"] =  ulg["unfairness"]

# Offer from partner ranges from $0.5 (fair) to $0.95 (unfair)
ulg["offer"] = round(1 - ulg["unfairness"], 2)


# Initialize list to store prompts
all_prompts = []

# Get participant IDs
participant_ids = ulg["sub"].unique()

# Iterate over participants
for participant_id in participant_ids:

    # Generate random label for options for each participant
    choice_options = randomized_choice_options(num_choices=2)

    # Instructions for LLM
    instructions = """You will be making real decisions that affect the monetary outcomes of YOURSELF and OTHERS.
    
    You will be playing multiple rounds of a game with DIFFERENT partners every round. 

    Your partner has been allotted $1.00. You will be paired with a different partner each round and your partner has already decided how much of their $1 to offer you. 

    IMPORTANT: Your partner can split their $1 in any amount as long as it is in $0.05 increments. 


    After observing your partner make an offer, you will be asked to determine the final monetary outcome of both your partner and yourself. The two options are labeled below: 
    
    """ + choice_options[0] + """: Accept the proposed offer and keep both you and your partner's money the same. 

    """ + choice_options[1] + """: Reject the offer and decrease both you and your partner's money to zero. 


    Ultimately, you will decide how much money you and your partner actually receive.


    """

    # Get participant's choice 
    choices = ulg[ulg["sub"] == participant_id]

    # Relabel choices with generated label
    choices = choices.copy()
    choices.loc[:, "decision_label"] = np.where(choices["decision"] == "accept", choice_options[0], choice_options[1])


    choices_as_text = ""

    # Iterate over participants' choices
    for _, row in choices.iterrows():

        # Construct prompt for LLM
        choices_as_text += (
            "Your partner keeps $" + str(row["keep"]) + 
            " and gives you $" + str(row["offer"]) + 
            ". You chose option <<"+row["decision_label"] + ">>.\n\n"
        )

    # Append prompt to list
    all_prompts.append({
        'text': instructions + choices_as_text, 
        'experiment': 'heffner2022economicgames/ug_data.csv', 
        'participant': str(participant_id),
    })






###################
# Prisoners dilemma
###################

# Instructions for LLM
instructions = """You will be making REAL decisions that affect the monetary outcomes of YOURSELF and OTHERS.
 
You will be playing multiple rounds of a game with DIFFERENT partners every round. 
Each subsequent interaction will be comprised of an entirely new partner. 
In other words, you will NEVER interact with the same person more than once during this study. 

During each interaction, both you and your partner will be given $1 and asked to make a decision of how much to contribute to the common pool. 
In other words, each player is deciding how much of their $1 to keep for themselves or give to the group. 

IMPORTANT: You and your partner each can split the $1 in any amount as long as it is in $0.10 increments.

Importantly, in each round, all money contributed to the common pool will be multiplied by 1.5x (one and one half).

After all money contributed to the common pool is multipled by 1.5x, this larger sum will be divided equally among you and your partner.

The amount of money that each player receives on each round is thus determined by BOTH people.

You will be shown how much money your partner contributed to the common pool. You will then be asked to decide how much money to contribute to the common pool.


"""

# Load data
prd = pd.read_csv(path + "pd_data.csv")

# Get participant IDs
participant_ids = prd["sub"].unique()

# Iterate over participants
for participant_id in participant_ids:

    # Get participant's choice and reshuffle
    choices = prd[prd["sub"] == participant_id]

    choices_as_text = ""

    # Iterate over participants' choices
    for _, row in choices.iterrows():

        # Construct prompt for LLM
        choices_as_text += (
            # sub_contribution ius the amount of money given to the common good by the subject, ranges from 0 to 1 in increments of 0.1.
            "You chose to contribute $<<" + str(row["sub_contribution"]) + ">>. "
            # partner_contribution is the amount of money given to the common good by their partner, ranges from defection (0) to cooperation (1) in increments of 0.1. 
            "Your partner contributes $" + str(row["partner_contribution"]) + ".\n\n"
        )


    # Append prompt to list
    all_prompts.append({
        'text': instructions + choices_as_text, 
        'experiment': 'heffner2022economicgames/prd_data.csv', 
        'participant': str(participant_id),
    })





###################
# Public goods game
###################


# Instructions for LLM
instructions = """You will participate in a series of interactions where you will be making REAL decisions that affect the monetary outcomes of YOURSELF and OTHERS. 

In each round, you will interact with three other mTurk workers.
Each subsequent interaction will be comprised of an entirely new group of people. 
In other words, you will NEVER interact with the same person more than once during this study. 

During each interaction, each player is given $1 and makes a decision of how much to contribute to the common pool. 
In other words, each player is deciding how much of their $1 to keep for themselves or give to the group. 

Importantly, in each round, all money contributed to the common pool will be multiplied by TWO and then this larger sum will be divided equally among all four players. 
The amount of money that each player receives on every round is thus determined BOTH by whether or not they give their money to the group, as well as by what other players decide to do with their money.

The amount you will get in each round is the sum of the money you received from the common pool and the money you kept for yourself.

You will be shown how much money your partners contributed to the common pool. You will then be asked to decide how much money to contribute to the common pool.


"""

# Load data
pgg = pd.read_csv(path + "pgg_data.csv")

# Get participant IDs
participant_ids = pgg["sub"].unique()

# Iterate over participants
for participant_id in participant_ids:

    # Get participant's choice and reshuffle
    choices = pgg[pgg["sub"] == participant_id]

    choices_as_text = ""

    # Iterate over participants' choices
    for _, row in choices.iterrows():

        # Construct prompt for LLM
        choices_as_text += (
            # The amount of money given to the common good by the subject, ranges from 0 to 1 in increments of 0.1.
            "You chose to contribute $<<" + str(row["sub_contribution"]) + ">>. "
             # partners_contribution is the amount of money given to the common good by their partners (collectively), ranges from defection (0) to cooperation (3) in increments of 0.1.
            "Your partners contribute $" + str(row["partners_contribution"]) + ".\n\n"
 
        )


    # Append prompt to list
    all_prompts.append({
        'text': instructions + choices_as_text, 
        'experiment': 'heffner2022economicgames/pgg_data.csv', 
        'participant': str(participant_id),
    })



#################
# Write json file
#################


# Get the absolute path of this Python script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the prompts.jsonl file in the same directory
filename = os.path.join(script_dir, 'prompts.jsonl')

# Write json file
with jsonlines.open(filename, 'w') as writer:
    writer.write_all(all_prompts)
