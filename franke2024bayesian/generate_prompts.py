import sys
import jsonlines
import numpy as np
import pandas as pd
from tqdm import tqdm
sys.path.append("..")
from utils import randomized_choice_options

json_out = []
CHARACTER_LIMIT = 120000

df = pd.read_csv("data-raw-human.csv")
trials = pd.read_csv("results.csv")
df_full = pd.merge(df, trials, on=["trial"])

# left join the full trial information to the human results
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "There will be two parts, each with 2 trials.\n"
    "In each trial, you will read a short description of a task and are asked to answer a question by pressing a key that indicates the answer.\n\n"
)

instructions_production = (
    "Your task is to play a conversation game. There are three objects that you and your friend can see. You have to choose a single word to identify one of the three objects for your friend. The three objects are:\n"
    "{object_1}\n"
    "{object_2}\n"
    "{object_3}\n\n"
    "Your task is to make your friend pick out the following target object:\n"
    "the {trigger}\n\n"
    "Which of the following words do you choose:\n"
    "{utt_1}: {utterance_1}\n"
    "{utt_2}: {utterance_2}\n"
    "{utt_3}: {utterance_3}\n"
    "{utt_4}: {utterance_4}\n\n"
    "Your answer:\n"
    "I would choose the word corresponding to key {response}."
)

instructions_listener = (
    "Your task is to play a conversation game. There are three objects that you and your friend can see. Your friend wants to communicate about one of these objects. Your friend selects a single word. Your task is to guess which object your friend is trying to refer to. The three objects are:\n"
    "{obj_1}: {object_1}\n"
    "{obj_2}: {object_2}\n"
    "{obj_3}: {object_3}\n\n"
    "Your friend can choose from the following list of words:\n"
    "{utterance_1}\n"
    "{utterance_2}\n"
    "{utterance_3}\n"
    "{utterance_4}\n\n"
    "Your friend chose the word:\n"
    "the {trigger}\n\n"
    "Which object do you think your friend is trying to refer to?\n\n"
    "Your answer:\n"
    "My friend wants to refer to the object corresponding to key {response}."
)

for participant in tqdm(df.submission_id.unique()):
    par_dict = {"text": task_instructions, "experiment": 'franke2024bayesian/data-raw-human.csv', "participant": str(participant)}
    par_RTs = []
    # generate by-participant randomization of keys that correspond to the forced-choice options
    (
        obj_1,
        obj_2,
        obj_3
    ) = randomized_choice_options(3)
    obj_list = [obj_1, obj_2, obj_3]
    (
        utt_1,
        utt_2,
        utt_3,
        utt_4
    ) = randomized_choice_options(4)
    utt_list = [utt_1, utt_2, utt_3, utt_4]
    # get participant's trials
    par_df = df_full[df_full.submission_id == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # get the order of target, distractor, competitor and the respective uttrances in the trial
        object_order = [trial["interpretation_index_target"], trial["interpretation_index_competitor"], trial["interpretation_index_distractor"]]
        utterance_order = [trial["production_index_target"], trial["production_index_competitor"], trial["production_index_distractor1"], trial["production_index_distractor2"]]
        objects = [None, None, None]
        utterances = [None, None, None, None]
        for ind, o in list(zip(object_order, ["interpretation_target", "interpretation_competitor", "interpretation_distractor"])):
            objects[ind] = trial[o]
        for ind, u in list(zip(utterance_order, ["production_target", "production_competitor", "production_distractor1", "production_distractor2"])):
            utterances[ind] = trial[u]
        # retrieve the key corresponding to the provided response via retrieving the index in the list
        response = trial["response"]

        if trial["condition"] == "interpretation":
            # the initial determiner needs to be removed
            resp_index = objects.index(" ".join(response.split(" ")[1:])) 
            response_key = obj_list[resp_index]
            trial_instuction = instructions_listener.format(
                obj_1=obj_1,
                obj_2=obj_2,
                obj_3=obj_3,
                object_1=objects[0],
                object_2=objects[1],
                object_3=objects[2],
                utterance_1=utterances[0],
                utterance_2=utterances[1],
                utterance_3=utterances[2],
                utterance_4=utterances[3],
                trigger=trial["trigger_word"],
                response=f"<<{response_key}>>"
            )
        elif trial["condition"] == "production":
            utt_index = utterances.index(response)
            response_key = utt_list[utt_index]
            trial_instuction = instructions_production.format(
                utt_1=utt_1,
                utt_2=utt_2,
                utt_3=utt_3,
                utt_4=utt_4,
                object_1=objects[0],
                object_2=objects[1],
                object_3=objects[2],
                utterance_1=utterances[0],
                utterance_2=utterances[1],
                utterance_3=utterances[2],
                utterance_4=utterances[3],
                trigger=trial["trigger_object"],
                response=f"<<{response_key}>>"
            )
        else:
            continue
        par_RTs.append(trial["responseTime"])
        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"
    # append reaction times    
    par_dict["RTs"] = par_RTs

    # check that the prompt is not too long
    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    json_out.append(par_dict)


with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)
