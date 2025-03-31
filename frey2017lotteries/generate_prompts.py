import pandas as pd
import os
import json
import numpy as np

base_path = "/Volumes/Extreme SSD/MPI/mpi_tasks/basel_berlin_data"
folders = ["main"]

output_prompts = []

def convert_to_builtin_type(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def format_number(num):
    return f"{int(num)}" if num == int(num) else f"{num:.1f}"

def format_gain_or_loss(value):
    if value < 0:
        return f"lose {format_number(abs(value))}"
    else:
        return f"gain {format_number(value)}"

for folder in folders:
    lotteries_path = os.path.join(base_path, folder, "lotteries", "lotteries.csv")
    participants_path = os.path.join(base_path, folder, "participants", "participants.csv")

    lotteries_data = pd.read_csv(lotteries_path)
    participants = pd.read_csv(participants_path)

    for participant_id in lotteries_data["partid"].unique():
        participant_data = lotteries_data[lotteries_data["partid"] == participant_id]
        meta_row = participants[participants["partid"] == participant_id]

        gambles_text = []

        session_text = (
            "You will make decisions between two lotteries with varying outcomes and probabilities.\n"
            "For each lottery, you will be shown the potential gains, losses, and the probabilities of winning or losing points. Each point equates to CHF 0.10 or 0.07 EUR.\n"
            "The money earned in this study will be added to or subtracted from your starting bonus of 15 CHF or 10 EUR. In the two most extreme cases, you can either double or entirely lose this amount. \n"
            "No immediate feedback will be provided on the outcomes of your choices.\n\n"
        )

        for gamble_number, gamble_data in participant_data.groupby("Dec_ID"):

            gamble_text = [f"Problem {int(gamble_number)}:"]

            for trial in gamble_data.itertuples():
                lottery_A = (
                    f"Lottery A: {format_gain_or_loss(trial.X1)} points with a {trial.PX1:.0f}% chance or "
                    f"{format_gain_or_loss(trial.X2)} points with a {100 - trial.PX1:.0f}% chance."
                )
                lottery_B = (
                    f"Lottery B: {format_gain_or_loss(trial.Z1)} points with a {trial.PZ1:.0f}% chance or "
                    f"{format_gain_or_loss(trial.Z2)} points with a {100 - trial.PZ1:.0f}% chance."
                )
                decision_line = f"You chose <<{'A' if trial.Decision_X == 1 else 'B'}>>."

                trial_text = f"{lottery_A}\n{lottery_B}\n{decision_line}\n"
                gamble_text.append(trial_text)

            gambles_text.append("\n".join(gamble_text))

        participant_text = session_text.strip() + "\n\n\n" + "\n\n".join(gambles_text)

        meta_info = {}
        if not meta_row.empty:
            for field in ["sex", "age", "location"]:
                if field in meta_row.columns and not pd.isnull(meta_row.iloc[0][field]):
                    meta_info[field] = meta_row.iloc[0][field]

        prompt = {
            "participant": f"{participant_id}",
            "experiment": "Lotteries",
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