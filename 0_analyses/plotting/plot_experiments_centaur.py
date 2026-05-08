import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

categories = pd.read_csv("../csvs/psych_experiment_categories.csv")
psych201_experiments = set(categories[categories["dataset"] == "Psych-201"]["experiment"].values)

models = {"-p-project1-hai_1196-hf-hub-models--unsloth--Meta-Llama-3.1-70B-bnb-4bit-snapshots-a009b8db2439814febe725486a5ed388f12a8744-.pth", "-p-project1-hai_1196-hf-hub-models--marcelbinz--Llama-3.1-Centaur-70B-adapter-snapshots-159600db8be99dc183c289923148dfd96cbd8e07-.pth"}

chunks = []
for chunk in pd.read_csv("../csvs/full_data_jureca_data_centaur.csv", chunksize=1_000_000):
    chunk["experiment"] = chunk["experiment"].str.replace("../data/", "", regex=False)
    chunk = chunk[chunk["model"].isin(models) & chunk["experiment"].isin(psych201_experiments)]
    if len(chunk):
        chunks.append(chunk)
raw = pd.concat(chunks, ignore_index=True)
grouped = raw.groupby(["experiment", "model"])["nll"]
full_data = grouped.mean().rename("mean").to_frame()
full_data["sem"] = grouped.sem().values
full_data["n"] = grouped.count().values
full_data = full_data.reset_index()

# Average NLL per directory/model
s = raw.groupby(["directory", "experiment", "model"])["nll"].mean().groupby(["directory", "model"]).mean()
print(s)

# Compute sd from sem and n
full_data["sd"] = full_data["sem"] * np.sqrt(full_data["n"])

# Compute Cohen's d per experiment: (mean_llama - mean_centaur) / pooled_sd
instruct_exp = full_data[full_data["model"] == "-p-project1-hai_1196-hf-hub-models--unsloth--Meta-Llama-3.1-70B-bnb-4bit-snapshots-a009b8db2439814febe725486a5ed388f12a8744-.pth"].set_index("experiment")
base_exp = full_data[full_data["model"] == "-p-project1-hai_1196-hf-hub-models--marcelbinz--Llama-3.1-Centaur-70B-adapter-snapshots-159600db8be99dc183c289923148dfd96cbd8e07-.pth"].set_index("experiment")
common = instruct_exp.index.intersection(base_exp.index)

pooled_sd = np.sqrt((instruct_exp.loc[common, "sd"]**2 + base_exp.loc[common, "sd"]**2) / 2)
cohen_d = (instruct_exp.loc[common, "mean"] - base_exp.loc[common, "mean"]) / pooled_sd

# Average effect size
print("\nAverage effect size:")
print(cohen_d.mean())
print(cohen_d.sem())
