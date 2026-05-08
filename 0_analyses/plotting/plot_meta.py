import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import defaultdict

base_models = [
    ("Qwen-Qwen3-0.6B-Base.pth",       "Qwen3-0.6B"),
    ("Qwen-Qwen3-1.7B-Base.pth",       "Qwen3-1.7B"),
    ("Qwen-Qwen3-4B-Base.pth",         "Qwen3-4B"),
    ("Qwen-Qwen3-8B-Base.pth",         "Qwen3-8B"),
    ("Qwen-Qwen3-14B-Base.pth",        "Qwen3-14B"),
    ("allenai-Olmo-3-1025-7B.pth",     "Olmo3-7B"),
    ("allenai-Olmo-3-1125-32B.pth",    "Olmo3.1-32B"),
    ("meta-llama-Llama-3.2-1B.pth",    "Llama3.2-1B"),
    ("meta-llama-Llama-3.2-3B.pth",    "Llama3.2-3B"),
    ("meta-llama-Llama-3.1-8B.pth",    "Llama3.1-8B"),
    ("meta-llama-Llama-3.1-70B.pth",   "Llama3.1-70B"),
]

instruct_models = [
    ("Qwen-Qwen3-0.6B.pth",                     "Qwen3-0.6B-Reasoning"),
    ("Qwen-Qwen3-1.7B.pth",                     "Qwen3-1.7B-Reasoning"),
    ("Qwen-Qwen3-4B.pth",                       "Qwen3-4B-Reasoning"),
    ("Qwen-Qwen3-8B.pth",                       "Qwen3-8B-Reasoning"),
    ("Qwen-Qwen3-14B.pth",                      "Qwen3-14B-Reasoning"),
    ("allenai-Olmo-3-7B-Instruct.pth",          "Olmo3-7B-Instruct"),
    ("allenai-Olmo-3.1-32B-Instruct.pth",       "Olmo3.1-32B-Instruct"),
    ("meta-llama-Llama-3.2-1B-Instruct.pth",    "Llama3.2-1B-Instruct"),
    ("meta-llama-Llama-3.2-3B-Instruct.pth",    "Llama3.2-3B-Instruct"),
    ("meta-llama-Llama-3.1-8B-Instruct.pth",    "Llama3.1-8B-Instruct"),
    ("meta-llama-Llama-3.1-70B-Instruct.pth",   "Llama3.1-70B-Instruct"),
]


exclude = {"evangelidis2023upscaling", "gunadi2021deferral"}

all_model_names = {m[0] for m in base_models + instruct_models}

# --- memory-efficient loading ------------------------------------------------
stats = defaultdict(lambda: [0.0, 0.0, 0])

for path, directory_label in [
    ("../csvs/full_data_jureca_data.csv",      "data"),
    ("../csvs/full_data_jureca_data_meta.csv", "data_meta"),
]:
    for chunk in pd.read_csv(path, usecols=["experiment", "model", "nll"], chunksize=500_000):
        chunk = chunk[chunk["model"].isin(all_model_names)]
        chunk["experiment"] = chunk["experiment"].str.replace("../data/", "", regex=False)
        for row in chunk.itertuples(index=False):
            s = stats[(row.experiment, row.model, directory_label)]
            s[0] += row.nll
            s[1] += row.nll * row.nll
            s[2] += 1

records = []
for (exp, model, directory), (s, sq, n) in stats.items():
    mean = s / n
    std = np.sqrt(max(sq / n - mean ** 2, 0.0))
    records.append({"experiment": exp, "model": model, "directory": directory,
                    "mean": mean, "sd": std})

full_data = pd.DataFrame(records)

# --- compute Cohen's d (meta - data) per model -------------------------------
def compute_cohen_ds(model_list):
    result = {}
    for model_file, label in model_list:
        md = full_data[full_data["model"] == model_file]
        meta_exp = md[md["directory"] == "data_meta"].set_index("experiment")
        data_exp = md[md["directory"] == "data"].set_index("experiment")
        meta_exp = meta_exp.loc[~meta_exp.index.isin(exclude)]
        data_exp = data_exp.loc[~data_exp.index.isin(exclude)]
        common = meta_exp.index.intersection(data_exp.index)
        if len(common) == 0:
            continue
        pooled_sd = np.sqrt((meta_exp.loc[common, "sd"] ** 2 + data_exp.loc[common, "sd"] ** 2) / 2)
        cohen_d = (data_exp.loc[common, "mean"] - meta_exp.loc[common, "mean"]) / pooled_sd
        result[label] = cohen_d
        print(f"{label}: mean={cohen_d.mean():.4f}, n={len(cohen_d)}")
    return result

print("=== Base models ===")
base_cohen_ds = compute_cohen_ds(base_models)
print("=== Instruct models ===")
instruct_cohen_ds = compute_cohen_ds(instruct_models)

# --- plot --------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial"],
    "font.size": 7,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 5.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 3,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2,
    "ytick.major.size": 2,
})

fig, axes = plt.subplots(1, 2, figsize=(6.85, 2.8), sharey=True)

for ax, cohen_ds, model_list, title in [
    (axes[0], base_cohen_ds,     base_models,     "Base models"),
    (axes[1], instruct_cohen_ds, instruct_models, "Instruct models"),
]:
    labels = [label for _, label in model_list if label in cohen_ds]
    df = pd.DataFrame([
        {"model": label, "cohen_d": v}
        for label in labels
        for v in cohen_ds[label].values
    ])

    sns.boxplot(data=df, x="model", y="cohen_d", order=labels,
                linewidth=0.7, showfliers=False,
                showmeans=True, meanline=True,
                boxprops={"facecolor": (0.12, 0.47, 0.71, 1.0),
                          "edgecolor": "C0"},
                whiskerprops={"color": "C0"},
                capprops={"color": "C0"},
                medianprops={"visible": False},
                meanprops={"color": (0.0, 0.1, 0.25), "linestyle": "-", "linewidth": 1.0},
                ax=ax)

    sns.stripplot(data=df, x="model", y="cohen_d", order=labels,
                  color="black", size=1.5, alpha=0.7, jitter=0.2,
                  ax=ax)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticklabels(labels, rotation=90, ha="center")
    ax.set_title(title)
    ax.set_xlabel("")
    ax.grid(True, axis="y", alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)

    family_of = lambda lab: "".join(c for c in lab.split("-")[0] if c.isalpha())
    for i in range(1, len(labels)):
        if family_of(labels[i]) != family_of(labels[i - 1]):
            ax.axvline(i - 0.5, color="0.7", linewidth=0.5, linestyle="--")

axes[0].set_ylabel("Meta-data benefit")
axes[1].set_ylabel("")

plt.tight_layout(pad=0.4)
plt.savefig("figures/fig5.png", dpi=300, bbox_inches="tight")
plt.savefig("figures/fig5.pdf", bbox_inches="tight")
plt.show()
