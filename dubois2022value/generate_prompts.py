import os
import numpy as np
import pandas as pd
import jsonlines
from tqdm import trange
import sys
sys.path.append("..") # for import of utils from above
from utils import randomized_choice_options

CHARACTER_LIMIT = 32000 * 4  # 32K tokens per prompt is the soft limit


def generate_prompts_horizon(path, datasets: list, verbose: bool = False):
    """
    :param datasets: list of csv files
    :param instruction: string that will be prepended to the generated prompts
    :param verbose: if True, print the character count of each prompt
    """
    all_prompts = []

    for dataset in datasets:
        df = pd.read_csv(dataset)
        num_participants = df.participant.max() + 1

        for participant in trange(num_participants):
            choice_options = randomized_choice_options(num_choices=3)

            prompt = \
                "You are participating in multiple games involving three apple trees, labeled " + choice_options[0] + ", " + choice_options[1] + ", and " + choice_options[2] + ".\n" \
                "The three apple trees are different across different games.\nEach time you choose an apple tree, you get an apple of a given size.\n" \
                "You choose an apple tree by pressing the corresponding key.\n" \
                "Each apple tree tends to provide apples of about the same size on average.\n" \
                "Your goal is to choose the apple trees that will give you the largest apples across the experiment.\n" \
                "The first few trials in each game are instructed trials where you will be told which apple tree to choose.\n" \
                "After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.\n\n"

            df_participant = df[(df['participant'] == participant)]
            num_tasks = df_participant.task.max() + 1

            for task in range(num_tasks):
                df_task = df_participant[(df_participant['task'] == task)]
                num_forced_choices = df_task.forced.sum()

                num_trials = df_task.trial.max() + 1
                prompt += f"Game {task + 1}. There are {num_trials} trials in this game.\n"

                for trial in range(num_trials):
                    df_trial = df_task[(df_task['trial'] == trial)]
                    c = choice_options[df_trial.choice.item()].item()
                    r = df_trial.reward.item()
                    if trial < num_forced_choices:
                        prompt += f"You are instructed to press {c} and get an apple with size {r} centimeters.\n"
                    else:
                        prompt += f"You press <<{c}>> and get an apple with size {r} centimeters.\n"
                prompt += '\n'

            prompt = prompt[:-2]
            if verbose:
                print(prompt[:5000])
                #assert (len(prompt) < CHARACTER_LIMIT), f"Too many characters: ({len(prompt)}) in participant {participant}"
            all_prompts.append({'text': prompt, 'experiment': path + dataset, 'participant': participant})

    with jsonlines.open('prompts.jsonl', 'w') as writer:
        print(f"Writing {len(all_prompts)} prompts to prompts.jsonl")
        writer.write_all(all_prompts)

def test_prompts(file='prompts.jsonl', length=5000):
    with jsonlines.open(file) as reader:
        for i, obj in enumerate(reader):
            if i == 1:
                break
            print(obj['text'][:length])


if __name__ == '__main__':
    files = os.listdir("./")
    datasets = sorted([f for f in files if (f.startswith("exp") and f.endswith(".csv"))])
    print(datasets)
    generate_prompts_horizon('dubois2022value/', datasets, verbose=False)
    test_prompts()
