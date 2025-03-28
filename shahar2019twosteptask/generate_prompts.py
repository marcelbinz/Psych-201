import sys
import jsonlines
import pandas as pd
from tqdm import tqdm
sys.path.append("..")
from utils import randomized_choice_options

for dataset in ["exp1.csv"]: # "TST_nspn.csv" from https://osf.io/zc24g
    df = pd.read_csv(dataset)

    # instructions for measurement 1
    instructions = (
        "You will make choices in a two-stage decision task.\n"
        "In the first stage, you will choose between two options: {option_1} and {option_2}.\n"
        "Your first-stage choice will lead to one of two second-stage states: {state_1} or {state_2}.\n"
        "In each second-stage state, you will make another choice between two options: {option_3} and {option_4}.\n"
        "Each second-stage choice can result in either receiving a reward (1) or no reward (0).\n"
        "The reward probabilities of second-stage options change slowly over time.\n"
        "Your goal is to maximize your rewards over {n_trials} trials.\n\n"
    )

    # instructions for measurement 2
    instructions2 = (
        "\n\nYou are now back 18 months later to undertake the same task again but this time over {n_trials} new trials.\n\n"
    )

    json_out = []

    for participant in tqdm(df.subject.unique()):
        # Get random symbols for options and states
        option_1, option_2, option_3, option_4, state_1, state_2 = randomized_choice_options(6)
        
        par_instructions = instructions.format(
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            state_1=state_1,
            state_2=state_2,
            n_trials=121 # 121 for measurement 1
        )

        par_instructions2 = instructions2.format(
            n_trials=201 # 201 for measurement 2
        )
        
        par_dict = {
            "text": par_instructions,
            "experiment": 'shahar2019twosteptask/TST_nspn.csv',
            "participant": str(participant),
            "RTs": []
        }
        
        par_df = df[df.subject == participant].reset_index(drop=True)

        for measurment in [1, 2]:
            measurment_df = par_df[par_df.measurment == measurment].reset_index(drop=True)
            n_trials = measurment_df.trial.nunique() # 121 for measurement 1, 201 for measurement 2
            for trial in measurment_df.trial.unique():
                trial_df = measurment_df[measurment_df.trial == trial].reset_index(drop=True)
                # if first trial of this subject on measurement 2, add the instructions
                if measurment == 2 and trial == measurment_df.trial.min():
                    par_dict["text"] += par_instructions2

                choice1 = trial_df.choice1.values[0]
                choice2 = trial_df.choice2.values[0]
                rt1 = int(1000 * trial_df.RT1.values[0]) #switch to ms
                rt2 = int(1000*trial_df.RT2.values[0]) #switch to ms
                reward = trial_df.reward.values[0]
                transition = trial_df.transition.values[0]
                second_stage_state = trial_df.second_stage_state.values[0]

                # Store reaction times
                par_dict["RTs"].extend([rt1, rt2])

                # Map the second stage state to our randomized state names
                current_state = state_1 if second_stage_state == 2 else state_2

                trial_text = (
                    f"You are presented with first-stage options {option_1} and {option_2}. "
                    f"You choose <<{option_1 if choice1 == 1 else option_2}>>. "
                    f"This leads to state {current_state}. "
                    f"In state {current_state}, you choose <<{option_3 if choice2 == 1 else option_4}>>. "
                    f"You receive {'a reward' if reward == 1 else 'no reward'}.\n"
                )

                par_dict["text"] += trial_text

        json_out.append(par_dict)

with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)