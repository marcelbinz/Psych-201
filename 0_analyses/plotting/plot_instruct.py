import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df_no_template = pd.read_csv("../csvs/full_data_jureca_data.csv")
df_with_template = pd.read_csv("../csvs/full_data_jureca_data_instruct.csv")

instruct_models = set(df_with_template["model"].unique())
df_no_template = df_no_template[df_no_template["model"].isin(instruct_models)]


def mean_nll(df):
    return (
        df.groupby(["experiment", "model"])["nll"]
        .mean()
        .groupby("model")
        .mean()
        .reset_index()
        .rename(columns={"nll": "value"})
    )


def parse_size_b(name):
    m = re.search(r"-(\d+(?:\.\d+)?)B", name)
    return float(m.group(1)) if m else None


s_no = mean_nll(df_no_template)
s_with = mean_nll(df_with_template)

for df in [s_no, s_with]:
    df["size_b"] = df["model"].apply(parse_size_b)

s_no = s_no.dropna(subset=["size_b"])
s_with = s_with.dropna(subset=["size_b"])

# Split into families
def pivot_family(df, mask_fn):
    sub = df[df["model"].apply(mask_fn)].copy()
    return sub.groupby("size_b")["value"].mean().sort_index()


is_qwen3 = lambda n: n.startswith("Qwen-Qwen3-") and not n.startswith("Qwen-Qwen3.")
is_olmo = lambda n: "olmo" in n.lower() and "instruct" in n.lower()
is_llama = lambda n: "llama" in n.lower() and "instruct" in n.lower()

panels = [
    ("Qwen3", is_qwen3),
    ("Olmo3.X", is_olmo),
    ("Llama3.X", is_llama),
]

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

fig, axes = plt.subplots(nrows=1, ncols=3, sharey=True, figsize=(6.85, 2.0))

for ax, (title, mask_fn) in zip(axes, panels):
    y_no = pivot_family(s_no, mask_fn)
    y_with = pivot_family(s_with, mask_fn)

    ax.plot(y_no.index, y_no.values, marker="o", color="C0",
            linestyle="-", label="No template")
    ax.plot(y_with.index, y_with.values, marker="o", color="C1",
            linestyle="--", label="Default template")

    ax.set_xscale("log")
    #ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel("Parameters (billions)")
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.legend(frameon=False, loc="upper right")

axes[0].set_ylabel("Negative log-likelihood (↓)")

ymin, ymax = axes[0].get_ylim()
axes[0].set_ylim(ymin, ymax * 1.3)

plt.tight_layout(pad=0.4)
plt.savefig("figures/fig_instruct.png", dpi=300, bbox_inches="tight")
plt.savefig("figures/fig_instruct.pdf", bbox_inches="tight")
plt.show()
