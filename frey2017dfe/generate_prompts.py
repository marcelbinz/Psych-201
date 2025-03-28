import pandas as pd
import os
import json
import numpy as np

base_path = "/Volumes/Extreme SSD/MPI/mpi_tasks/basel_berlin_data"
folders = ["main"]

output_prompts = []


def format_number(num):
    return f"{int(num)}" if num == int(num) else f"{num:.1f}"


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
    dfe_samples_path = os.path.join(base_path, folder, "dfe", "dfe_samples.csv")
    dfe_samples = pd.read_csv(dfe_samples_path)
    participants_path = os.path.join(base_path, folder, "participants", "participants.csv")
    participants = pd.read_csv(participants_path)

    for participant_id in dfe_samples["partid"].unique():
        participant_data = dfe_samples[dfe_samples["partid"] == participant_id]
        meta_row = participants[participants["partid"] == participant_id]

        trials_text = []
        all_rts = []

        session_text = (
            "Each round, you’ll see two boxes: Box A and Box B. Each box contains different possible money amounts, with some outcomes being more likely than others.\n"
            "To learn what's in each box, you can sample as many times as you like. Each time you sample, you'll see how much money that box would have given you."
            "However, you won’t earn anything while sampling.\n"
            "Once you're confident, stop sampling and choose the box you like. One final outcome will be drawn from the box you chose, and that draw will determine how much you’ll earn for that round.\n"
            "At the end of the study, one of the tasks will be picked at random."
            "Your earnings from that task will be added to or subtracted from your starting bonus of 15 CHF or 10 EUR."
            "Depending on your choices, you could double your bonus—or lose it entirely."
        )

        for trial_number, trial_data in participant_data.groupby("gamble_ind"):

            trial_text = [f"Problem {int(trial_number)}:"]

            for trial in trial_data.itertuples():
                decision_text = (
                    f"You decided to <<sample {'A' if trial.sample_opt == 'A' else 'B'}>>. "
                    f"You observed an outcome of {format_number(trial.sample_out)} points."
                )
                trial_text.append(decision_text)
                all_rts.append(int(trial.sample_rts) if not pd.isna(trial.sample_rts) else None)

            final_decision = trial_data.iloc[-1]
            final_choice = "A" if final_decision.decision == "A" else "B"
            trial_text.append(
                f"You decided to <<choose {final_choice}>> based on your observations. "
            )

            trials_text.append("\n".join(trial_text))

        participant_text = session_text + "\n\n" + "\n\n".join(trials_text)
        meta_info = {}
        if not meta_row.empty:
            for field in ["sex", "age", "location"]:
                if field in meta_row.columns and not pd.isnull(meta_row.iloc[0][field]):
                    meta_info[field] = meta_row.iloc[0][field]

        prompt = {
            "participant": f"{participant_id}",
            "experiment": "Decisions From Experience",
            "text": participant_text,
            "RTs": all_rts,
        }

        if meta_info:
            prompt.update(meta_info)

        output_prompts.append(prompt)

output_path = "prompts.jsonl"
with open(output_path, "w") as f:
    for prompt in output_prompts:
        prompt = {k: convert_to_builtin_type(v) for k, v in prompt.items()}
        f.write(json.dumps(prompt) + "\n")
