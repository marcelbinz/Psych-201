import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../csvs/full_data_jureca_data.csv")
s = df.groupby(["directory", "experiment", "model"])["nll"].mean().groupby(["directory", "model"]).mean()
print(s.sort_index().to_string())

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

def model_type(name: str):
    n = name.lower()

    if n.startswith("allenai-olmo-"):
        if "instruct" in n:
            return "Instruct"
        if "think" in n:
            return "Think"
        return "Base"

    if n.startswith("qwen-qwen2.5") or n.startswith("deepseek-ai-deepseek-r1-distill-qwen"):
        if "deepseek-ai" in n:
            return "Reasoning"
        if "-coder-" in n:
            return "Code"
        if "-math-" in n:
            return "Math"
        if "-vl-" in n:
            return "Vision"
        if "instruct" in n:
            return "Instruct"
        return "Base"

    if n.startswith("qwen-qwen3-"):
        if "instruct" in n:
            return "Vision Instruct"
        if "thinking" in n:
            return "Vision Thinking"
        if "base" in n:
            return "Base"
        return "Reasoning"

    if "llama" in n:
        if "deepseek" in n:
            return "Reasoning"
        if "vision" in n:
            return "Vision"
        if "instruct" in n:
            return "Instruct"
        return "Base"

data["size_b"] = data["model"].apply(parse_size_b)
data["type"] = data["model"].apply(model_type)
data = data.dropna(subset=["size_b"])

# Drop Math
data = data[data["type"] != "Math"]

# --- Effect size computation (Cohen's d per experiment, then averaged) ---
PAIRS = [
    # (post-trained, base, post-training type)
    # Qwen1.5
    ("Qwen-Qwen1.5-0.5B-Chat.pth", "Qwen-Qwen1.5-0.5B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-1.8B-Chat.pth", "Qwen-Qwen1.5-1.8B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-4B-Chat.pth", "Qwen-Qwen1.5-4B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-7B-Chat.pth", "Qwen-Qwen1.5-7B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-14B-Chat.pth", "Qwen-Qwen1.5-14B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-32B-Chat.pth", "Qwen-Qwen1.5-32B.pth", "Instruction-tuned"),
    ("Qwen-Qwen1.5-72B-Chat.pth", "Qwen-Qwen1.5-72B.pth", "Instruction-tuned"),
    # Qwen2
    ("Qwen-Qwen2-0.5B-Instruct.pth", "Qwen-Qwen2-0.5B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2-1.5B-Instruct.pth", "Qwen-Qwen2-1.5B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2-7B-Instruct.pth", "Qwen-Qwen2-7B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2-72B-Instruct.pth", "Qwen-Qwen2-72B.pth", "Instruction-tuned"),
    # Qwen2.5
    ("Qwen-Qwen2.5-0.5B-Instruct.pth", "Qwen-Qwen2.5-0.5B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-1.5B-Instruct.pth", "Qwen-Qwen2.5-1.5B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-3B-Instruct.pth", "Qwen-Qwen2.5-3B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-7B-Instruct.pth", "Qwen-Qwen2.5-7B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-14B-Instruct.pth", "Qwen-Qwen2.5-14B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-32B-Instruct.pth", "Qwen-Qwen2.5-32B.pth", "Instruction-tuned"),
    ("Qwen-Qwen2.5-72B-Instruct.pth", "Qwen-Qwen2.5-72B.pth", "Instruction-tuned"),
    # Qwen2.5 Code
    ("Qwen-Qwen2.5-Coder-0.5B.pth", "Qwen-Qwen2.5-0.5B.pth", "Code"),
    ("Qwen-Qwen2.5-Coder-1.5B.pth", "Qwen-Qwen2.5-1.5B.pth", "Code"),
    ("Qwen-Qwen2.5-Coder-3B.pth", "Qwen-Qwen2.5-3B.pth", "Code"),
    ("Qwen-Qwen2.5-Coder-7B.pth", "Qwen-Qwen2.5-7B.pth", "Code"),
    ("Qwen-Qwen2.5-Coder-14B.pth", "Qwen-Qwen2.5-14B.pth", "Code"),
    ("Qwen-Qwen2.5-Coder-32B.pth", "Qwen-Qwen2.5-32B.pth", "Code"),
    # Qwen2.5 Math
    ("Qwen-Qwen2.5-Math-1.5B.pth", "Qwen-Qwen2.5-1.5B.pth", "Math"),
    ("Qwen-Qwen2.5-Math-7B.pth", "Qwen-Qwen2.5-7B.pth", "Math"),
    ("Qwen-Qwen2.5-Math-72B.pth", "Qwen-Qwen2.5-72B.pth", "Math"),
    # Qwen2.5 Vision
    ("Qwen-Qwen2.5-VL-3B-Instruct.pth", "Qwen-Qwen2.5-3B.pth", "Vision"),
    ("Qwen-Qwen2.5-VL-7B-Instruct.pth", "Qwen-Qwen2.5-7B.pth", "Vision"),
    ("Qwen-Qwen2.5-VL-32B-Instruct.pth", "Qwen-Qwen2.5-32B.pth", "Vision"),
    ("Qwen-Qwen2.5-VL-72B-Instruct.pth", "Qwen-Qwen2.5-72B.pth", "Vision"),
    # DeepSeek R1 Distill Qwen
    ("deepseek-ai-DeepSeek-R1-Distill-Qwen-1.5B.pth", "Qwen-Qwen2.5-1.5B.pth", "Reasoning"),
    ("deepseek-ai-DeepSeek-R1-Distill-Qwen-7B.pth", "Qwen-Qwen2.5-7B.pth", "Reasoning"),
    ("deepseek-ai-DeepSeek-R1-Distill-Qwen-14B.pth", "Qwen-Qwen2.5-14B.pth", "Reasoning"),
    ("deepseek-ai-DeepSeek-R1-Distill-Qwen-32B.pth", "Qwen-Qwen2.5-32B.pth", "Reasoning"),
    # Qwen3
    ("Qwen-Qwen3-0.6B.pth", "Qwen-Qwen3-0.6B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3-1.7B.pth", "Qwen-Qwen3-1.7B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3-4B.pth", "Qwen-Qwen3-4B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3-8B.pth", "Qwen-Qwen3-8B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3-14B.pth", "Qwen-Qwen3-14B-Base.pth", "Reasoning"),
    # Qwen3.5
    ("Qwen-Qwen3.5-0.8B.pth", "Qwen-Qwen3.5-0.8B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3.5-2B.pth", "Qwen-Qwen3.5-2B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3.5-4B.pth", "Qwen-Qwen3.5-4B-Base.pth", "Reasoning"),
    ("Qwen-Qwen3.5-9B.pth", "Qwen-Qwen3.5-9B-Base.pth", "Reasoning"),
    # Qwen3 VL
    ("Qwen-Qwen3-VL-2B-Instruct.pth", "Qwen-Qwen3-1.7B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-4B-Instruct.pth", "Qwen-Qwen3-4B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-8B-Instruct.pth", "Qwen-Qwen3-8B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-32B-Instruct.pth", "Qwen-Qwen3-14B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-2B-Thinking.pth", "Qwen-Qwen3-1.7B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-4B-Thinking.pth", "Qwen-Qwen3-4B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-8B-Thinking.pth", "Qwen-Qwen3-8B-Base.pth", "Vision"),
    ("Qwen-Qwen3-VL-32B-Thinking.pth", "Qwen-Qwen3-14B-Base.pth", "Vision"),
    # OLMo
    ("allenai-Olmo-3-7B-Instruct.pth", "allenai-Olmo-3-1025-7B.pth", "Instruction-tuned"),
    ("allenai-Olmo-3.1-32B-Instruct.pth", "allenai-Olmo-3-1125-32B.pth", "Instruction-tuned"),
    ("allenai-Olmo-3-7B-Think.pth", "allenai-Olmo-3-1025-7B.pth", "Reasoning"),
    ("allenai-Olmo-3.1-32B-Think.pth", "allenai-Olmo-3-1125-32B.pth", "Reasoning"),
    # Llama
    ("meta-llama-Meta-Llama-3-8B-Instruct.pth", "meta-llama-Meta-Llama-3-8B.pth", "Instruction-tuned"),
    ("meta-llama-Llama-3.1-8B-Instruct.pth", "meta-llama-Llama-3.1-8B.pth", "Instruction-tuned"),
    ("meta-llama-Llama-3.1-70B-Instruct.pth", "meta-llama-Llama-3.1-70B.pth", "Instruction-tuned"),
    ("meta-llama-Llama-3.2-1B-Instruct.pth", "meta-llama-Llama-3.2-1B.pth", "Instruction-tuned"),
    ("meta-llama-Llama-3.2-3B-Instruct.pth", "meta-llama-Llama-3.2-3B.pth", "Instruction-tuned"),
    # DeepSeek R1 Distill Llama
    ("deepseek-ai-DeepSeek-R1-Distill-Llama-8B.pth", "meta-llama-Llama-3.1-8B.pth", "Reasoning"),
    ("deepseek-ai-DeepSeek-R1-Distill-Llama-70B.pth", "meta-llama-Llama-3.1-70B.pth", "Reasoning"),
    # Llama Vision
    ("unsloth-Llama-3.2-11B-Vision.pth", "meta-llama-Llama-3.1-8B.pth", "Vision"),
    ("unsloth-Llama-3.2-90B-Vision.pth", "meta-llama-Llama-3.1-70B.pth", "Vision"),
]

# Compute Cohen's d per experiment, then average across experiments
effect_records = []
for post_model, base_model, pt_type in PAIRS:
    base_data = df[df["model"] == base_model]
    post_data = df[df["model"] == post_model]
    if base_data.empty or post_data.empty:
        print(f"WARNING: missing data for {post_model} or {base_model}")
        continue
    base_by_exp = base_data.groupby("experiment")["nll"]
    post_by_exp = post_data.groupby("experiment")["nll"]
    common = base_by_exp.mean().index.intersection(post_by_exp.mean().index)
    if len(common) < 2:
        continue
    base_mean = base_by_exp.mean().loc[common]
    base_sd = base_by_exp.std().loc[common]
    post_mean = post_by_exp.mean().loc[common]
    post_sd = post_by_exp.std().loc[common]
    pooled_sd = np.sqrt((base_sd**2 + post_sd**2) / 2)
    cohen_d = (post_mean - base_mean) / pooled_sd
    d = cohen_d.mean()
    effect_records.append({
        "post_model": post_model, "base_model": base_model,
        "type": pt_type, "cohens_d": d,
    })

es_df = pd.DataFrame(effect_records)
print("\n=== Per-model-pair effect sizes (Cohen's d, positive = worse than base) ===")
print(es_df[["post_model", "type", "cohens_d"]].to_string(index=False))

# Average across model pairs within each post-training type
type_avg = es_df.groupby("type")["cohens_d"].mean()
print("\n=== Average Cohen's d by post-training type ===")
print(type_avg.to_string())

# Split
is_olmo = data["model"].str.startswith("allenai-Olmo")
olmo_data = data[is_olmo].copy()
# is_qwen25 = data["model"].str.startswith("Qwen-Qwen2.5") | data["model"].str.startswith("deepseek-ai-DeepSeek-R1-Distill-Qwen")
# qwen25_data = data[is_qwen25].copy()
is_qwen3 = data["model"].str.startswith("Qwen-Qwen3-")
qwen3_data = data[is_qwen3].copy()
is_llama = data["model"].str.lower().str.contains("llama")
llama_data = data[is_llama].copy()

pivot_olmo = (
    olmo_data.pivot_table(index="size_b", columns="type", values="value", aggfunc="mean")
    .sort_index()
)
pivot_qwen3 = (
    qwen3_data.pivot_table(index="size_b", columns="type", values="value", aggfunc="mean")
    .sort_index()
)
pivot_llama = (
    llama_data.pivot_table(index="size_b", columns="type", values="value", aggfunc="mean")
    .sort_index()
)

type_colors = {
    "Base": "C0",
    "Instruct": "C1",
    "Reasoning": "C2",
    "Think": "C2",
    "Vision": "C3",
    "Vision Instruct": "C3",
    "Vision Thinking": "C4",
    "Code": "C5",
}

# Science figure formatting
# Full width: 174mm = 6.85in, single col: 55mm = 2.17in, 1.5 col: 120mm = 4.72in
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

fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, sharey=True,
                                      figsize=(6.85, 2.0))

# Qwen3 models
for col in pivot_qwen3.columns:
    y = pivot_qwen3[col].dropna()
    ax1.plot(y.index, y.values, marker="o", label=col, color=type_colors.get(col))

ax1.set_xscale("log")
ax1.set_title("Qwen3")
ax1.set_xlabel("Parameters (billions)")
ax1.set_ylabel("Negative log-likelihood (↓)")
ax1.grid(True, alpha=0.3, linewidth=0.5)
ax1.legend(frameon=False)

# OLMo
for col in pivot_olmo.columns:
    y = pivot_olmo[col].dropna()
    ax2.plot(y.index, y.values, marker="o", label=col, color=type_colors.get(col))

ax2.set_xscale("log")
ax2.set_title("Olmo3.X")
ax2.set_xlabel("Parameters (billions)")
ax2.grid(True, alpha=0.3, linewidth=0.5)
ax2.legend(frameon=False)

# Llama models
for col in pivot_llama.columns:
    y = pivot_llama[col].dropna()
    ax3.plot(y.index, y.values, marker="o", label=col, color=type_colors.get(col))

ax3.set_xscale("log")
ax3.set_title("Llama3.X")
ax3.set_xlabel("Parameters (billions)")
ax3.grid(True, alpha=0.3, linewidth=0.5)
ax3.legend(frameon=False)

plt.tight_layout(pad=0.4)
plt.savefig("figures/fig2.png", dpi=300, bbox_inches="tight")
plt.savefig("figures/fig2.pdf", bbox_inches="tight")
plt.show()
