import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

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

# (post_model, base_model, display_name)
PAIRS = [
    # Qwen1.5
    #("Qwen-Qwen1.5-0.5B-Chat.pth",  "Qwen-Qwen1.5-0.5B.pth",  "Qwen1.5-0.5B-Chat"),
    #("Qwen-Qwen1.5-1.8B-Chat.pth",  "Qwen-Qwen1.5-1.8B.pth",  "Qwen1.5-1.8B-Chat"),
    #("Qwen-Qwen1.5-4B-Chat.pth",    "Qwen-Qwen1.5-4B.pth",    "Qwen1.5-4B-Chat"),
    #("Qwen-Qwen1.5-7B-Chat.pth",    "Qwen-Qwen1.5-7B.pth",    "Qwen1.5-7B-Chat"),
    #("Qwen-Qwen1.5-14B-Chat.pth",   "Qwen-Qwen1.5-14B.pth",   "Qwen1.5-14B-Chat"),
    #("Qwen-Qwen1.5-32B-Chat.pth",   "Qwen-Qwen1.5-32B.pth",   "Qwen1.5-32B-Chat"),
    #("Qwen-Qwen1.5-72B-Chat.pth",   "Qwen-Qwen1.5-72B.pth",   "Qwen1.5-72B-Chat"),
    # Qwen2
    #("Qwen-Qwen2-0.5B-Instruct.pth", "Qwen-Qwen2-0.5B.pth",   "Qwen2-0.5B-Instruct"),
    #("Qwen-Qwen2-1.5B-Instruct.pth", "Qwen-Qwen2-1.5B.pth",   "Qwen2-1.5B-Instruct"),
    #("Qwen-Qwen2-7B-Instruct.pth",   "Qwen-Qwen2-7B.pth",     "Qwen2-7B-Instruct"),
    #("Qwen-Qwen2-72B-Instruct.pth",  "Qwen-Qwen2-72B.pth",    "Qwen2-72B-Instruct"),
    # Qwen2.5
    #("Qwen-Qwen2.5-0.5B-Instruct.pth",  "Qwen-Qwen2.5-0.5B.pth",  "Qwen2.5-0.5B-Instruct"),
    #("Qwen-Qwen2.5-1.5B-Instruct.pth",  "Qwen-Qwen2.5-1.5B.pth",  "Qwen2.5-1.5B-Instruct"),
    #("Qwen-Qwen2.5-3B-Instruct.pth",    "Qwen-Qwen2.5-3B.pth",    "Qwen2.5-3B-Instruct"),
    #("Qwen-Qwen2.5-7B-Instruct.pth",    "Qwen-Qwen2.5-7B.pth",    "Qwen2.5-7B-Instruct"),
    #("Qwen-Qwen2.5-14B-Instruct.pth",   "Qwen-Qwen2.5-14B.pth",   "Qwen2.5-14B-Instruct"),
    #("Qwen-Qwen2.5-32B-Instruct.pth",   "Qwen-Qwen2.5-32B.pth",   "Qwen2.5-32B-Instruct"),
    #("Qwen-Qwen2.5-72B-Instruct.pth",   "Qwen-Qwen2.5-72B.pth",   "Qwen2.5-72B-Instruct"),
    # Qwen2.5 Math
    #("Qwen-Qwen2.5-Math-1.5B.pth",  "Qwen-Qwen2.5-1.5B.pth",  "Qwen2.5-1.5B-Math"),
    #("Qwen-Qwen2.5-Math-7B.pth",    "Qwen-Qwen2.5-7B.pth",    "Qwen2.5-7B-Math"),
    #("Qwen-Qwen2.5-Math-72B.pth",   "Qwen-Qwen2.5-72B.pth",   "Qwen2.5-72B-Math"),
    # Qwen2.5 Vision
    #("Qwen-Qwen2.5-VL-3B-Instruct.pth",  "Qwen-Qwen2.5-3B.pth",   "Qwen2.5-3B-VL"),
    #("Qwen-Qwen2.5-VL-7B-Instruct.pth",  "Qwen-Qwen2.5-7B.pth",   "Qwen2.5-7B-VL"),
    #("Qwen-Qwen2.5-VL-32B-Instruct.pth", "Qwen-Qwen2.5-32B.pth",  "Qwen2.5-32B-VL"),
    #("Qwen-Qwen2.5-VL-72B-Instruct.pth", "Qwen-Qwen2.5-72B.pth",  "Qwen2.5-72B-VL"),
    # DeepSeek R1 Distill Qwen
    #("deepseek-ai-DeepSeek-R1-Distill-Qwen-1.5B.pth", "Qwen-Qwen2.5-1.5B.pth", "DS-R1-Qwen-1.5B"),
    #("deepseek-ai-DeepSeek-R1-Distill-Qwen-7B.pth",   "Qwen-Qwen2.5-7B.pth",   "DS-R1-Qwen-7B"),
    #("deepseek-ai-DeepSeek-R1-Distill-Qwen-14B.pth",  "Qwen-Qwen2.5-14B.pth",  "DS-R1-Qwen-14B"),
    #("deepseek-ai-DeepSeek-R1-Distill-Qwen-32B.pth",  "Qwen-Qwen2.5-32B.pth",  "DS-R1-Qwen-32B"),
    # Qwen3
    ("Qwen-Qwen3-0.6B.pth",  "Qwen-Qwen3-0.6B-Base.pth",  "Qwen3-0.6B-Reasoning"),
    ("Qwen-Qwen3-1.7B.pth",  "Qwen-Qwen3-1.7B-Base.pth",  "Qwen3-1.7B-Reasoning"),
    ("Qwen-Qwen3-4B.pth",    "Qwen-Qwen3-4B-Base.pth",    "Qwen3-4B-Reasoning"),
    ("Qwen-Qwen3-8B.pth",    "Qwen-Qwen3-8B-Base.pth",    "Qwen3-8B-Reasoning"),
    ("Qwen-Qwen3-14B.pth",   "Qwen-Qwen3-14B-Base.pth",   "Qwen3-14B-Reasoning"),
    # Qwen3.5
    #("Qwen-Qwen3.5-0.8B.pth", "Qwen-Qwen3.5-0.8B-Base.pth", "Qwen3.5-0.8B"),
    #("Qwen-Qwen3.5-2B.pth",   "Qwen-Qwen3.5-2B-Base.pth",   "Qwen3.5-2B"),
    #("Qwen-Qwen3.5-4B.pth",   "Qwen-Qwen3.5-4B-Base.pth",   "Qwen3.5-4B"),
    #("Qwen-Qwen3.5-9B.pth",   "Qwen-Qwen3.5-9B-Base.pth",   "Qwen3.5-9B"),
    # Qwen3 VL
    ("Qwen-Qwen3-VL-2B-Instruct.pth",  "Qwen-Qwen3-1.7B-Base.pth", "Qwen3-2B-Vision-Instruct"),
    ("Qwen-Qwen3-VL-4B-Instruct.pth",  "Qwen-Qwen3-4B-Base.pth",   "Qwen3-4B-Vision-Instruct"),
    ("Qwen-Qwen3-VL-8B-Instruct.pth",  "Qwen-Qwen3-8B-Base.pth",   "Qwen3-8B-Vision-Instruct"),
    ("Qwen-Qwen3-VL-32B-Instruct.pth", "Qwen-Qwen3-14B-Base.pth",  "Qwen3-32B-Vision-Instruct"),
    ("Qwen-Qwen3-VL-2B-Thinking.pth",  "Qwen-Qwen3-1.7B-Base.pth", "Qwen3-2B-Vision-Thinking"),
    ("Qwen-Qwen3-VL-4B-Thinking.pth",  "Qwen-Qwen3-4B-Base.pth",   "Qwen3-4B-Vision-Thinking"),
    ("Qwen-Qwen3-VL-8B-Thinking.pth",  "Qwen-Qwen3-8B-Base.pth",   "Qwen3-8B-Vision-Thinking"),
    ("Qwen-Qwen3-VL-32B-Thinking.pth", "Qwen-Qwen3-14B-Base.pth",  "Qwen3-32B-Vision-Thinking"),
    # OLMo
    ("allenai-Olmo-3-7B-Instruct.pth",    "allenai-Olmo-3-1025-7B.pth",   "Olmo3-7B-Instruct"),
    ("allenai-Olmo-3.1-32B-Instruct.pth", "allenai-Olmo-3-1125-32B.pth",  "Olmo3.1-32B-Instruct"),
    ("allenai-Olmo-3-7B-Think.pth",       "allenai-Olmo-3-1025-7B.pth",   "Olmo3-7B-Think"),
    ("allenai-Olmo-3.1-32B-Think.pth",    "allenai-Olmo-3-1125-32B.pth",  "Olmo3.1-32B-Think"),
    # Llama
    #("meta-llama-Meta-Llama-3-8B-Instruct.pth", "meta-llama-Meta-Llama-3-8B.pth", "Llama3-8B-Instruct"),
    ("meta-llama-Llama-3.1-8B-Instruct.pth",    "meta-llama-Llama-3.1-8B.pth",   "Llama3.1-8B-Instruct"),
    ("meta-llama-Llama-3.1-70B-Instruct.pth",   "meta-llama-Llama-3.1-70B.pth",  "Llama3.1-70B-Instruct"),
    ("meta-llama-Llama-3.2-1B-Instruct.pth",    "meta-llama-Llama-3.2-1B.pth",   "Llama3.2-1B-Instruct"),
    ("meta-llama-Llama-3.2-3B-Instruct.pth",    "meta-llama-Llama-3.2-3B.pth",   "Llama3.2-3B-Instruct"),
    # DeepSeek R1 Distill Llama
    ("deepseek-ai-DeepSeek-R1-Distill-Llama-8B.pth",  "meta-llama-Llama-3.1-8B.pth",  "Llama3.1-8B-Reasoning"),
    ("deepseek-ai-DeepSeek-R1-Distill-Llama-70B.pth", "meta-llama-Llama-3.1-70B.pth", "Llama3.1-70B-Reasoning"),
    # Llama Vision
    ("unsloth-Llama-3.2-11B-Vision.pth", "meta-llama-Llama-3.1-8B.pth",  "Llama3.2-11B-Vision"),
    ("unsloth-Llama-3.2-90B-Vision.pth", "meta-llama-Llama-3.1-70B.pth", "Llama3.2-90B-Vision"),
]

all_models = set(m for pair in PAIRS for m in pair[:2])

categories = pd.read_csv("../csvs/psych_experiment_categories.csv")
categories = categories.drop(columns=["Intertemporal Choice", "Moral Judgment", "Psychophysics", "Cognitive Control"])
category_cols = [c for c in categories.columns if c not in ["experiment", "dataset"]]

# Accumulate sum, sum-of-squares, count per (experiment, model)
stats = defaultdict(lambda: [0.0, 0.0, 0])

CHUNKSIZE = 500_000
for chunk in pd.read_csv("../csvs/full_data_jureca_data.csv", chunksize=CHUNKSIZE,
                         usecols=["experiment", "model", "nll"]):
    chunk = chunk[chunk["model"].isin(all_models)]
    chunk["experiment"] = chunk["experiment"].str.replace("../data/", "", regex=False)
    for row in chunk.itertuples(index=False):
        key = (row.experiment, row.model)
        s = stats[key]
        s[0] += row.nll
        s[1] += row.nll * row.nll
        s[2] += 1

records = []
for (exp, model), (s, sq, n) in stats.items():
    mean = s / n
    std = np.sqrt(max(sq / n - mean ** 2, 0.0))
    records.append({"experiment": exp, "model": model, "mean": mean, "std": std})

agg = pd.DataFrame(records).merge(categories, on="experiment", how="inner")

# Compute Cohen's d per (display_name, category)
heatmap_data = {}

for post_model, base_model, name in PAIRS:
    post = agg[agg["model"] == post_model].set_index("experiment")
    base = agg[agg["model"] == base_model].set_index("experiment")
    common = post.index.intersection(base.index)
    if len(common) == 0:
        continue
    post, base = post.loc[common], base.loc[common]
    pooled_sd = np.sqrt((post["std"] ** 2 + base["std"] ** 2) / 2)
    cohen_d = (post["mean"] - base["mean"]) / pooled_sd
    cat_membership = post[category_cols]
    heatmap_data[name] = {
        cat: cohen_d[cat_membership[cat] == 1].mean()
        for cat in category_cols
    }

# Build matrix rows=models, cols=categories; append average row
model_names = [name for _, _, name in PAIRS if name in heatmap_data]
matrix = np.array([[heatmap_data[name].get(cat, np.nan) for cat in category_cols]
                   for name in model_names])

avg_row = np.nanmean(matrix, axis=0, keepdims=True)

# Sort columns by average Cohen's d (low to high)
# Sort columns (x) by average Cohen's d, low to high
col_order = np.argsort(avg_row[0])
category_cols = [category_cols[i] for i in col_order]
matrix = matrix[:, col_order]
avg_row = avg_row[:, col_order]

# Sort rows (y) by per-model average, low to high; keep Average row at bottom
row_avgs = np.nanmean(matrix, axis=1)
row_order = np.argsort(row_avgs)
matrix = matrix[row_order]
model_names = [model_names[i] for i in row_order]

matrix_with_avg = np.vstack([matrix, avg_row])
y_labels = model_names + ["Average"]

vmax = np.nanpercentile(np.abs(matrix), 95)

fig, ax = plt.subplots(figsize=(6.85, len(y_labels) * 0.18 + 1.0))
im = ax.imshow(matrix_with_avg, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)

# Separator line before the average row
ax.axhline(len(model_names) - 0.5, color="white", linewidth=2.0)

# Numbers in the average row, drawn on a white background with a black border
avg_row_idx = len(model_names)
for j, val in enumerate(avg_row[0]):
    if not np.isnan(val):
        ax.text(j, avg_row_idx, f"{val:.2f}", ha="center", va="center",
                fontsize=5, color="black",
                bbox=dict(boxstyle="round,pad=0.25,rounding_size=0.3",
                          facecolor="white", edgecolor="black", linewidth=0.5))

ax.set_xticks(range(len(category_cols)))
ax.set_xticklabels(category_cols, rotation=90, ha="right")
ax.set_yticks(range(len(y_labels)))
ax.set_yticklabels(y_labels)
ax.set_title("Post-training misalignment")

cbar = plt.colorbar(im, ax=ax, shrink=1.0, pad=0.02)


plt.tight_layout(pad=0.4)
plt.savefig("figures/fig4.png", dpi=300, bbox_inches="tight")
plt.savefig("figures/fig4.pdf", bbox_inches="tight")
plt.show()
