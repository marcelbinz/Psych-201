import os
import re

import jsonlines
import scipy.io

data_path = "../moutoussis_2018"


gng_base_instr = """In this task, you will be presented with 4 stimuli, A, B, C, and D. Once the stimulus is presented, you must decide whether to press a button or not.
Each stimulus is associated with two possible outcomes, and your reward depends on whether you decide to press the button or not.
For two of the stimuli, choosing correctly (press or no press) increases your reward by £1 with 0.8 probability and does not increase it with 0.2 probability. Choosing incorrectly increases your reward by £1 with 0.2 probability and does not increase it with 0.8 probability.
For the other two stimuli, choosing correctly (press or no press) does not increase your reward with 0.8 probability and decreases your reward by £1 with 0.2 probability. Choosing incorrectly does not increase your reward with 0.2 probability and decreases your reward by £1 with 0.8 probability.
You do not know which stimuli are associated with which outcomes.
You are playng for real money. Excellent performance could be worth up to £5 in additional earnings. Random performance will not be rewarded with additional earnings.

Choose 1 to press the button and 0 to not press the button.

"""

stim_dict_base = {
    "1" : "A",
    "2" : "B",
    "3" : "C",
    "4" : "D",
}

output = []
ids = []
dir_path_base = os.path.join(data_path, "S1") # baseline test
data_files_base = os.listdir(dir_path_base)
for d in data_files_base:
    id_match = re.match(r'(\d{5})', d)
    id_number = id_match.group(1)
    mat_data = scipy.io.loadmat(os.path.join(dir_path_base, d))
    trial_nums = mat_data["LearnVerData"][:, 0]
    stimuli = mat_data["LearnVerData"][:, 1]
    choices  = mat_data["LearnVerData"][:, 12]
    rewards = mat_data["LearnVerData"][:, 16]
    text = f"{gng_base_instr}"
    for n, s, c, r in zip(trial_nums, stimuli, choices, rewards):
        if int(c) == 3:
            continue
        else:
            reward = f"£{int(r)}" if int(r) >= 0 else f"-£{abs(int(r))}"
            next_trial = f"The stimulus on the next trial is {stim_dict_base[str(int(s))]}. You chose <<{str(int(c))}>>. You received {reward}."
            text = f"{text} {next_trial}"
    output.append({"text": text, "experiment": "moutoussis2018pavlovian", "participant": f"{id_number}"})
    ids.append(id_number)


gng_six_instr = """You have returned to the lab 6 months later.

In this task, you will be presented with 4 new stimuli, K, L, M, N. Once the stimulus is presented, you must decide whether to press a button or not.
Each stimulus is associated with two possible outcomes, and your reward depends on whether you decide to press the button or not.
For two of the stimuli, choosing correctly (press or no press) increases your reward by £1 with 0.8 probability and does not increase it with 0.2 probability. Choosing incorrectly increases your reward by £1 with 0.2 probability and does not increase it with 0.8 probability.
For the other two stimuli, choosing correctly (press or no press) does not increase your reward with 0.8 probability and decreases your reward by £1 with 0.2 probability. Choosing incorrectly does not increase your reward with 0.2 probability and decreases your reward by £1 with 0.8 probability.
You do not know which stimuli are associated with which outcomes.
You are playng for real money. Excellent performance could be worth up to £5 in additional earnings. Random performance will not be rewarded with additional earnings.

Choose 1 to press the button and 0 to not press the button.

"""

stim_dict_six = {
    "1" : "K",
    "2" : "L",
    "3" : "M",
    "4" : "N",
}


dir_path_six = os.path.join(data_path, "S2") # baseline test
data_files_six = os.listdir(dir_path_six)
ids_six_month = []
for d in data_files_six:
    id_match = re.match(r'(\d{5})', d)
    id_number = id_match.group(1)
    ids_six_month.append(id_number)
    index_of_participant = ids.index(id_number)
    mat_data = scipy.io.loadmat(os.path.join(dir_path_six, d))
    trial_nums = mat_data["LearnVerData"][:, 0]
    stimuli = mat_data["LearnVerData"][:, 1]
    choices  = mat_data["LearnVerData"][:, 12]
    rewards = mat_data["LearnVerData"][:, 16]
    new_text = f"{output[index_of_participant]['text']}\n\n{gng_six_instr}"
    for n, s, c, r in zip(trial_nums, stimuli, choices, rewards):
        if int(c) == 3:
            continue
        else:
            reward = f"£{int(r)}" if int(r) >= 0 else f"-£{abs(int(r))}"
            next_trial = f"The stimulus on the next trial is {stim_dict_six[str(int(s))]}. You chose <<{str(int(c))}>>. You received {reward}."
            new_text = f"{new_text} {next_trial}"
    output[index_of_participant]['text'] = new_text


gng_eighteen_instr = """You have returned to the lab 18 months later.

In this task, you will be presented with 4 new stimuli, W, X, Y, Z. Once the stimulus is presented, you must decide whether to press a button or not.
Each stimulus is associated with two possible outcomes, and your reward depends on whether you decide to press the button or not.
For two of the stimuli, choosing correctly (press or no press) increases your reward by £1 with 0.8 probability and does not increase it with 0.2 probability. Choosing incorrectly increases your reward by £1 with 0.2 probability and does not increase it with 0.8 probability.
For the other two stimuli, choosing correctly (press or no press) does not increase your reward with 0.8 probability and decreases your reward by £1 with 0.2 probability. Choosing incorrectly does not increase your reward with 0.2 probability and decreases your reward by £1 with 0.8 probability.
You do not know which stimuli are associated with which outcomes.
You are playng for real money. Excellent performance could be worth up to £5 in additional earnings. Random performance will not be rewarded with additional earnings.

Choose 1 to press the button and 0 to not press the button.

"""

stim_dict_eighteen = {
    "1" : "W",
    "2" : "X",
    "3" : "Y",
    "4" : "Z",
}


dir_path_eighteen = os.path.join(data_path, "S3") # baseline test
data_files_eighteen = os.listdir(dir_path_eighteen)
count_follow_ups_eighteen = 0
count_follow_ups_six_and_eighteen = 0
for d in data_files_eighteen:
    id_match = re.match(r'(\d{5})', d)
    id_number = id_match.group(1)
    if id_number not in ids:
        print(f"ID number {id_number} does not exist in 18-month data. It should do, in principle.")
        continue
    if id_number in ids_six_month:
        count_follow_ups_six_and_eighteen += 1
        gng_eighteen_instr = gng_eighteen_instr.replace("18 months", "12 months")
    index_of_participant = ids.index(id_number)
    ids.pop(index_of_participant)
    mat_data = scipy.io.loadmat(os.path.join(dir_path_eighteen, d))
    trial_nums = mat_data["LearnVerData"][:, 0]
    stimuli = mat_data["LearnVerData"][:, 1]
    choices  = mat_data["LearnVerData"][:, 12]
    rewards = mat_data["LearnVerData"][:, 16]
    new_text = f"{output[index_of_participant]['text']}\n\n{gng_eighteen_instr}"
    for n, s, c, r in zip(trial_nums, stimuli, choices, rewards):
        if int(c) == 3:
            continue
        else:
            reward = f"£{int(r)}" if int(r) >= 0 else f"-£{abs(int(r))}"
            next_trial = f"The stimulus on the next trial is {stim_dict_eighteen[str(int(s))]}. You chose <<{str(int(c))}>>. You received {reward}."
            new_text = f"{new_text} {next_trial}"
    output[index_of_participant]['text'] = new_text
    count_follow_ups_eighteen += 1

print(f"""Data found for {len(data_files_base)} participants on baseline study. 817 reported by the authors.
Data found for {len(data_files_six)} participants on 6-month follow-up. 61 reported by authors.
Data for {count_follow_ups_eighteen} participants on 18-month follow-up. 542 good-quality and 557 total reported by authors. Unclear how to identify good-quality IDs.
Data for {count_follow_ups_six_and_eighteen} participants who participated in 6- and 18-month follow-ups. 54 reported by authors.""")

with jsonlines.open('moutoussis2018pavlovian/prompts.jsonl', 'w') as writer:
    writer.write_all(output)
