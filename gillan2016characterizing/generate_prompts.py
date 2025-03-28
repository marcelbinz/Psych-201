# data from https://osf.io/usdgt/
import sys

sys.path.append("..")

import os
from glob import glob
import pandas as pd
import jsonlines
from utils import randomized_choice_options

import numpy as np

np.random.seed(1234)


instructions = """
You will be selecting one of the fractals {fractal_0} or {fractal_1}. These fractals will take you to one of blue or orange state.
The fractals can take you to either state, but one will mostly take you to the blue state, and the other will mostly take you to the orange state.
The state a fractal takes you to most won't change during the game.
Blue state has fractal {fractal_2} and fractal {fractal_3}, and orange state has fractal {fractal_4} and {fractal_5}.
You will be asked to select one of these four fractals.
Each of these four fractals have a certain probability that they will hand out a 25 cents coin.
The probability of a fractal giving a coin will change slowly during the game.
You can select the fractals by pressing the corresponding keys.
Your goal is to collect as many coins as possible over the next 200 trials.\n
"""

SURVEY_COLUMNS = ["age", "iq", "sds_total", "stai_total", "oci_total", "lsas_total", "bis_total", "scz_total", "aes_total", "eat_total", "audit_total"]
BEH_COLUMNS = ["trial", "p_2", "p_3", "p_4", "p_5", "a_0", "a_0_redundant", "a_0_rt", "transition", "a_1", "a_1_redundant", "state_1", "a_1_rt", "reward", "redundant"]
json_out = []
for experiment_no in [1, 2]:
    missing_surveys = 0
    missing_behaviours = 0
    self_report = pd.read_csv(f"osfstorage-archive/Experiment {experiment_no}/self_report_study{experiment_no}.csv")
    exp_files = glob(f"osfstorage-archive/Experiment {experiment_no}/twostep_data_study{experiment_no}/*csv")
    for exp_file in exp_files:
        with open(exp_file, "r") as f:
            lines = f.readlines()

        # Find the first line where the first column is '1'
        start_idx = None
        for i, line in enumerate(lines):
            cols = line.strip().split(",")
            if cols[0] == "1":
                start_idx = i
        if start_idx is None:
            missing_behaviours += 1
            continue
        df = pd.read_csv(exp_file, skiprows=start_idx, header=None)
        df.columns = BEH_COLUMNS

        fractal_0, fractal_1, fractal_2, fractal_3, fractal_4, fractal_5 = randomized_choice_options(6)
        prompt = instructions.format(fractal_0=fractal_0, fractal_1=fractal_1, fractal_2=fractal_2, fractal_3=fractal_3, fractal_4=fractal_4, fractal_5=fractal_5)

        for trial in df.iterrows():
            trial = trial[1]
            state_1 = "blue" if trial.state_1 == 2 else "orange"
            a_0 = fractal_0 if trial.a_0 == "left" else fractal_1
            if state_1 == "blue":
                a_1 = fractal_2 if trial.a_1 == "left" else fractal_3
            else:
                a_1 = fractal_4 if trial.a_1 == "left" else fractal_5

            reward_text = "You get a coin." if trial.reward == 1 else "You do not get a coin."
            par_text = f"You select fractal <<{a_0}>>. You end up in the {state_1} state. You select <<{a_1}>>. {reward_text}\n"
            prompt += par_text

        par_name = os.path.basename(exp_file).split(".csv")[0]
        subj_col = "subj.x" if experiment_no == 1 else "subj"
        par_report = self_report[self_report[subj_col] == par_name].reset_index(drop=True)
        par_report = par_report[par_report.columns[par_report.columns.isin(SURVEY_COLUMNS)]]
        try:
            par_report = par_report.iloc[0].to_dict()
        except IndexError:  # some people are missing survey data
            par_report = {}
            missing_surveys += 1

        reaction_0, reaction_1 = df.a_0_rt.values, df.a_1_rt.values
        reaction_times = np.empty((reaction_0.size + reaction_1.size), dtype=reaction_0.dtype)
        reaction_times[0::2] = reaction_0
        reaction_times[1::2] = reaction_1
        reaction_times = reaction_times.tolist()

        assert prompt.count("<<") == len(reaction_times)
        data_dict = {"text": prompt, "experiment": f"gillan2016characterizing/exp{experiment_no}.csv", "participant": par_name, "RTs": reaction_times}
        data_dict.update(par_report)
        json_out.append(data_dict)

    assert len(exp_files) == (self_report[subj_col].nunique() + missing_surveys)

    print(f"{missing_surveys} participants from experiment {experiment_no} missing survey data.")
    print(f"{missing_behaviours} participants from experiment {experiment_no} have corrupted behavioural data.")
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)
