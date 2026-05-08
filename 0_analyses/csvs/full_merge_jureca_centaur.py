import os
from glob import glob
import torch
import pandas as pd

if __name__ == '__main__':

    data_models = [
        "-p-project1-hai_1196-hf-hub-models--marcelbinz--Llama-3.1-Centaur-70B-adapter-snapshots-159600db8be99dc183c289923148dfd96cbd8e07-.pth",
        "-p-project1-hai_1196-hf-hub-models--unsloth--Meta-Llama-3.1-70B-bnb-4bit-snapshots-a009b8db2439814febe725486a5ed388f12a8744-.pth",
    ]

    configs = [
        ("data",         data_models,         "full_data_jureca_data_centaur.csv"),
    ]
    experiments = glob('../data/*')

    for base_dir, models, out_file in configs:
        data = []
        for experiment in experiments:
            print(experiment)
            exp_name = os.path.basename(experiment)
            for fname in models:
                path = os.path.join('..', base_dir, exp_name, fname)
                try:
                    nlls = torch.load(path, map_location="cpu")
                    for participant, values in nlls.items():
                        for trial, nll in enumerate(values.tolist()):
                            data.append([base_dir, experiment, fname, participant, trial, nll])
                except:
                    print("Not found", base_dir, experiment, fname)
            print()

        df = pd.DataFrame(data, columns=['directory', 'experiment', 'model', 'participant', 'trial', 'nll'])
        print(df)
        print(df.groupby(['directory', 'model'])['nll'].mean())
        df.to_csv(out_file, index=False)
