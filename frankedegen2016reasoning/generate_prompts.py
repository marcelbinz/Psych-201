import random
import sys
import jsonlines
import pandas as pd
from tqdm import tqdm
sys.path.append("..")
from utils import randomized_choice_options
json_out = []
CHARACTER_LIMIT = 32000


  ###Experiment1


df = pd.read_csv("pone.0154854.s007.csv", sep='\t')

# general task instructions
task_instructions = (
    "In this experiment, you will see images of different situations and answer questions about them.\n"
    "On each trial you will see a display of three creatures (monsters or robots) with different accessories (hats or scarves).\n"
    "At the top of the display you will see a message that was sent by a previous participant who saw the same display as you and was instructed to get you to pick out one of the creatures.\n"
    "Your task is to choose the creature you think the previous participant intended you to pick by pressing a key corresponding to it.\n\n"
)

#every trial instruction
instructions_trial = (
    "The previous participant said:	{message}\n"
    "Images of creatures: \n"
    "{letter_1}: {image_1}\n"
    "{letter_2}: {image_2}\n"
    "{letter_3}: {image_3}\n\n"
    "Choose the creature you think the previous participant intended you to pick by pressing the corresponding key.\n"
    "Remember that the participant could only say one of these things:\n"
    "\"purple monster\"\n"
    "\"green monster\"\n"
    "\"red hat\"\n"
    "\"blue hat\"\n"
    "Your answer: {response}.\n"
)

# possible messages and two feature dimensions
messages = ["purple monster", "green monster", "red hat", "blue hat"]
set_1 = {"purple monster", "green monster", "robot"}
set_2 = {"red hat", "blue hat", "scarf"}


#go over participants
for participant in tqdm(df.workerid.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'frankedegen2016reasoning-exp1', "participant": str(participant)}
    RT = []
    #reindex and drop the old index
    par_df = df[df.workerid == participant].reset_index(drop=True)
    # iterate over trials
    for _, trial in par_df.iterrows():
        # retrieve the response_type, the trial type and generate the message
        response_type = trial["response"]
        condition = trial["condition"]
        message = random.choice(messages)

        #for simple trials generate the target, competitor and distractor according to the procedure in the paper
        if condition == ("simple"):
            # depending on in which dimension the message is
            if message in set_1:
                target = message + " with a scarf"
                competitor_obj = random.choice(list(set_2.difference({"scarf"})))
                distractor_obj = set_2.difference({"scarf", competitor_obj}).pop()
                competitor = message + " with a " + competitor_obj
                distractor = random.choice(list(set_1.difference({message}))) + " with a " + distractor_obj
            else:
                target = "robot with a " + message
                competitor_obj = random.choice(list(set_1.difference({"robot"})))
                distractor_obj = set_1.difference({"robot", competitor_obj}).pop()
                competitor = competitor_obj + " with a " + message
                distractor = distractor_obj + " with a " + random.choice(list(set_2.difference({message})))
        #same for the complex trials with the slightly different procedure described in the paper
        elif condition == "complex":
            # depending on the message dimension as well
            if message in set_1:
                target_obj = random.choice(list(set_2.difference({"scarf"})))
                target = message + " with a " + target_obj
                competitor_obj = set_2.difference({"scarf", target_obj}).pop()
                competitor = message + " with a " + competitor_obj
                distractor = "robot with a " + target_obj
            else:
                target_obj = random.choice(list(set_1.difference({"robot"})))
                target = target_obj + " with a " + message
                competitor_obj = set_1.difference({"robot", target_obj}).pop()
                competitor = competitor_obj + " with a " + message
                distractor = target_obj + " with a scarf"
        # skip the filer trials
        else:
            continue

        #append reaction the time
        RT.append(trial["rt"])

        # generate by-participant randomization of keys that correspond to the forced-choice options
        (
            obj_1,
            obj_2,
            obj_3
        ) = randomized_choice_options(3)
        obj_list = [obj_1, obj_2, obj_3]

        # create a list of images and randomly shuffle it
        pictures = [target, distractor, competitor]
        random.shuffle(pictures)

        # find the index of the response in the list
        if response_type == "target":
            response_idx = pictures.index(target)
        elif response_type == "competitor":
            response_idx = pictures.index(competitor)
        else:
            response_idx = pictures.index(distractor)

        # find the key corresponding to the response
        response = obj_list[response_idx]


        #fill the parameters to the trial outputs
        trial_instuction = instructions_trial.format(
            message=message,
            letter_1 = obj_1,
            letter_2 = obj_2,
            letter_3 = obj_3,
            image_1 = pictures[0],
            image_2 = pictures[1],
            image_3 = pictures[2],
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"

    # check that the prompt is not too long
    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"
    # append reaction times and z scores
    par_dict["RTs"] = RT

    json_out.append(par_dict)

  ###Experiment2


df = pd.read_csv("pone.0154854.s008.csv", sep='\t')

# general task instructions
task_instructions = (
    "In this experiment, you will see images of different situations and answer questions about them.\n"
    "On each trial you will see a display of three creatures (monsters or robots) with different accessories (hats or scarves).\n"
    "One of them will be highlighted.\n"
    "Your task is to get another worker to pick out the highlighted creature by sending one of four possible messages.\n\n"
)

#every trial instruction
instructions_trial = (
    "You see the following creatures:\n"
    "{creature_1}\n"
    "{creature_2}\n"
    "{creature_3}\n"
    "Highlighted creature: {creature}\n\n"
    "Your task is to get another worker to pick out the highlighted creature.\n"
    "It's not highlighted on their display.\n"
    "Choose one of the following four messages to send it to the other worker and get them to pick out the right creature."
    "The other worker knows you can only send these messages:\n"
    "{letter_1}: {message_1}\n"
    "{letter_2}: {message_2}\n"
    "{letter_3}: {message_3}\n"
    "{letter_4}: {message_4}\n"
    "Your answer: {response}.\n"
)

# possible messages and two feature dimensions
messages = ["purple monster", "green monster", "red hat", "blue hat"]
set_1 = {"purple monster", "green monster", "robot"}
set_2 = {"red hat", "blue hat", "scarf"}


#go over participants
for participant in tqdm(df.workerid.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'frankedegen2016reasoning-exp2', "participant": str(participant)}
    RT = []
    #reindex and drop the old index
    par_df = df[df.workerid == participant].reset_index(drop=True)
    # iterate over trials
    for _, trial in par_df.iterrows():
        # retrieve the response_type, the trial type and generate the target message
        response_type = trial["response"]
        condition = trial["condition"]
        target = random.choice(messages)

        #for simple trials generate the target, competitor and distractor images and messages according to the procedure in the paper
        if condition == ("simple"):
            # depending on in which dimension the message is
            if target in set_1:
                competitor = random.choice(list(set_2.difference({"scarf"})))
                target_image = target + " with a " + competitor
                competitor_image = "robot with a " + competitor
                distractors = [set_1.difference({"robot", target}).pop(), set_2.difference({"scarf", competitor}).pop()]
                distractor_image = distractors[0] + " with a " + distractors[1]
            else:
                competitor = random.choice(list(set_1.difference({"robot"})))
                target_image = competitor + " with a " + target
                competitor_image = competitor + " with a scarf"
                distractors = [set_1.difference({"robot", competitor}).pop(), set_2.difference({"scarf", target}).pop()]
                distractor_image = distractors[0] + " with a " + distractors[1]
        #same for the complex trials with the slightly different procedure described in the paper
        elif condition == "complex":
            # depending on the message dimension as well
            if target in set_1:
                competitor = random.choice(list(set_2.difference({"scarf"})))
                target_image = target + " with a " + competitor
                competitor_image = "robot with a " + competitor
                distractors = [set_1.difference({"robot", target}).pop(), set_2.difference({"scarf", competitor}).pop()]
                distractor_image = target + " with a " + distractors[1]
            else:
                competitor = random.choice(list(set_1.difference({"robot"})))
                target_image = competitor + " with a " + target
                competitor_image = competitor + " with a scarf"
                distractors = [set_1.difference({"robot", competitor}).pop(), set_2.difference({"scarf", target}).pop()]
                distractor_image = distractors[0] + " with a " + target
        # skip the filer trials
        else:
            continue

        # create a list of creatures and shuffle it
        creatures = [target_image, competitor_image, distractor_image]
        random.shuffle(creatures)

        #append reaction the time
        RT.append(trial["rt"])

        # generate by-participant randomization of keys that correspond to the forced-choice options
        (
            obj_1,
            obj_2,
            obj_3,
            obj_4
        ) = randomized_choice_options(4)
        obj_list = [obj_1, obj_2, obj_3, obj_4]

        # shuffle the messages
        random.shuffle(messages)

        # find the index of the response in the list
        if response_type == "target":
            response_idx = messages.index(target)
        elif response_type == "competitor":
            response_idx = messages.index(competitor)
        else:
            distractor = random.choice(distractors)
            response_idx = messages.index(distractor)

        # find the key corresponding to the response
        response = obj_list[response_idx]


        #fill the parameters to the trial outputs
        trial_instruction = instructions_trial.format(
            creature_1 = creatures[0],
            creature_2 = creatures[1],
            creature_3 = creatures[2],
            creature = target_image,
            letter_1 = obj_1,
            letter_2 = obj_2,
            letter_3 = obj_3,
            letter_4 = obj_4,
            message_1 = messages[0],
            message_2 = messages[1],
            message_3 = messages[2],
            message_4 = messages[3],
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instruction + "\n"

    # check that the prompt is not too long
    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"
    # append reaction times
    par_dict["RTs"] = RT

    json_out.append(par_dict)


# Save output to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)
