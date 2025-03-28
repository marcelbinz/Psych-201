import pandas as pd
import jsonlines
import sys
import textwrap
sys.path.append("..")

datasets = ["nasioulas2024feedback_data.csv"]
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)

    for participant, df_participant in df.groupby('SUB'):
        RTs = []

        # Extract participant-level values once
        age = df_participant.at[df_participant.index[0], "age"]
        nationality = df_participant.at[df_participant.index[0], "nationality"]
        num_blocks = df_participant["BLOCK"].max() + 1

        # Ensure unique values for specific columns
        for col in ["EXP", "typeOfFeedback", "sureThing", "blockInstructions"]:
            if df_participant[col].nunique() != 1:
                raise ValueError(f"Error: {col} should have a unique value!")

        exp = df_participant.at[df_participant.index[0], "EXP"]
        tof = df_participant.at[df_participant.index[0], "typeOfFeedback"]
        sureThing = df_participant.at[df_participant.index[0], "sureThing"]
        block_instructions = df_participant.at[df_participant.index[0], "blockInstructions"]


        text1 = textwrap.dedent("""\
            Let's consider the following example: (50pts, 70%; 0pts) vs (37pts, 100%).
            In this example, if you choose the left option (L), you will gain 50 points with probability 70% and 0pts with 30%.
            If you choose the right option (R), you will gain 37 points with probability 100%."""
                                ) if sureThing == 1 else textwrap.dedent("""\
            Let's consider the following example: (50pts, 30%; 0pts) vs (17pts, 50%; 15pts).
            In this example, if you choose the left option (L), you will gain 50 points with probability 30% and 0 points with probability 70%. 
            If you choose the right option (R), you will gain either 17 points or 15 points with probability 50% for each outcome."""
                                                                         )

        text4 = "At the end of the experiment, one round among all the rounds of the actual experiment will be selected randomly to determine the bonus you will get."

        text5 = textwrap.dedent("""\
            End of Training. You are about to start the actual experiment.
            Recall that one of the rounds of the experiment will be randomly selected to determine your final monetary bonus,
            and that this round can be one in which the outcomes are not revealed. 
            The outcome of the chosen option in this randomly selected round will determine your bonus. 
            Each round is equally important for the final payment."""
                                )

        if exp == 7:  # Losses involved
            text1 = textwrap.dedent("""\
                Note that the obtained outcome can be positive (gains), negative (losses), or zero.
                Let's consider the following example: (50pts, 70%; 0pts) vs (37pts, 100%).
                In this example, if you choose the left option (L) you will gain 50 points with probability 70% and 0pts with probability 30%. 
                If you choose the right option (R), you will gain 37 points with probability 100%.
                Now, let's consider another example: (-15pts, 30%; 0pts) vs (-5pts, 100%).
                In this example, if you choose the left option (L) you will lose 15 points with probability 30% and 0pts with probability 70%. 
                If you choose the right option (R), you will lose 5 points with probability 100%."""
                                    )

            text4 = textwrap.dedent("""\
            At the end of the experiment, your bonus will be determined based on your total points (total gains - total losses).
            Hence, your goal is to maximize your number of points in the gain domain and to minimize the number of losses."""
                                    )

            text5 = textwrap.dedent("""\
                        End of Training. You are about to start the actual experiment.
                        Recall that your bonus will be determined based on your total points (total gains - total losses) and that all rounds from now on count (regardless of whether your obtained outcome is revealed to you or not). 
                        Hence, your goal is to maximize your number of points in the gain domain and to minimize your number of points in the loss domain."""
                                    )

        text2 = (textwrap.dedent("""\
                In some rounds (after you choose one option, the lottery is played and you obtain an outcome), the obtained outcome will be revealed to you.
                In some other rounds (after you choose one option, the lottery is played and you obtain an outcome), the obtained outcome will not be revealed to you."""
                                 )
                 if tof == "partial"
                 else textwrap.dedent("""\
                In some rounds (after you choose one option, the lottery is played and you obtain an outcome), the obtained outcome will be displayed with the tag Obtained Outcome. Additionally, the outcome you would have won by choosing the other option will be displayed with the tag Forgone Outcome. 
                In some other rounds (after you choose one option, the lottery is played and you obtain an outcome), the outcomes will not be revealed."""
                                      )
                 )

        if block_instructions == 1:
            text3 = ("At the beginning of each block, you will be informed whether the obtained outcome is revealed or not after each choice in this block."
                     if tof == "partial"
                     else "At the beginning of each block, you will be informed whether the outcomes are revealed or not after each choice in this block." )
        else:
            text3 = "You will be notified at the beginning of each block."

        prompt_parts = [
            "You will face several decision problems. Each problem consists of two options.",
            "In each round, you can select one of the two options by pressing L or R, for choosing the Left or the Right option, respectively, appearing on your screen.",
            "In each round, after you choose one option, a lottery is played with the indicated probability and points. This lottery determines your obtained outcome in this round.",
            text1, text2,
            textwrap.dedent("""\
                This experiment is composed of two main phases: a training phase, so that you get acclimated with the task, and the actual experiment.
                Both phases are made up of blocks.
                {} 
                Then, you will play several rounds of the same decision problem - so the options within each block will be the same. Yet, their position (L or R) can change.
                At the end of each block, an 'End of Block' message will appear.
                Afterward, you will be moved to the next block.""".format(text3)
                ),
            textwrap.dedent("""\
                In addition to the fixed participation fee, you can earn a bonus based on your choices.
                {}  
                Rounds in which the obtained outcome is not revealed can also be selected to determine your bonus.
                On the other hand, rounds of the training phase cannot be selected and do NOT determine your bonus.
                Please note: each round is equally important for the final payment.""".format(text4)
                ),
            "You are now starting the training phase (these rounds do not affect the final bonus)."
        ]

        startedTestPhase = 0
        for block, df_block in df_participant.groupby("BLOCK"):
            num_trials = df_block["TRIAL"].max() + 1
            feedback = df_block.at[df_block.index[0], "FEEDBACK"]
            valence = df_block.at[df_block.index[0], "VALENCE"]

            if startedTestPhase == 0 and df_block.at[df_block.index[0], "training"] == 0:
                prompt_parts.append(text5)
                startedTestPhase = 1


            block_text = f"Block {block}:"

            if block_instructions:
                block_text += "\n"
                block_text += ("The obtained outcome is revealed after each choice in this block."
                               if feedback else "The obtained outcome is NOT revealed after each choice in this block.") \
                    if tof == "partial" else \
                    ("The outcomes (of both the chosen and the unchosen option) are revealed after each choice in this block."
                     if feedback else "The outcomes are NOT revealed after each choice in this block.")

            prompt_parts.append(block_text)

            for _, df_trial in df_block.groupby("TRIAL"):
                # Extract trial-specific values efficiently
                magRisky = df_trial.at[df_trial.index[0], "magRisky"]
                pRisky = df_trial.at[df_trial.index[0], "pRisky"]
                magSafe1 = df_trial.at[df_trial.index[0], "magSafe1"]
                magSafe2 = df_trial.at[df_trial.index[0], "magSafe2"]
                pSafe = df_trial.at[df_trial.index[0], "pSafe"]
                inv = df_trial.at[df_trial.index[0], "INV"]
                lr = df_trial.at[df_trial.index[0], "LR"]
                outcome = int(df_trial.at[df_trial.index[0], "OUT"])
                cfoutcome = df_trial.at[df_trial.index[0], "CF_OUT"]
                rtime = df_trial.at[df_trial.index[0], "RTIME"]

                if pd.notna(cfoutcome):
                    cfoutcome = int(cfoutcome)

                if valence == 0:
                    pRisky = 100 - pRisky

                safe_option = f"({magSafe1}pts, 50%; {magSafe2}pts, 50%)" if sureThing == 0 else f"({magSafe1}pts, 100%)"
                risky_option = f"({magRisky}pts, {pRisky}%; 0pts)"
                option1, option2 = (safe_option, risky_option) if inv else (risky_option, safe_option)

                # Decision statement
                trial_text = f"Choose: {option1} vs {option2}. You press {'<<L>>' if lr == 0 else '<<R>>'}."

                # Feedback
                if feedback:
                    trial_text += f" Obtained Outcome = {outcome}."
                    if tof == "complete":
                        trial_text += f" Forgone Outcome = {cfoutcome}."

                prompt_parts.append(trial_text)
                RTs.append(rtime)

        # Join parts 
        final_prompt = "\n".join(prompt_parts)

        all_prompts.append({
            'text': final_prompt,
            'experiment': 'nasioulas2024feedback/exp' + str(exp),
            'participant': int(participant),
            'RTs': [int(rt) for rt in RTs],  # Convert each RT to int
            'age': str(age),
            'nationality': nationality
        })


with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)