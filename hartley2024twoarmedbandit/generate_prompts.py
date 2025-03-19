import numpy as np
import pandas as pd
import json
import jsonlines
import sys
from tqdm import tqdm
sys.path.append("..")

datasets = ["exp1.csv", "exp2.csv"]
demographic_datasets = ["voc_sub_info_1.csv", "voc_sub_info_2.csv"]
all_prompts = []
dataset = "exp1.csv"

df1 = pd.read_csv(datasets[0])
df2 = pd.read_csv(datasets[1])


df_info1 = pd.read_csv(demographic_datasets[0])
df_info2 = pd.read_csv(demographic_datasets[1])
df_info2["subID"] = (df_info2["subject_id"]).astype(str)

df_bandit_names = pd.DataFrame( {
    "color": ["purple/red", "orange/blue", "green/pink"],
    "condition": df1["condition"].unique()
} )

df_colors = pd.DataFrame({
    "hex": ["#D8271C", "#3386FF", "#D89F1C", "#1CD855", "#FA92F8", "#741CD8"],
    "color": ["purple/red", "orange/blue", "orange/blue", "green/pink", "green/pink", "purple/red"]
})

df_location_1 = pd.DataFrame({
    "leftBandit": ['bandit50a', 'bandit50b', 'bandit70', 'bandit30', 'bandit90', 'bandit10'],
    "arcade_color_L": ["#741CD8", "#D8271C", "#D89F1C", "#3386FF", "#1CD855", "#FA92F8"],
    "color_left": ["purple", "red", "orange", "blue", "green", "pink"]
})

cols_required = [
    "subID", "trial", "color", "agency", "banditResp", 
    "reward", "tokenOffer", "tokensEarned",
    "agencyRT", "banditRT", "color_left"
]

df1 = df1.merge(df_bandit_names, how = "left", on = "condition")
df2 = df2.merge(df_colors, how = "left", left_on = "arcade_color_L", right_on = "hex")
df1 = df1.merge(df_location_1, how = "left", on = "leftBandit")
df2 = df2.merge(df_location_1, how = "left", on = "arcade_color_L")
df2.rename(columns={"color_x": "color_L", "color_y": "color_R"}, inplace=True)
df2["agency"] = df2["stage_1_choice"]
df2["banditResp"] = df2["stage_2_choice"]
df2["tokensEarned"] = df2["stage_3_outcome"]
df2["tokenOffer"] = df2["offer"]
df2["reward"] = (df2["stage_3_outcome"] >= 10).astype(int)
df2["subID"] = (df2["subject_id"]).astype(str)
df2["agencyRT"] = df2["stage_1_rt"]
df2["banditRT"] = df2["stage_2_rt"]
df1["agencyRT"] = df1["agencyRT"].round(2)
df2["agencyRT"] = df2["agencyRT"].round(2)
df1["banditRT"] = df1["banditRT"].round(2)
df2["banditRT"] = df2["banditRT"].round(2)


df1 = df1[cols_required]
df2 = df2[cols_required]

# these rows cannot be used
# in total missing data for 39 participants
# df2.query("agency.isna()").groupby("subID").count().count()
df2.query("agency.notna()", inplace = True)

for i in range(2):
    df = [df1, df2][i]
    df_info = [df_info1, df_info2][i]
    df_full = pd.merge(df, df_info, how = "left", on = "subID")
    for participant in tqdm(df_full["subID"].unique()):
        prompt = ""
        agency_RT = []
        bandit_RT = []
        df_participant = df_full.query(f'subID == "{participant}"')
        prompt = 'You will be playing a slot machine game in which your goal is to collect as many coins as possible.\n'\
                 'In each round, you are going to play one of three different two-armed bandits.\n'\
                 'The three bandits have arms of colors purple/red, orange/blue, and green/pink.\n'\
                 'In the beginning of each trial, you are going to be informed about which of the three bandits you are going to play.\n'\
                 'The location of the arms varies between trials, but you are going to be informed about that in the beginning of every trial.\n'\
                 'The three bandits differ in the distribution of reward probabilties. The reward probability of a given arm stays the same throughout the game.\n'\
                 'After playing an arm, you are going to collect 10 coins with the given reward probability, or 0 coins with (1 - reward probability).\n'\
                 'Each trial consists of two stages:\n'\
                 'In the first stage, you have to do an agency decision. That is, you decide if you select the arm from the bandit by yourself or if a random coin toss makes the decision for you.\n'\
                 'If you press "1", you decide yourself, if you press "0", the random coin toss decides.\n'\
                 'The second stage depends on your action in the first stage:\n'\
                 'If you decided to select by yourself, you can do the Arm decision. That is, you then choose between the left and the right arm.\n'\
                 'Press "1" to select the left arm. Press "2" to select the right arm.\n'\
                 'If you decided to go with the coin toss, one of the arms is selected randomly.\n'\
                 'Importantly, if you decided to go with the coin toss, you can earn a varying number of additional coins, which is going to be indicated in the beginning of each trial.\n'\
                 'Eventually, you receive feedback about the paid-out coins.\n'\
                 'The game starts now:\n'\
            
        for trial_id in df_participant["trial"]:
            df_trial = df_participant.query(f'trial == {trial_id}')
            str_bandit_condition = str(df_trial["color"].item())
            choice_agency = str(df_trial["agency"].item())
            choice_bandit = str(df_trial["banditResp"].item())
            taken_offer = str(df_trial["tokenOffer"].item())
            coins_bandit = str([0, 10][df_trial["reward"].item()])
            coins_agency = str([df_trial["tokensEarned"].item(), 0][int(df_trial["agency"].item())])
            coins_agency = str(coins_agency)
            color_left = str(df_trial["color_left"].item())
            prompt += "In this trial, you get offered " + taken_offer + " coins if you leave the decision to the random coin toss.\n"
            prompt += "Bandit: " + str_bandit_condition + ".\n"
            prompt += "The left arm of the bandit has color: " + color_left + ":\n"
            prompt += "Agency decision: You press <<" + choice_agency + ">>.\n"
            if choice_agency == "1":
                prompt += "Arm decision: You press <<" + choice_bandit + ">>.\n"
                prompt += "You get " + coins_bandit + " coins for the bandit decision.\n"
            elif choice_agency == "0":
                prompt += "The random coin toss decides to choose arm: <<" + choice_bandit + ">>.\n"
                prompt += "You get " + taken_offer + " coins for the agency decision and " + coins_bandit + " coins for the bandit decision.\n"
            agency_RT.append(df_trial["agencyRT"].item())
            bandit_RT.append(df_trial["banditRT"].item())
        all_prompts.append({
            "text": prompt, 
            "experiment": "hartley2024twoarmedbandit/" + datasets[i], 
            "participant": participant,
            "agency_RTs": agency_RT,
            "bandit_RTs": bandit_RT,
            "age": df_trial["age"].item()
        })

with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
