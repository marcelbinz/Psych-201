import pandas as pd
import os
import json
import numpy as np
# TEMP TEST LINE

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

for folder in folders:
    bart_pumps_path = os.path.join(base_path, folder, "bart", "bart_pumps.csv")
    bart_riskperc_path = os.path.join(base_path, folder, "bart", "bart_riskperc.csv")
    bart_rts_path = os.path.join(base_path, folder, "bart", "bart_rts.csv")
    participants_path = os.path.join(base_path, folder, "participants", "participants.csv")

    bart_pumps = pd.read_csv(bart_pumps_path)
    bart_riskperc = pd.read_csv(bart_riskperc_path)
    bart_rts = pd.read_csv(bart_rts_path)
    participants = pd.read_csv(participants_path)

    bart_pumps = bart_pumps.applymap(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isnull(x) else x)
    bart_riskperc = bart_riskperc.applymap(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isnull(x) else x)

    for participant_id in bart_pumps["partid"].unique():
        participant_pumps = bart_pumps[bart_pumps["partid"] == participant_id]
        participant_riskperc = bart_riskperc[bart_riskperc["partid"] == participant_id]
        participant_rts = bart_rts[bart_rts["partid"] == participant_id]
        meta_row = participants[participants["partid"] == participant_id]

        trials_text = []
        rts_dict = {}

        for trial_number in participant_pumps["trial"].unique():
            trial_pumps = participant_pumps[participant_pumps["trial"] == trial_number]
            if trial_pumps.empty:
                continue

            pumps = int(trial_pumps.iloc[-1]["pumps"])
            exploded = int(trial_pumps.iloc[-1]["exploded"])
            payoff = int(trial_pumps.iloc[-1]["payoff"])

            trial_text = [f"Balloon {trial_number}:"]
            trial_rts = []

            rts_row = participant_rts[participant_rts["trial"] == trial_number]
            if not rts_row.empty:
                for i in range(1, pumps + 1):
                    rt_col = f"pump{i}"
                    if rt_col in rts_row.columns and not pd.isnull(rts_row.iloc[0][rt_col]):
                        trial_rts.append(int(rts_row.iloc[0][rt_col]))

            for pump in range(1, pumps):
                trial_text.append(
                    f"You decided to <<pump>>. The balloon did not explode. You gained 1 point. "
                    f"You accumulated {pump} point{'s' if pump > 1 else ''}."
                )

            if exploded == 1:
                trial_text.append("You decided to <<pump>>. The balloon exploded. You lost all points.\n")
            else:
                trial_text.append(
                    f"You decided to <<pump>>. The balloon did not explode. You gained {pumps} points.\n"
                    f"You decided to <<stop>>. You earned {payoff} points.\n"
                )

            trials_text.append("\n".join(trial_text))
            rts_dict[f"Balloon {trial_number}"] = trial_rts

        session_text = (
            "Your goal is to maximize the money you can earn by inflating the balloon without making it explode."
            "In each round, you are shown a balloon. Every time you inflate it, the amount of money you could earn increases. Each pump equates to CHF 0.008 or 0.005 EUR.\n"
            "However, the balloon can explode at any moment."
            "If you stop inflating before it explodes, you keep the money accumulated in that round."
            "If the balloon explodes, you lose all the money from that round."
            "Each round starts with a new balloon."
            "At the end of the study, one round will be randomly selected."
            "The money you earned in that round will be added to your initial bonus of 15 CHF or 10 EUR.\n\n\n"
            + "\n\n".join(trials_text)
        )

        meta_info = {}
        if not meta_row.empty:
            for field in ["sex", "age", "location"]:
                if field in meta_row.columns and not pd.isnull(meta_row.iloc[0][field]):
                    meta_info[field] = meta_row.iloc[0][field]

        prompt = {
            "participant": str(participant_id),
            "experiment": "BART",
            "text": session_text
        }

        if rts_dict:
            prompt["RTs"] = rts_dict
        if meta_info:
            prompt.update(meta_info)

        output_prompts.append(prompt)

output_path = "prompts.jsonl"
with open(output_path, "w") as f:
    for prompt in output_prompts:
        prompt = {k: convert_to_builtin_type(v) for k, v in prompt.items()}
        f.write(json.dumps(prompt) + "\n")

