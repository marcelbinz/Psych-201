import sys
import jsonlines
import pandas as pd
from tqdm import tqdm
sys.path.append("..")

json_out = []
CHARACTER_LIMIT = 32000


   ###Experiment 1a



df = pd.read_csv("exp1a.csv")

# general task instructions
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "There will be 10 displays of the same task.\n"
    "In each task trial you will read a short description of a task and will be asked to answer a question by typing a response.\n"
    "After seeing a certain amount of black and red circles on the screen, you will be asked to complete a sentence of the form “— are red”\n\n"
    "Please, do NOT write numbers or number words!\n\n"
)

#every trial instruction
instructions_trial= (
    "You see {red} red circles among 432 circles in total. How many of the circles are red? Please complete a sentence of form “— are red”\n"
    "Your answer: {response} are red.\n"
)

#go over participants
for participant in tqdm(df.SUBJECT.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'vantiel2020probabilistic_pragmatics/exp1a.csv', "participant": str(participant)}
    #reindex and drop the old index
    par_df = df[df.SUBJECT == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # retrieve the key corresponding to the provided response and number of the red circles by retrieving the indices in the list
        response = trial["RESP"]
        red = trial["DOTS"]

        #fill the parameters to the trial outputs
        trial_instuction = instructions_trial.format(
            red=red,
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"

    # check that the prompt is not too long
    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    json_out.append(par_dict)


    ###Experiment 1b




df = pd.read_csv("exp1b.csv")

# general task instructions
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "There will be 10 displays of the same task.\n"
    "In each task trial you will read a short description of a task and will be asked to answer a question by typing a response.\n"
    "After seeing a certain amount of black and red circles on the screen, you will be asked to complete a sentence of the form “— are red”\n\n"
    "Please, do NOT write numbers or number words!\n\n"
)

#every trial instruction
instructions_trial= (
    "You see {red} red circles among 432 circles in total. How many of the circles are red? Please complete a sentence of form “— are red”\n"
    "Your answer: {response} are red.\n"
)

#go over participants
for participant in tqdm(df.SUBJECT.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'vantiel2020probabilistic_pragmatics/exp1b.csv', "participant": str(participant)}
    #reindex and drop the old index
    par_df = df[df.SUBJECT == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # retrieve the key corresponding to the provided response and number of the red circles by retrieving the indices in the list
        response = trial["RESP"]
        red = trial["DOTS"]

        #fill the parameters to the trial outputs
        trial_instuction = instructions_trial.format(
            red=red,
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"

    # check that the prompt is not too long
    assert (
        len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    json_out.append(par_dict)


    ###Experiment 2a

    # dictionary for the pairs of predicates
dictionary = {
    "is from California": "is from San Francisco",
    "saw an insect": "saw a cockroach",
    "read a novel": "read 'Moby Dick'",
    "saw a bird": "saw an eagle",
    "played a card game": "played poker",
    "used a herb": "used rosemary",
    "is from Texas": "is from Houston",
    "ordered fish": "ordered salmon",
    "ordered meat": "ordered steak",
    "ate a fruit": "ate an apple",
    "drank alcohol": "drank wine",
    "bought a flower": "bought a rose",
    "owns a pet": "owns a dog",
    "owns a vehicle": "owns a truck",
    "owns a weapon": "owns a sword",
    "saw an animal": "saw a lion",
    "travelled to Japan": "travelled to Tokyo",
    "ate vegetables": "ate carrots",
    "bought a gemstone": "bought a diamond",
    "was drinking a soda": "was drinking a Pepsi",
    "watched a movie": "watched 'Pulp Fiction'",
    "saw a tree": "saw an oak",
    "travelled to Russia": "travelled to Moscow",
    "travelled to France": "travelled to Paris",
    "is from Illinois": "is from Chicago"
}

# read a file
df = pd.read_csv("exp2a.csv", delimiter=' ')

# general task instructions
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "There will be 50 trials of the same task.\n"
    "In each trial, you will read a statement (premise) and a possible conclusion.\n"
    "Your task is to decide whether the premise implies the conclusion.\n"
    "Please select ‘1' on the keyboard if the conclusion is true based on the statement or ‘0' if it does not necessarily follow.\n"
    "For example: ¨Dorothy ate salmon¨ implies that ¨Dorothy ate fish¨ since salmon is a fish.\n"
    "But at the same time: ¨Dorothy ate fish¨ doesn't imply ¨Dorothy ate salmon¨ since not all fish is salmon.\n\n"
)

# every trial instruction
instructions_trial = (
    "Please indicate whether the premise ¨Dorothy {premise}¨ implies the conclusion ¨Dorothy {conclusion}¨. Please type 1 for Yes and 0 for No.\n"
    "Your answer: {response}\n"
)
# go over participants
for participant in tqdm(df.subject.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'vantiel2020probabilistic_pragmatics/exp2a.csv',
                "participant": str(participant)}
    RT = []
    # reindex and drop the old index
    par_df = df[df.subject == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # retrieve the keys corresponding to the provided response, trial type, predicate and reaction type
        response = trial["response"]
        type = trial["type"]
        pred = trial["predicate"]
        RT.append(trial["rt"])

        # align premise and conclusion with respond to the type, retrieving the strong statement from the dictionary
        if type == "strong_to_weak":
            premise = dictionary[pred]
            conclusion = pred
        else:
            conclusion = dictionary[pred]
            premise = pred

        # fill the parameters to the trial outputs
        trial_instuction = instructions_trial.format(
            premise=premise,
            conclusion=conclusion,
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"

    # check that the prompt is not too long
    assert (
            len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    # append reaction times
    par_dict["RTs"] = RT

    json_out.append(par_dict)





        ###Experiment 2b



#set of the quantifiers without "of the" part
our_set={"few", "very few", "hardly any", "many", "some", "a few", "several"}


# dictionary for the pairs of predicates
dictionary = {
    "are from California": "are from San Francisco",
    "saw an insect": "saw a cockroach",
    "read a novel": "read 'Moby Dick'",
    "saw a bird": "saw an eagle",
    "played a card game": "played poker",
    "used a herb": "used rosemary",
    "are from Texas": "are from Houston",
    "ordered fish": "ordered salmon",
    "ordered meat": "ordered steak",
    "ate a fruit": "ate an apple",
    "drank alcohol": "drank wine",
    "bought a flower": "bought a rose",
    "own a pet": "own a dog",
    "own a vehicle": "own a truck",
    "own a weapon": "own a sword",
    "saw an animal": "saw a lion",
    "travelled to Japan": "travelled to Tokyo",
    "ate vegetables": "ate carrots",
    "bought a gemstone": "bought a diamond",
    "were drinking a soda": "were drinking a Pepsi",
    "watched a movie": "watched 'Pulp Fiction'",
    "saw a tree": "saw an oak",
    "travelled to Russia": "travelled to Moscow",
    "travelled to France": "travelled to Paris",
    "are from Illinois": "are from Chicago"
}

# read a file
df = pd.read_csv("exp2b.csv", delimiter=' ')

# general task instructions
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "There will be 34 trials of the same task.\n"
    "In each trial, you will read a statement (premise) and a possible conclusion.\n"
    "Your task is to decide whether the premise implies the conclusion.\n"
    "Please select ‘1' on the keyboard if the conclusion is true based on the statement or ‘0' if it does not necessarily follow.\n"
    "For example: ¨All guests ate salmon.¨ implies that ¨All guests ate fish.¨ since salmon is a type fish.\n"
    "But at the same time: ¨All guests ate fish.¨ doesn't imply ¨All guests ate salmon.¨ since not all fish is salmon.\n\n"
)

# every trial instruction
instructions_trial = (
    "Please indicate whether the premise ¨{quantifier} people {premise}¨ implies the conclusion ¨{quantifier} people {conclusion}¨. Please type 1 for Yes and 0 for No.\n"
    "Your answer: {response}\n"
)
# go over participants
for participant in tqdm(df.subject.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'vantiel2020probabilistic_pragmatics/exp2b.csv',
                "participant": str(participant)}
    RT = []
    # reindex and drop the old index
    par_df = df[df.subject == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # retrieve the keys corresponding to the provided response, trial type, predicate, quantifier and reaction type
        response = trial["response"]
        type = trial["type"]
        pred = trial["predicate"]
        quantifier = trial["quantifier"]
        RT.append(trial["rt"])

        #quantifier adjustment
        if quantifier not in our_set:
            quantifier += " of the"
        quantifier = quantifier.capitalize()

        # align premise and conclusion with respond to the type, retrieving the strong statement from the dictionary
        if type == "strong_to_weak":
            premise = dictionary[pred]
            conclusion = pred
        else:
            conclusion = dictionary[pred]
            premise = pred

        # fill the parameters to the trial outputs
        trial_instuction = instructions_trial.format(
            premise=premise,
            quantifier = quantifier,
            conclusion=conclusion,
            response=f"<<{response}>>"
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instuction + "\n"

    # check that the prompt is not too long
    assert (
            len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    # append reaction times
    par_dict["RTs"] = RT

    json_out.append(par_dict)



    ###Experiment 3



df = pd.read_csv("exp3.csv")

# add the general task instructions
task_instructions = (
    "Thank you for participating in this experiment!\n"
    "The experiment begins with two practice trials followed by 24 trials of the same main task.\n"
    "In each trial, you will see a display with a mix of black and red circles.\n"
    "Your task is to estimate what percentage of the total circles are red.\n"
    "You will use a slider to indicate your estimate. The slider starts at 50%, but you can adjust it both ways.\n"
    "Try to be as accurate as possible.\n\n"
)

# add every trial instructions
instructions_trial = (
    "What percentage of the circles are red? You see {red} red circles among 432 circles in total.\n"
    "Your estimate: {response}.\n"
)

for participant in tqdm(df.submission_id.unique()):
    # create a future json entry for the participant
    par_dict = {"text": task_instructions, "experiment": 'vantiel2020-probabilistic_pragrmatics/exp3.csv',
                "participant": str(participant)}
    # reindex and drop the old index
    par_df = df[df.submission_id == participant].reset_index(drop=True)
    # iterate over trials, construct interpretation and production instructions
    for _, trial in par_df.iterrows():
        # retrieve the key corresponding to the provided response and number of red circles by retrieving the
        # indices in the list
        response = int(trial["rating_slider"] / 4.32)
        red = trial["dots_number"]

        # fill the parameters to the trial outputs
        trial_instruction = instructions_trial.format(
            response=f"<<{response}%>>",
            red=red
        )

        # append trial prompt to participant's recording
        par_dict["text"] += trial_instruction + "\n"

    # check that the prompt is not too long
    assert (
            len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    json_out.append(par_dict)




    ###Experiment 4




# Load the dataset for Experiment 4
df = pd.read_csv("exp4.csv")

# Set of quantifiers that should not include "of the"
our_set = {"Few", "Very few", "Hardly any", "Many", "Some", "A few", "Several"}

# General task instructions
task_instructions = (
    "Thank you for participating in the experiment!\n\n"
    "In this study, you will be presented with a series of trials.\n"
    "In each trial, you will see a display of red and black circles, \n"
    "along with a statement about the distribution of colors (e.g., 'Half of the circles are black').\n"
    "Your task is to evaluate how well the statement describes the display \n "
    "by adjusting a slider ranging from 0 to 100.\n\n"
)

# Instructions for each trial
instructions_trial = (
    "You see {dots} red circles among 432 circles in total.\n"
    "How well does this statement describe the display?\n"
    "Statement: \"{formatted_quantifier} circles are red.\"\n"
    "Your rating: {response}\n\n"
)


# Iterate over participants
for participant in tqdm(df['subject'].unique()):
    # Create a JSON entry for each participant
    par_dict = {"text": task_instructions, "experiment": 'exp4.csv', "participant": str(participant)}

    # Filter data for the current participant
    par_df = df[df['subject'] == participant].reset_index(drop=True)

    # Iterate over trials for this participant
    for _, trial in par_df.iterrows():
        quantifier = trial["quantifier"]
        dots = trial["dots"]
        response = trial["dep"]

        # Adjust quantifier format based on the defined set
        if quantifier not in our_set:
            quantifier = f"{quantifier} of the"
        formatted_quantifier = quantifier

        # Format trial instruction
        trial_instruction = instructions_trial.format(
            dots=dots,
            formatted_quantifier=formatted_quantifier,
            response=f"<<{response}>>"
        )

        # Append trial data to participant's record
        par_dict["text"] += trial_instruction

    # Ensure character limit is not exceeded
    assert (
            len(par_dict["text"]) < CHARACTER_LIMIT
    ), f"Participant {participant} has too many characters: ({len(par_dict['text'])})"

    json_out.append(par_dict)

# Save output to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(json_out)
