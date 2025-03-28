import sys

sys.path.append("..")

import numpy as np
import pandas as pd
import jsonlines

from utils import randomized_choice_options

np.random.seed(1234)

prompt = """During this task, you will be presented with pairs of images, each of which is associated with a certain number of points.
In each trial, please select an image. After your selection, points of both images will be revealed to you.
The image on the left can be selected using {left_key}, and the image on the right can be selected using {right_key}.
Your goal is to maximise the total number of points.
The points are associated with the images in a structured way, and they vary from 0 to 100.
There are 60 trials in total.\n"""


def clean_name(name_in):
    """Remove any digits and replace underscores with spaces"""
    name_out = "".join([i for i in name_in if not i.isdigit()])
    return name_out.replace("_", " ")


exp = pd.read_csv("https://osf.io/6exjm/download")

all_prompts = []
for par_no, par in enumerate(exp.participant.unique()):
    left_key, right_key = randomized_choice_options(num_choices=2)
    sub_df = exp[exp.participant == par].reset_index(drop=True)

    current_prompt = prompt.format(left_key=left_key, right_key=right_key)

    for _, row in sub_df.iterrows():
        left_image, right_image = clean_name(row.left_image.split("/")[1]), clean_name(row.right_image.split("/")[1])
        choice = right_key if row.choice else left_key
        current_prompt += f"You were shown {left_image} on the left and {right_image} on the right. You press <<{choice}>> and receive {row.reward_received} points. {left_image} had {row.left_reward} points, and {right_image} had {row.right_reward} points.\n"
    all_prompts.append({"text": current_prompt, "experiment": "demircan2024evaluatingreward", "participant": par_no})

with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
