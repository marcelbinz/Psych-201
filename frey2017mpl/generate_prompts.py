import pandas as pd
import os
import json
import math
import numpy as np
import sys
sys.path.append("..")

base_path = "/Volumes/Extreme SSD/MPI/mpi_tasks/basel_berlin_data"
folders = ["main"]

output_prompts = []

def convert_to_builtin_type(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def format_number(num):
    return f"{int(num)}" if num == int(num) else f"{num:.1f}"

def format_outcome(value, outcome_type):
    if value < 0:
        return f"lose {format_number(abs(value))}"
    if outcome_type == "win":
        return f"gain {format_number(value)}"
    return f"lose {format_number(value)}"

for folder in folders:
    mpl_path = os.path.join(base_path, folder, "mpl", "mpl.csv")
    mpl_problems_path = os.path.join(base_path, folder, "mpl", "mplProblems.csv")
    participants_path = os.path.join(base_path, folder, "participants", "participants.csv")

    mpl_data = pd.read_csv(mpl_path)
    mpl_problems = pd.read_csv(mpl_problems_path)
    participants = pd.read_csv(participants_path)

    merged_data = pd.concat([mpl_data.reset_index(drop=True), mpl_problems.reset_index(drop=True)], axis=1)
    merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]
    grouped = merged_data.groupby(['dp', 'decision'])
    merged_data['A_out1'] = grouped['A_out1'].transform('first')
    merged_data['A_out2'] = grouped['A_out2'].transform('first')
    merged_data['A_p1'] = grouped['A_p1'].transform('first')
    merged_data['A_p2'] = grouped['A_p2'].transform('first')
    merged_data['B_out1'] = grouped['B_out1'].transform('first')
    merged_data['B_out2'] = grouped['B_out2'].transform('first')
    merged_data['B_p1'] = grouped['B_p1'].transform('first')
    merged_data['B_p2'] = grouped['B_p2'].transform('first')

    for participant_id in merged_data["partid"].unique():
        participant_data = merged_data[merged_data["partid"] == participant_id]
        meta_row = participants[participants["partid"] == participant_id]

        trials_text = []

        session_text = (
            "You will be presented with several pairs of lotteries in each trial. Each lottery offers specific chances of winning or losing points. Each point equates to 0.075 CHF or 0.05 EUR. \n"
            "Your task is to choose between lottery A and lottery B in each pair. Each choice affects your potential earnings.\n"
            "The money earned in this study will be added to or subtracted from your starting bonus of 15 CHF or 10 EUR. In the two most extreme cases, you can either double or entirely lose this amount."
            "No immediate feedback will be provided regarding the outcomes of your choices. "
        )

        for trial_number, trial_data in participant_data.groupby("dp"):
            trial_text = [f"Problem {int(trial_number)}:"]
            for trial in trial_data.itertuples():
                if any(math.isnan(x) for x in [trial.A_p1, trial.A_p2, trial.B_p1, trial.B_p2]):
                    continue

                # Lottery A
                a_line = (
                    f"Lottery A: {trial.A_p1 * 100:.0f}% chance to {format_outcome(trial.A_out1, 'win')} points and "
                    f"{trial.A_p2 * 100:.0f}% chance to {format_outcome(trial.A_out2, 'lose')} points."
                )

                # Lottery B
                b_line = (
                    f"Lottery B: {trial.B_p1 * 100:.0f}% chance to {format_outcome(trial.B_out1, 'win')} points and "
                    f"{trial.B_p2 * 100:.0f}% chance to {format_outcome(trial.B_out2, 'lose')} points."
                )

                choice_line = f"You chose lottery <<{'A' if trial.choice == 0 else 'B'}>>."

                trial_text.extend([a_line, b_line, choice_line, ""])

            if len(trial_text) > 1:
                trials_text.append("\n".join(trial_text))

        participant_text = session_text.strip() + "\n\n\n" + "\n\n".join(trials_text)

        meta_info = {}
        if not meta_row.empty:
            for field in ["sex", "age", "location"]:
                if field in meta_row.columns and not pd.isnull(meta_row.iloc[0][field]):
                    meta_info[field] = meta_row.iloc[0][field]

        prompt = {
            "participant": f"{participant_id}",
            "experiment": "MPL",
            "text": participant_text,
        }
        if meta_info:
            prompt.update(meta_info)

        output_prompts.append(prompt)

output_path = "prompts.jsonl"

with open(output_path, "w") as f:
    for prompt in output_prompts:
        prompt = {k: convert_to_builtin_type(v) for k, v in prompt.items()}
        f.write(json.dumps(prompt) + "\n")