import os

import jsonlines
import pandas as pd

data_path = "../Barnby_etal_2021_SVO/Data"


p1_prompt = """You are matched with an anonymous partner. 
You will be presented with two options, each of which describes the number of points you and your partner will receive. You must choose the option that you prefer.
In all trials, you must collect as many points as possible. You will be paid based on the number of points you collect at the end of the experiment.
"""

p2_prompt = """You return to the lab 7 days later.
You are be matched with a new anonymous partner.
You will also be presented with two options, each of which describes the number of points you and your partner will receive. You must choose the option that you think your partner will choose. You will receive more points if you correctly predict your partner's choice. You will be informed about whether you answered correctly or not.
At the end, you will be asked to rate the extent to which you agree that your partner was motivated by harmful intent and self-interest, using two separate scales between 0 and 100, with 100 indicating maximum harmful intent or self-interest.
You will also be asked whether you think your partner was (1) aiming to share money equally, (2) trying to earn as much money as possible, or (3) trying to prevent you from earning money.
"""

phase1 = pd.read_csv(os.path.join(data_path, "Intentions_Phase1.csv"))
phase2 = pd.read_csv(os.path.join(data_path, "Intentions_Phase2.csv"))

final_mc_question = {
    "Trying to share as much money between us as possibe" : 1, # spelling mistake is in the original data
    "Trying to earn as much money as possible" : 2,
    "Trying to stop me from earning points" : 3,
}

ids = range(1, 698) # 697 participants in the study
output = []

for id in ids:
    text = p1_prompt
    reaction_times = []
    participant_subset_p1 = phase1[phase1["id"] == id]
    age = str(int(participant_subset_p1["Age"].values[0]))
    ethnicity = str(participant_subset_p1["Ethnicity"].values[0])
    ICARTot = str(int(participant_subset_p1["ICARTot"].values[0]))
    ICARrt = str(int(participant_subset_p1["ICARrt"].values[0]))
    for i, row in participant_subset_p1.iterrows():
        response = int(row['Response'])
        text = f"{text}\nTrial {row['Trial']}:\nOption 1: Points for you: {row['Option1_PPT']}, Points for your partner: {row['Option1_Partner']}\nOption 2: Points for you: {row['Option2_PPT']}, Points for your partner: {row['Option2_Partner']}\n\n. You chose option <<{str(response)}>>. You received {int(row[f'Option{response}_PPT'])} points."
        reaction_times.append(float(row['Intentions_RT']))
    participant_subset_p2 = phase2[phase2["id"] == id]
    text = f"{text}\n\n{p2_prompt}\n"
    for i, row in participant_subset_p2.iterrows():
        response = int(row['Response'])
        correct_answer = int(row['Answer'])
        points = "1 point" if response == correct_answer else "0 points"
        text = f"{text}\nTrial {row['Trial']}:\nOption 1: Points for you: {row['Option1_PPT']}, Points for your partner: {row['Option1_Partner']}\nOption 2: Points for you: {row['Option2_PPT']}, Points for your partner: {row['Option2_Partner']}\n\n. You chose option <<{str(response)}>>. Your partner chose option {str(correct_answer)}. You received {points}."
        reaction_times.append(float(row['Intentions_RT']))
    if row['Final_Guess'] == "Please select an option": # participant 555 did not answer the final question. We will exclude them.
        continue
    else:
        rating = final_mc_question[str(row['Final_Guess'])]
    text = f"{text}\n\nYou rated your partner's harmful intent as <<{int(participant_subset_p2['HI'].values[0])}>> and self-interest as <<{int(participant_subset_p2['SI'].values[0])}>> on separate scales from 0 to 100. When asked whether your partner was aiming to (1) share money equally, (2) trying to earn as much money as possible, or (3) trying to prevent you from earning money. You chose <<{rating}>>."
    reaction_times.extend(['NA'] * 3)
    assert len(reaction_times) == 18 + 36 + 3, "Incorrect number of reaction times. There should be 18 phase 1 trials, 36 phase 2 trials, and 3 final questions (all NAs)."
    output.append({"text" : text, "experiment" : "barnby2022knowing", "participant" : id, "RTs" : reaction_times, "age" : age, "nationality" : ethnicity, "ICARTot" : ICARTot, "ICAR_RT" : ICARrt})

with jsonlines.open('barnby2022knowing/prompts.jsonl', 'w') as writer:
    writer.write_all(output)
