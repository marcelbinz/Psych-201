import numpy as np
import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel
import torch

# Load Psych-201 dataset
print("Loading dataset...")
ds = load_dataset('marcelbinz/Psych-201')['train']
df = ds.to_pandas()

# Get first data point for each experiment/study
print("Extracting first data point per study...")
first_per_study = df.groupby('study').first().reset_index()

# Extract text until first "<<"
def extract_text(text):
    if '<<' in text:
        return text.split('<<')[0].strip()
    return text.strip()

first_per_study['text_clean'] = first_per_study['text'].apply(extract_text)

# Load ModernBERT
print("Loading ModernBERT...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = AutoTokenizer.from_pretrained('answerdotai/ModernBERT-base')
model = AutoModel.from_pretrained('answerdotai/ModernBERT-base').to(device)
model.eval()

# Generate embeddings
print("Generating embeddings...")
embeddings = []
studies = []

with torch.no_grad():
    for idx, row in first_per_study.iterrows():
        text = row['text_clean']
        study = row['study']

        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512).to(device)
        outputs = model(**inputs)

        # Use mean pooling over token embeddings
        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy().squeeze()
        embeddings.append(embedding)
        studies.append(study)

        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1}/{len(first_per_study)} studies")

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import umap

embeddings = np.array(embeddings)
print(f"Embeddings shape: {embeddings.shape}")

# PCA
print("Running PCA...")
pca = PCA(n_components=2)
embeddings_pca = pca.fit_transform(embeddings)

# t-SNE
print("Running t-SNE...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
embeddings_tsne = tsne.fit_transform(embeddings)

# UMAP
print("Running UMAP...")
reducer = umap.UMAP(n_components=2, random_state=42)
embeddings_umap = reducer.fit_transform(embeddings)

# Save as dict mapping study -> embeddings
embeddings_dict = {
    'studies': studies,
    'raw': {study: emb for study, emb in zip(studies, embeddings)},
    'pca': {study: emb for study, emb in zip(studies, embeddings_pca)},
    'tsne': {study: emb for study, emb in zip(studies, embeddings_tsne)},
    'umap': {study: emb for study, emb in zip(studies, embeddings_umap)},
}
print(f"Generated embeddings for {len(studies)} studies")

np.save('experiment_embeddings.npy', embeddings_dict)
print("Saved embeddings dict to experiment_embeddings.npy")
