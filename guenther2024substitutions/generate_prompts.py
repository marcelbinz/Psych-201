import pandas as pd
import jsonlines

# load data
exp1 = pd.read_csv("substitutions_experiment1_cleaned.csv")
exp2 = pd.read_csv("substitutions_experiment2_cleaned.csv")
exp_replication = pd.read_csv("substitutions_replication_cleaned.csv")

# create empty list to store all prompts
all_prompts = []

################
# Experiment 1 #
################
# Define number of participants and trials
participants_exp1 = exp1["participant"].unique()
trials_exp1 = range(exp1["trial_index"].max() + 1)

# define initial prompt
instruction1 = 'In this experiment, you will be presented with different single words and asked to find substitutes for them.\n'\
    'Later, in another experiment, we will ask other people to guess the original words based on what you will come up with.\n'\
    'Your task is to refer to a given word without using this word.\n'\
    'You can imagine yourself in a situation where the use of a word is banned or censored, or you have forgotten it, but you still want to tell another person exactly what you mean.\n'\
    'Important hints and tips\n'\
    'Note that you are not restricted to existing words. You may use any other one-word expression you like and be as creative as you want.\n'\
    'Here are examples of how you can substitute some words, but you are not restricted to these ways:\n'\
    'for zebra, you might write tigerhorse\n'\
    'for despair, you might write anti-hope\n'\
    'for tomcat, you might write meowboy\n'\
    'for wine, you might write grapecohol\n'\
    'for Jesus, you might write Christ\n'\
    'Keep in mind that it is very important that other people are able to guess your original word specifically, and nothing else. Please try to come up with an expression that would allude to the given word as clearly as possible.\n'\
    'An association or even a synonym might not help other people understand what was meant:\n'\
    'for earring, jewelry is not a great substitute, because other people might then also guess bracelet or ring\n'\
    'for tiger, lion is not a great substitute, because other people might then also guess cat or leopard\n'\
    'There are no right or wrong answers. We are interested in what you will come up with. Please do not look up anything. This would distort the results of our study.\n'\
    'Please note that the "Continue" button will be blocked within first 3 seconds of each trial. Do not be confused, this is just a measure to prevent random quick answers.\n'\
    'You will be presented with no more than 50 words. The study will take about 15 minutes to complete.\n'\
    'Please note that you will not be able to return to earlier answers.\n'

# Experiment1: Generate individual prompts for participants
for participant in participants_exp1:
    exp1_participant = exp1[exp1["participant"] == participant]
    participant = participant.item()
    age = exp1_participant["age"].iloc[0].item()
    individual_prompt = instruction1
    rt_list = []
    for trial in trials_exp1:
        exp1_trial = exp1_participant.loc[exp1_participant["trial_index"] == trial]
        if not exp1_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp1_trial["stimulus"].iloc[0]
            response = exp1_trial["response"].iloc[0]
            datapoint = f"{stimulus}. You enter <<{response}>>.\n"
            individual_prompt += datapoint
    individual_prompt += "\n"
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024substitutions/experiment1",
            "participant": participant,
            "age": age,
        }
    )

#################
# Experiment 2  #
#################
# Define number of participants and trials
participants_exp2 = exp2["participant"].unique()
trials_exp2 = range(exp1["trial_index"].max() + 1)

# define initial prompt
instruction2 = 'In this experiment, you will be presented with different single words and asked to find substitutes for them.\n'\
    'Later, in another experiment, we will ask other people to guess the original words based on what you will come up with.\n'\
    'Your task is to refer to a given word without using this word.\n'\
    'You can imagine yourself in a situation where the use of a word is banned or censored, or you have forgotten it, but you still want to tell another person exactly what you mean.\n'\
    'Important hints and tips\n'\
    'In three different blocks, you will be instructed whether you need to use either an existing, novel combined word or a completely made-up word.\n'\
    'Here are examples of how you may substitute with these types of words:\n'\
    'Existing words:\n'\
    'for Jesus, you might write Christ\n'\
    'for flower, you might write floret\n'\
    'Novel combined words:\n'\
    'for zebra, you might write tigerhorse\n'\
    'for despair, you might write anti-hope\n'\
    'for tomcat, you might write meowboy\n'\
    'Completely made-up words:\n'\
    'for wine, you might write grapecohol\n'\
    'for student, you might write teachee\n'\
    '... and many others! Here you are not limited to a specific way of making up a word! However, in this category, please do not use words that are just a combination of two existing words!\n'\
    'A simple association or even a synonym might not help other people understand what was meant:\n'\
    'for earring, jewelry is not a great substitute, because other people might then also guess bracelet or ring\n'\
    'for tiger, lion is not a great substitute, because other people might then also guess cat or leopard\n'\
    'Keep in mind that it is very important that other people are able to guess your original word specifically, and nothing else. Please try to come up with an expression that would allude to the given word as clearly as possible.\n'\
    'Please also note that you are not allowed to use a word that contains the original word (such as lion for lioness).\n'\
    'There are no right or wrong answers. We are interested in what you will come up with. Please do not look up anything. This would distort the results of our study.\n'\
    'Please note that the "Continue" button will be blocked within first 3 seconds of each trial. Do not be confused, this is just a measure to prevent random quick answers.\n'\
    'You will be presented with no more than 50 words. The study will take about 20 minutes to complete.\n'\
    'Please note that you will not be able to return to earlier answers.\n'\
    'Existing words\n'\
    'In this block, please use only existing words as responses.\n'\
    'Examples: "apple", "despair", "flower", etc.\n'\
    'Please type in a one-word substitute for the word\n'\
    'Use an existing word\n'\
    'Novel combined words\n'\
    'In this block, please use only new combinations of two existing words as responses.\n'\
    'Examples: "tigerhorse", "meowboy", "anti-hope", etc.\n'\
    'Please type in a one-word substitute for the word\n'\
    'Use a novel combined word\n'\
    'Completely novel words\n'\
    'In this block, please use only completely novel words as responses.\n'\
    'You can use any new words unless they are just a combination of two existing words.\n'\
    'Examples: "grapecohol", "teachee", "awaying", "splishes", "gubber", etc.\n'\
    'Please type in a one-word substitute for the word\n'\
    'Use a completely made-up word\n'

# Experiment2: Generate individual prompts for participants
for participant in participants_exp2:
    exp2_participant = exp2[exp2["participant"] == participant]
    participant = participant.item()
    age = exp2_participant["age"].iloc[0].item()
    individual_prompt = instruction2
    rt_list = []
    for trial in trials_exp2:
        exp2_trial = exp2_participant.loc[exp2_participant["trial_index"] == trial]
        if not exp2_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp2_trial["stimulus"].iloc[0]
            response = exp2_trial["response"].iloc[0]
            datapoint = f"{stimulus}. You enter <<{response}>>.\n"
            individual_prompt += datapoint
    individual_prompt += "\n"
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024substitutions/experiment2",
            "participant": participant,
            "age": age,
        }
    )


#############################
# Experiment 3: Replication #
#############################
# Define number of participants and trials
participants_exp_replication = exp_replication["participant"].unique()
trials_exp_replication = range(exp_replication["trial_index"].max() + 1)

instruction_replication = 'In this experiment, you will be presented with different single words and asked to find substitutes for them.\n'\
    'Later, in another experiment, we will ask other people to guess the original words based on what you will come up with.\n'\
    'Your task is to refer to a given word without using this word.\n'\
    'You can imagine yourself in a situation where the use of a word is banned or censored, or you have forgotten it, but you still want to tell another person exactly what you mean.\n'\
    'Important hints and tips\n'\
    'Note that you are not restricted to existing words. You may use any other one-word expression you like and be as creative as you want.\n'\
    'Here are examples of how you can substitute some words, but you are not restricted to these ways:\n'\
    '- for zebra, you might write tigerhorse\n'\
    '- for despair, you might write anti-hope\n'\
    '- for tomcat, you might write meowboy\n'\
    '- for wine, you might write grapecohol\n'\
    '- for Jesus, you might write Christ\n'\
    'Keep in mind that it is very important that other people are able to guess your original word specifically, and nothing else. Please try to come up with an expression that would allude to the given word as clearly as possible.\n'\
    'An association or even a synonym might not help other people understand what was meant:\n'\
    '- for earring, jewelry is not a great substitute, because other people might then also guess bracelet or ring\n'\
    '- for tiger, lion is not a great substitute, because other people might then also guess cat or leopard\n'\
    'There are no right or wrong answers. We are interested in what you will come up with. Please do not look up anything. This would distort the results of our study.\n'\
    'Please note that the "Continue" button will be blocked within first 3 seconds of each trial. Do not be confused, this is just a measure to prevent random quick answers.\n'\
    'You will be presented with no more than 50 words. The study will take about 15 minutes to complete.\n'\
    'Please note that you will not be able to return to earlier answers.'


for participant in participants_exp_replication:
    exp_replication_participant = exp_replication[exp_replication["participant"] == participant]
    participant = participant.item()
    age = exp_replication_participant["age"].iloc[0].item()
    individual_prompt = instruction_replication
    rt_list = []
    for trial in trials_exp_replication:
        exp_replication_trial = exp_replication_participant.loc[exp_replication_participant["trial_index"] == trial]
        if not exp_replication_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_replication_trial["stimulus"].iloc[0]
            response = exp_replication_trial["response"].iloc[0]
            datapoint = f"{stimulus}. You enter <<{response}>>.\n"
            individual_prompt += datapoint
    individual_prompt += "\n"
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024substitutions/replication",
            "participant": participant,
            "age": age,
        }
    )


# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
