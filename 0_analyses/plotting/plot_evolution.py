import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../csvs/full_data_jureca_data.csv")

# --- Base model NLL scaling ---
s = df.groupby(["directory", "experiment", "model"])["nll"].mean().groupby(["directory", "model"]).mean()
tmp = s.reset_index()
value_col = tmp.columns[-1]
model_col = next(
    (c for c in tmp.columns[:-1] if tmp[c].astype(str).str.endswith(".pth").any()),
    tmp.columns[-2],
)
data = tmp[[model_col, value_col]].rename(columns={model_col: "model", value_col: "value"})
data["model"] = data["model"].astype(str)

def parse_size_b(name: str):
    m = re.search(r"-(\d+(?:\.\d+)?)B", name)
    return float(m.group(1)) if m else None

def qwen_generation(name: str):
    n = name.lower()
    if not n.startswith("qwen-qwen"):
        return None
    if "instruct" in n or "coder" in n or "math" in n or "-vl-" in n:
        return None
    if "qwen3.5-" in n:
        if "base" in n:
            return "Qwen3.5"
        return None
    if "qwen3-" in n:
        if "base" in n:
            return "Qwen3"
        return None
    if "qwen2.5-" in n:
        return "Qwen2.5"
    if "qwen2-" in n:
        return "Qwen2"
    return None

data["size_b"] = data["model"].apply(parse_size_b)
data["generation"] = data["model"].apply(qwen_generation)
data = data.dropna(subset=["size_b", "generation"])

pivot = (
    data.pivot_table(index="size_b", columns="generation", values="value", aggfunc="mean")
    .sort_index()
)
col_order = ["Qwen2", "Qwen2.5", "Qwen3", "Qwen3.5"]
pivot = pivot[[c for c in col_order if c in pivot.columns]]

# --- Cohen's d (instruction misalignment) ---
qwen2_sizes = ["0.5B", "1.5B", "7B", "72B"]
qwen25_sizes = ["0.5B", "1.5B", "3B", "7B", "14B", "32B", "72B"]
qwen3_sizes = ["0.6B", "1.7B", "4B", "8B", "14B"]
qwen35_sizes = ["0.8B", "2B", "4B", "9B"]

pairs = []
for size in qwen2_sizes:
    pairs.append({"family": "Qwen2", "size": size,
                  "base": f"Qwen-Qwen2-{size}.pth",
                  "instruct": f"Qwen-Qwen2-{size}-Instruct.pth"})
for size in qwen25_sizes:
    pairs.append({"family": "Qwen2.5", "size": size,
                  "base": f"Qwen-Qwen2.5-{size}.pth",
                  "instruct": f"Qwen-Qwen2.5-{size}-Instruct.pth"})
for size in qwen3_sizes:
    pairs.append({"family": "Qwen3", "size": size,
                  "base": f"Qwen-Qwen3-{size}-Base.pth",
                  "instruct": f"Qwen-Qwen3-{size}.pth"})
for size in qwen35_sizes:
    pairs.append({"family": "Qwen3.5", "size": size,
                  "base": f"Qwen-Qwen3.5-{size}-Base.pth",
                  "instruct": f"Qwen-Qwen3.5-{size}.pth"})

results = []
for p in pairs:
    base_data = df[df["model"] == p["base"]]
    instruct_data = df[df["model"] == p["instruct"]]
    if base_data.empty or instruct_data.empty:
        continue
    base_by_exp = base_data.groupby("experiment")["nll"]
    instruct_by_exp = instruct_data.groupby("experiment")["nll"]
    common = base_by_exp.mean().index.intersection(instruct_by_exp.mean().index)
    if common.empty:
        continue
    base_mean = base_by_exp.mean().loc[common]
    base_sd = base_by_exp.std().loc[common]
    instruct_mean = instruct_by_exp.mean().loc[common]
    instruct_sd = instruct_by_exp.std().loc[common]
    pooled_sd = np.sqrt((base_sd**2 + instruct_sd**2) / 2)
    cohen_d = (instruct_mean - base_mean) / pooled_sd
    mean_d = cohen_d.mean()
    results.append({"family": p["family"], "size": p["size"], "cohen_d": mean_d})

results = pd.DataFrame(results)
results["size_num"] = results["size"].str.replace("B", "").astype(float)

# Average Cohen's d across all sizes within each generation
family_avg = (
    results.groupby("family")["cohen_d"].mean()
    .reindex(["Qwen2", "Qwen2.5", "Qwen3", "Qwen3.5"])
)

# Science figure formatting
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

family_order = ["Qwen2", "Qwen2.5", "Qwen3", "Qwen3.5"]
linestyles = ["dotted", "dashdot", "--", "-"]
alphas = [0.4, 0.6, 0.8, 1.0]

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(6.85, 2.0), gridspec_kw={"wspace": 0.35, "width_ratios": [1.4, 1.1]})

# Left panel: base model NLL
for i, col in enumerate(pivot.columns):
    y = pivot[col].dropna()
    ax1.plot(y.index, y.values, marker="o", label=col, color="C0",
             linestyle=linestyles[i], alpha=alphas[i])

ax1.set_xscale("log")
ax1.set_xlabel("Parameters (billions)")
ax1.set_ylabel("Negative log-likelihood (↓)")
ax1.grid(True, alpha=0.3, linewidth=0.5)
ax1.legend(frameon=False)

# Right panel: Cohen's d boxplot with individual points
families = ["Qwen2", "Qwen2.5", "Qwen3", "Qwen3.5"]
results["family"] = pd.Categorical(results["family"], categories=families, ordered=True)

print("=== Mean Cohen's d per family ===")
for fam, val in results.groupby("family", observed=True)["cohen_d"].mean().items():
    n = (results["family"] == fam).sum()
    print(f"{fam}: mean={val:.4f}, n={n}")

sns.boxplot(data=results, x="family", y="cohen_d", order=families,
            linewidth=0.7, showfliers=False, width=0.6,
            showmeans=True, meanline=True,
            boxprops={"edgecolor": "C0"},
            whiskerprops={"color": "C0"},
            capprops={"color": "C0"},
            medianprops={"visible": False},
            meanprops={"color": (0.0, 0.1, 0.25), "linestyle": "-", "linewidth": 1.0},
            ax=ax2)

c0 = (0.12, 0.47, 0.71)
box_patches = [p for p in ax2.patches if type(p).__name__ == "PathPatch"]
for patch, a in zip(box_patches, alphas):
    patch.set_facecolor((*c0, a))

sns.stripplot(data=results, x="family", y="cohen_d", order=families,
              color="black", size=3.0, alpha=0.8, jitter=0.2,
              ax=ax2)

ax2.set_xlabel("")
ax2.set_ylabel("Post-training misalignment")
ax2.grid(True, alpha=0.3, linewidth=0.5, axis="y")
ax2.set_axisbelow(True)

plt.tight_layout(pad=0.4, w_pad=1.0)
plt.savefig("figures/fig3a.png", dpi=300, bbox_inches="tight")
plt.savefig("figures/fig3a.pdf", bbox_inches="tight")
plt.show()
