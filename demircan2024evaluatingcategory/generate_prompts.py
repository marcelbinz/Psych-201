import sys

sys.path.append("..")

import numpy as np
import pandas as pd
import jsonlines

from utils import randomized_choice_options

np.random.seed(1234)

prompt = """Hello! Thanks a lot for helping us today! Your task is to deliver some images to our friends Julty and Folty.
Unfortunately, it has been a while since we hung out with Julty and Folty, and we cannot remember what they like and do not like.
However, we remember that whatever Julty likes, Folty does not like; and whatever Folty likes, Julty does not like.
We will present you with 120 images, one by one. After receiving each image you need to deliver it to either Julty or to Folty.
You can give the image to Julty using the button {left_key}, and to Folty using the button {right_key}.
Once you deliver an image, they tell us whether they enjoyed their image or not. We will pass on the feedback to you.
Hopefully, you can figure out over time which images are more suited for whom.\n"""


def clean_name(name_in):
    """Remove any digits and replace underscores with spaces"""
    name_out = "".join([i for i in name_in if not i.isdigit()])
    return name_out.replace("_", " ")


exp = pd.read_csv("https://osf.io/rsd46/download")

all_prompts = []
for par_no, par in enumerate(exp.participant.unique()):
    left_key, right_key = randomized_choice_options(num_choices=2)
    sub_df = exp[exp.participant == par].reset_index(drop=True)

    current_prompt = prompt.format(left_key=left_key, right_key=right_key)

    for _, row in sub_df.iterrows():
        image = clean_name(row.image.split("/")[1])
        if row.choice:
            choice = right_key
            choice_dino, no_choice_dino = "Folty", "Julty"
        else:
            choice = left_key
            choice_dino, no_choice_dino = "Julty", "Folty"

        feedback_text = f"{choice_dino} loves the image!\n" if row.correct else f"{choice_dino} does not like the image. It was meant for {no_choice_dino}.\n"
        current_prompt += f"You were shown {image}. You press <<{choice}>> to deliver the image to {choice_dino}. {feedback_text}"

    all_prompts.append({"text": current_prompt, "experiment": "demircan2024evaluatingcategory", "participant": par_no})


with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
