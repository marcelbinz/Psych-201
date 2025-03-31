import os
import sys
import pandas as pd
import jsonlines


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils import randomized_choice_options

# Load data
script_dir = os.path.dirname(os.path.abspath(__file__))
file1 = os.path.join(script_dir, "armed_bandit_2023-04-28_out.csv")
file2 = os.path.join(script_dir, "armed_bandit_2023-06-02_out.csv")
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

df_all = pd.concat([df1, df2], ignore_index=True)

# Group the data by participant and session
groups = df_all.groupby(["participant.code", "session.code"])

# Fixed instructions text for the multi-armed bandit task
instructions = (
    "In this task, five buttons will be displayed on the screen, and on each trial you have to select one of the five buttons by clicking on it. "
    "Each time you select a button, you earn some points. Buttons differ from one another in the average points that they yield. "
    "There will be 20 trials in the practice block and 40 in each of the remaining 4 blocks.\n\n"
    "Note that after each click the system needs about one second to process your entry. "
    "The average payout from each button remains the same within each block, but may change from one block to the next.\n\n"
    "At the end of each block, you'll get feedback about how many points you earned in that block. "
    "The first block will be for practice, but the points you earn from the remaining 4 blocks will be used to determine your bonus payment for this task. "
    "For this task, you will be paid a bonus of 1 pence (£0.01) per 100 points."
)

all_prompts = []

# Process each experimental session
for (participant_code, session_code), df_session in groups:
    # Sort trials by block then by trial number
    df_session = df_session.sort_values(by=["block", "trial"])

    # Randomize the button names for this session
    choice_options = randomized_choice_options(num_choices=5)
    displayed_buttons = ", ".join(choice_options)

    # Start building the prompt text
    prompt_text = instructions + "\n\n"
    prompt_text += f"For this session, the available buttons are: {displayed_buttons}.\n\n"

    # Get the unique block numbers (Block 1 is practice; blocks 2-5 are incentivized)
    blocks = sorted(df_session["block"].unique())

    for block in blocks:
        df_block = df_session[df_session["block"] == block]
        # Compute cumulative points for this block (assumed in field "player.payoff.1")
        cumulative_points = df_block["player.payoff.1"].cumsum().tolist()

        if block == 1:
            prompt_text += "Practice Block:\n\n"
        else:
            prompt_text += f"Incentivized Block {block - 1}:\n\n"

        # Iterate over trials in the block
        for i, (_, row) in enumerate(df_block.iterrows()):
            trial_num = int(row["trial"])
            points = int(row["player.payoff.1"])
            cumulative = int(cumulative_points[i])

            # Use the participant's selection (assumed 1-indexed) to get the chosen button
            selection = int(row["player.selection"])
            try:
                chosen_button = choice_options[selection - 1]
            except IndexError:
                chosen_button = f"Option{selection}"

            trial_line = (
                f"Trial {trial_num}: You selected <<{chosen_button}>> and received {points} points. "
                f"Total points: {cumulative}.\n"
            )
            prompt_text += trial_line

        prompt_text += "\n"

    prompt_text += "End of session.\n"

    # Create prompt dictionary for this session
    prompt_dict = {
        "text": prompt_text,
        "experiment": "multi_armed_bandit",
        "participant": participant_code,
        "session": session_code
    }
    all_prompts.append(prompt_dict)

output_file = os.path.join(script_dir, "prompts.jsonl")
with jsonlines.open(output_file, mode='w') as writer:
    writer.write_all(all_prompts)

print(f"Created {len(all_prompts)} prompt(s) in {output_file}.")