import sys
import jsonlines
import numpy as np
import pandas as pd
from tqdm import tqdm
sys.path.append("..")
from utils import randomized_choice_options

json_out = []
CHARACTER_LIMIT = 120000

df = pd.read_csv("exp1.csv")

instructions = (
    "You are playing the role of a musician living in a fantasy land.\n"
    "You play the flute for gold coins to an audience of genies, who live inside magic lamps on Pink Mountain and Blue Mountain.\n"
    "Pink Mountain has genies {alien_0} and {alien_1}, and Blue Mountain has genies {alien_2} and {alien_3}.\n"
    "Each genie lives in a lamp with the corresponding letter on it.\n"
    "When you arrive on a mountain, you can pick up a lamp and rub it.\n"
    "If the genie is in the mood for music, he will come out of his lamp, listen to a song, and give you a gold coin.\n"
    "Each genie’s interest in music changes with time.\n"
    "To go to the mountains, you chose one of two magic carpets, which you purchase from a magician, who enchants them to fly.\n"
    "Magic carpet {spaceship_0} generally flies to Pink Mountain, and magic carpet {spaceship_1} generally flies to Blue Mountain.\n"
    "However, on rare occasions a strong wind blowing from that mountain makes flying there too dangerous because the wind might blow you off the carpet.\n"
    "In this case, the carpet is forced to land instead on the other mountain.\n"
    "You can take a magic carpet or pick up a lamp and rub it by pressing the corresponding key.\n"
    "Your goal is to get as many coins as possible over the next {n_trials} days.\n\n"
)
for participant in tqdm(df.participant.unique()):
    (
        spaceship_0,
        spaceship_1,
        planet_0,
        planet_1,
        alien_0,
        alien_1,
        alien_2,
        alien_3,
    ) = randomized_choice_options(8)
    par_instructions = instructions.format(
        spaceship_0=spaceship_0,
        spaceship_1=spaceship_1,
        planet_0=planet_0,
        planet_1=planet_1,
        alien_0=alien_0,
        alien_1=alien_1,
        alien_2=alien_2,
        alien_3=alien_3,
        n_trials=int(
            df[df.participant == participant].trial.nunique() / 2
        ),  # because two step
    )
    par_dict = {"text": par_instructions, "experiment": 'feher2020humans/exp1.csv', "participant": str(participant)}
    # iterate every two trials
    par_df = df[df.participant == participant].reset_index(drop=True)
    for trial in range(0, par_df.trial.nunique(), 2):
        # select the current two trials
        # by row number
        first_step_df = par_df.iloc[trial, :]

        # map state_left and state_right to spaceship_0 and spaceship_1
        # except leave -1 as -1
        first_step_df["state_left"] = pd.Series(
            {
                -1: "-1",
                0: spaceship_0,
                1: spaceship_1,
            }
        ).get(first_step_df["state_left"], first_step_df["state_left"])
        first_step_df["state_right"] = pd.Series(
            {
                -1: "-1",
                0: spaceship_0,
                1: spaceship_1,
            }
        ).get(first_step_df["state_right"], first_step_df["state_right"])
        # mape choice_1 to spaceship_0 and spaceship_1
        # except leave -1 as -1
        first_step_df["choice"] = pd.Series(
            {
                -1: "-1",
                0: spaceship_0,
                1: spaceship_1,
            }
        ).get(first_step_df["choice"], first_step_df["choice"])

        second_step_df = par_df.iloc[trial + 1, :]
        second_step_df = second_step_df.to_frame().T

        second_step_df.loc[second_step_df["current_state"] == -1, "current_state"] = -1
        second_step_df.loc[
            second_step_df["current_state"] == 0, "current_state"
        ] = planet_0
        second_step_df.loc[
            second_step_df["current_state"] == 1, "current_state"
        ] = planet_1

        # if current_state is -1, assign -1 to state_left and state_right
        # if current_state is 0, assign alien_0 and alien_1 to state_left and state_right
        # if current_state is 1, assign alien_2 and alien_3 to state_left and state_right
        second_step_df.loc[second_step_df["current_state"] == -1, "state_left"] = -1
        second_step_df.loc[second_step_df["current_state"] == -1, "state_right"] = -1
        second_step_df.loc[
            second_step_df["current_state"] == planet_0, "state_left"
        ] = alien_0
        second_step_df.loc[
            second_step_df["current_state"] == planet_0, "state_right"
        ] = alien_1
        second_step_df.loc[
            second_step_df["current_state"] == planet_1, "state_left"
        ] = alien_2
        second_step_df.loc[
            second_step_df["current_state"] == planet_1, "state_right"
        ] = alien_3

        second_step_df.loc[
            (second_step_df["current_state"] == planet_0)
            & (second_step_df["choice"] == 0),
            "choice",
        ] = alien_0
        second_step_df.loc[
            (second_step_df["current_state"] == planet_0)
            & (second_step_df["choice"] == 1),
            "choice",
        ] = alien_1
        second_step_df.loc[
            (second_step_df["current_state"] == planet_1)
            & (second_step_df["choice"] == 0),
            "choice",
        ] = alien_2
        second_step_df.loc[
            (second_step_df["current_state"] == planet_1)
            & (second_step_df["choice"] == 1),
            "choice",
        ] = alien_3

        spaceship_left = first_step_df.state_left
        spaceship_right = first_step_df.state_right
        choice_1 = first_step_df.choice
        planet_landed = second_step_df.current_state.values[0]
        planet_left = second_step_df.state_left.values[0]
        planet_right = second_step_df.state_right.values[0]
        choice_2 = second_step_df.choice.values[0]
        reward = second_step_df.reward.values[0]

        par_text = f"You are presented with magic carpets {spaceship_left} and {spaceship_right}."
        # not sure what is going on with types, so here we are
        if choice_1 in [-1, "-1"]:
            par_text += " You do not respond in time for this day. You do not go to any mountain. You do not get any coins.\n"
            par_dict["text"] += par_text
            continue

        if planet_landed == planet_0:
            par_text += (
                f" You press <<{choice_1}>>."
                f" You end up on Pink Mountain."
                f" You see lamp {planet_left} and lamp {planet_right}."
            )
        elif planet_landed == planet_1:
            par_text += (
                f" You press <<{choice_1}>>."
                f" You end up on Blue Mountain."
                f" You see lamp {planet_left} and lamp {planet_right}."
            )
        else:
            print("should not happen")

        if choice_2 in [-1, "-1"]:
            par_text += " You do not respond in time for this day. You do not play any music. You do not get any coins.\n"
            par_dict["text"] += par_text
            continue

        par_text += (
            f" You rub lamp <<{choice_2}>>."
            f" You receive {int(reward)} coins.\n"
        )

        par_dict["text"] += par_text

    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    # assert there is no {-1} in the text
    assert (
        "{-1}" not in par_dict["text"]
    ), f"Participant {participant} has {-1} in the text."

    par_dict["text"] = par_dict["text"][:-1]
    json_out.append(par_dict)


with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)
