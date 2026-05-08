import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datasets import load_dataset

# Load Psych-201 dataset and count participants
ds = load_dataset('marcelbinz/Psych-201')['train']
print(ds)
df = ds.to_pandas()
print(f"Columns: {list(df.columns)}")
n_participants = len(df)
print(f"Psych-201 participants: {n_participants}")
print(f"Psych-201 participants (in thousands): {n_participants / 1000:.3f}")

# Count responses ("<<" occurrences in text column)
n_responses = df['text'].str.count('<<').sum()
print(f"Psych-201 responses: {n_responses}")
print(f"Psych-201 responses (in millions): {n_responses / 1e6:.3f}")

# Count unique experiments
n_experiments = df['experiment'].nunique()
print(f"Psych-201 unique experiments: {n_experiments}")

# Load embeddings
embeddings_dict = np.load('experiment_embeddings.npy', allow_pickle=True).item()
studies = embeddings_dict['studies']
pca_embeddings = embeddings_dict['pca']

# Get is_psych101 for each study
study_to_psych101 = df.groupby('study')['is_psych101'].first().to_dict()

# Load experiment categories
categories_df = pd.read_csv('../csvs/psych_experiment_categories.csv')
category_cols = [c for c in categories_df.columns if c not in ['experiment', 'dataset']]

# Map each experiment to its primary category
def get_category(row):
    for cat in category_cols:
        if row[cat] == 1:
            return cat
    return 'Other'

categories_df['category'] = categories_df.apply(get_category, axis=1)
exp_to_category = dict(zip(categories_df['experiment'], categories_df['category']))

# Science figure formatting (matching plot.py)
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

# Full page width: 6.85in
fig, axes = plt.subplots(2, 2, figsize=(6.85, 4.5))

# Subplot 1: Participants
# https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2823295
axes[0, 0].bar(['Normal study', 'Mega-study', 'Psych-101', 'Psych-201'], [0.195, 15.715, 60.92, n_participants / 1000], color=['C3', 'C2', 'C1', 'C0'])
axes[0, 0].set_ylabel('Number of participants\n(in thousands)')
axes[0, 0].set_title('Participants')
axes[0, 0].set_xticks(range(4))
axes[0, 0].set_xticklabels(['Normal study', 'Mega-study', 'Psych-101', 'Psych-201'], rotation=45, ha='right')
axes[0, 0].grid(True, alpha=0.3, linewidth=0.5)

# Subplot 2: PCA embeddings - symbols for Psych-101/201, colors for category
pca_coords = np.array([pca_embeddings[s] for s in studies])

# Map study names to experiment names (replace / with -)
study_to_exp = {s: s.replace('/', '-') for s in studies}
categories = [exp_to_category.get(study_to_exp[s], 'Other') for s in studies]
is_psych101 = [study_to_psych101.get(s, False) for s in studies]

# Colors: orange for Psych-101, blue for Psych-201
for psych101, color, label in [(True, 'C1', 'Psych-101'), (False, 'C0', 'Psych-201')]:
    mask = [p == psych101 for p in is_psych101]
    axes[0, 1].scatter(pca_coords[mask, 0], pca_coords[mask, 1], color=color, alpha=0.7, s=10, label=label)

axes[0, 1].set_xlabel('PC1')
axes[0, 1].set_ylabel('PC2')
axes[0, 1].set_title('Experiment embeddings')
axes[0, 1].legend(frameon=False)
axes[0, 1].grid(True, alpha=0.3, linewidth=0.5)

# Subplot 3: Age histogram
ages = df['age'][df['age'] != 'N/A'].astype(float)
axes[1, 0].hist(ages, bins=30, color='C0', edgecolor='white', linewidth=0.3)
axes[1, 0].set_xlabel('Age')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_title('Age')
axes[1, 0].grid(True, alpha=0.3, linewidth=0.5)

# Subplot 4: Nationality
nationalities = df['nationality'][df['nationality'] != 'N/A']
nationality_counts = nationalities.value_counts().head(20)
axes[1, 1].bar(range(len(nationality_counts)), nationality_counts.values, color='C0')
axes[1, 1].set_xticks(range(len(nationality_counts)))
axes[1, 1].set_xticklabels(nationality_counts.index, rotation=90, ha='center')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_title('Nationality')
axes[1, 1].grid(True, alpha=0.3, linewidth=0.5)

plt.tight_layout(pad=0.4)
plt.savefig('figures/fig_stats.png', dpi=300, bbox_inches='tight')
plt.savefig('figures/fig_stats.pdf', bbox_inches='tight')
plt.show()
