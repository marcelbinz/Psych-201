import pandas as pd
import jsonlines


# load data
history = pd.read_csv('Data/ap1_history_experiment_anonymized.csv')
psych1 = pd.read_csv('Data/ap1_psych_experiment1_anonymized.csv')
psych2 = pd.read_csv('Data/ap1_psych_experiment2_anonymized.csv')
psych3 = pd.read_csv('Data/ap1_psych_experiment3_anonymized.csv')
psych4 = pd.read_csv('Data/ap1_psych_experiment4_anonymized.csv')


# Recode Feeling of Rightness and Reread Response
## Feeling of Rightness
### Create a dictionary mapping numbers to scale values
for_scale_dict = {
    1: "Very uncertain",
    2: "Uncertain",
    3: "Rather uncertain",
    4: "Neither certain nor uncertain",
    5: "Rather certain",
    6: "Certain",
    7: "Very certain"
}

### Map using the dictionary
history['for_resp_factor'] = history['for_resp_factor'].map(for_scale_dict)
psych1['for_resp_factor'] = psych1['for_resp_factor'].map(for_scale_dict)
psych2['for_resp_factor'] = psych2['for_resp_factor'].map(for_scale_dict)
psych3['for_cite_resp_factor'] = psych3['for_cite_resp_factor'].map(for_scale_dict)
psych3['for_read_resp_factor'] = psych3['for_read_resp_factor'].map(for_scale_dict)
psych4['for_cite_resp_factor'] = psych4['for_cite_resp_factor'].map(for_scale_dict)
psych4['for_read_resp_factor'] = psych4['for_read_resp_factor'].map(for_scale_dict)

## Re-read Response
### Create a dictionary mapping numbers to scale values
rethink_scale_dict = {
    0: "Continue",
    1: "Re-read the abstract"
}

### Map using the dictionary
history['rethink_resp'] = history['rethink_resp'].map(rethink_scale_dict)
psych1['rethink_resp'] = psych1['rethink_resp'].map(rethink_scale_dict)
psych2['rethink_resp'] = psych2['rethink_resp'].map(rethink_scale_dict)
psych3['rethink_resp'] = psych3['rethink_resp'].map(rethink_scale_dict)
psych4['rethink_resp'] = psych4['rethink_resp'].map(rethink_scale_dict)

# create empty list to store all prompts
all_prompts = []


################
# Instructions #
################

# Initial instructions
## Experiment 1 and 2
instruction_history_exp1_and_2 = 'Imagine this study is part of your typical daily work at your university.\n'\
    'The following abstracts have been written by one of your colleagues, and you now have the opportunity to decide whether the papers should be submitted for publication based on their abstracts.\n'\
    'Naturally, you do not have the capacity to bring all the papers to publication, only a small proportion.\n'\
    'Please make your decision as quickly as possible.\n'\
    'There is no right or wrong answer; we wish to capture your intuitive judgment.\n'\
    'We are interested in your first impression and will ask you to report your level of certainty about this initial decision.\n'\
    'Furthermore, we will ask for a second assessment of the abstract for methodological purposes, and kindly ask you to evaluate   the abstracts a second time.\n'\
    'You will be able to read the abstracts again if you do not remember them sufficiently.\n'

## Experiment 3 and 4
instruction_exp3_and_4 = 'Imagine this study is part of your typical daily work at your university.\n'\
    'You retrieved the following abstracts during a literature search, and now you have the opportunity to decide whether you would (a) read the papers based on the abstracts, and (b) cite the respective papers of the abstracts in your work.\n'\
    'Naturally, you do not have the capacity to cite or read all of the papers, only a small proportion.\n'\
    'Please make your decision as quickly as possible.\n'\
    'There is no right or wrong answer; we wish to capture your intuitive judgment.\n'\
    'We are interested in your first impression and will ask you to report your level of certainty about this initial decision.\n'\
    'Furthermore, we will ask for a second assessment of the abstract for methodological purposes, and kindly ask you to evaluate the abstracts a second time.\n'\
    'You will be able to read the abstracts again if you do not remember them sufficiently.\n'

# Response Instructions
## Experiment 1 and 2
### Decision 1: Probability to Publish the Article
trial_instruction_decision1_resp = "Intuitive answer: What is the likelihood that you would submit this article for publication if you had to intuitively decide based solely on this abstract?"

### FOR: Feeling of Rightness
trial_instruction_for_resp = "Certainty about the intuitive answer: When I submitted the answer, I felt:"

### Decision 1: Probability to Publish the Article after Rethinking
trial_instruction_decision2_resp = "Considered Answer: What is the likelihood that you would submit this article for publication if you now had to make a decision based solely on this abstract after rethinking?"

## Experiment 3 and 4
### Reading: Probability to Read the Article
trial_instruction_decision1_read = 'What is the likelihood that you would READ this article, if you had to intuitively decide based solely on this abstract?'

### Citing: Probability to Cite the Article
trial_instruction_decision1_cite = 'What is the likelihood that you would CITE this article, if you had to intuitively decide based solely on this abstract?'

### Reading FOR: Feeling of Rightness
trial_instruction_for_read = 'When I submitted the answer to READ, I felt:'

### Citing FOR: Feeling of Rightness
trial_instruction_for_cite = 'When I submitted the answer to CITE, I felt:'

### Reading: Probability to Read the Article after Rethinking
trial_instruction_decision2_read = 'What is the likelihood that you would READ this article if you now had to make a decision based solely on this abstract after rethinking?'

### Citing: Probability to Cite the Article after Rethinking
trial_instruction_decision2_cite = 'What is the likelihood that you would CITE this article if you now had to make a decision based solely on this abstract after rethinking?'

# Re-read Instructions
## Re-read instruction 1
## Only displayed once during the first trial
trial_instruction_rethink_1 = 'Thank you for providing your quick answer and then sharing your certainty about your answer.\n'\
    'Now we would like you to take a moment to reconsider your response.\n'\
    'Please take some time to rethink the decision.\n'\
    'Consider any factors you may have missed, reflect on different perspectives, or simply reassess your initial thoughts.\n'\
    'The exact duration is up to you.\n'\
    'When you feel ready and have thoroughly rethought your answer, please proceed to the next step by clicking "Continue".\n'\
    'If you do not remember the abstract you can read it again by clicking "Re-read the abstract".\n'\
    'Remember, your thoughtful consideration is crucial to this study, so please take the time you need.\n'

## Rethink instruction 2
## Displayed in every trial after the first trial
trial_instruction_rethink_2 = 'Please take some time to rethink your decision. When you feel ready, please proceed to the next step by clicking "Continue" or reading the abstract again by clicking on the button "Re-read the abstract".'


###########
# History #
###########
# Define number of participants and trials
participants_history = history["id"].unique()
trials_history = range(history["trial"].max() + 1)

# History: Generate individual prompts for participants
for participant in participants_history:
    history_participant = history[history["id"] == participant]
    participant = participant.item()
    individual_prompt = instruction_history_exp1_and_2
    rt_list = []
    for trial in trials_history:
        history_trial = history_participant.loc[history_participant["trial"] == trial]
        if not history_trial.empty:  # Only process if trial exists for this participant
            abstract = 'Abstract: "' + history_trial["abstract_text"].iloc[0] + '"'
            decision1 = history_trial["decision1_resp"].iloc[0]
            for_resp = history_trial["for_resp_factor"].iloc[0]
            decision2 = history_trial["decision2_resp"].iloc[0]
            rethink_resp = history_trial["rethink_resp"].iloc[0]
            
            # store reaction times
            decision1_rt = history_trial["decision1_rt"].iloc[0].item()
            for_resp_rt = history_trial["for_rt"].iloc[0].item()
            decision2_rt = history_trial["decision2_rt"].iloc[0].item()
            rethink_rt = history_trial["rethink_rt"].iloc[0].item()
            rt_list_trial = [decision1_rt, for_resp_rt, decision2_rt, rethink_rt]
            rt_list.append(rt_list_trial)

            # Choose rethink instruction based on trial number
            rethink_instruction = trial_instruction_rethink_1 if trial == 0 else trial_instruction_rethink_2
            
            if rethink_resp == "Continue":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            elif rethink_resp == "Re-read the abstract":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {abstract} {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            individual_prompt += datapoint
    # unlist rt_list
    rt_list = [item for sublist in rt_list for item in sublist]
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "schiekiera2025metascience/history",
            "participant": participant,
            "RTs": rt_list
        }
    )


###########
# Psych1 #
###########
# Define number of participants and trials
participants_psych1 = psych1["id"].unique()
trials_psych1 = range(psych1["trial"].max() + 1)

# Psych1: Generate individual prompts for participants
for participant in participants_psych1:
    psych1_participant = psych1[psych1["id"] == participant]
    participant = participant.item()
    individual_prompt = instruction_history_exp1_and_2
    rt_list = []
    for trial in trials_psych1:
        psych1_trial = psych1_participant.loc[psych1_participant["trial"] == trial]
        if not psych1_trial.empty:  # Only process if trial exists for this participant
            abstract = 'Abstract: "' + psych1_trial["abstract_text"].iloc[0] + '"'
            decision1 = psych1_trial["decision1_resp"].iloc[0]
            for_resp = psych1_trial["for_resp_factor"].iloc[0]
            decision2 = psych1_trial["decision2_resp"].iloc[0]
            rethink_resp = psych1_trial["rethink_resp"].iloc[0]

            # store reaction times
            decision1_rt = psych1_trial["decision1_rt"].iloc[0].item()
            for_resp_rt = psych1_trial["for_rt"].iloc[0].item()
            decision2_rt = psych1_trial["decision2_rt"].iloc[0].item()
            rethink_rt = psych1_trial["rethink_rt"].iloc[0].item()
            rt_list_trial = [decision1_rt, for_resp_rt, decision2_rt, rethink_rt]
            rt_list.append(rt_list_trial)

            # Choose rethink instruction based on trial number
            rethink_instruction = trial_instruction_rethink_1 if trial == 0 else trial_instruction_rethink_2
            
            if rethink_resp == "Continue":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            elif rethink_resp == "Re-read the abstract":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {abstract} {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            individual_prompt += datapoint
    # unlist rt_list
    rt_list = [item for sublist in rt_list for item in sublist]
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "schiekiera2025metascience/psych1",
            "participant": participant,
            "RTs": rt_list
        }
    )


###########
# Psych2 #
###########

# Define number of participants and trials
participants_psych2 = psych2["id"].unique()
trials_psych2 = range(psych2["trial"].max() + 1)

# Psych2: Generate individual prompts for participants
for participant in participants_psych2:
    psych2_participant = psych2[psych2["id"] == participant]
    participant = participant.item()
    individual_prompt = instruction_history_exp1_and_2
    rt_list = []
    for trial in trials_psych2:
        psych2_trial = psych2_participant.loc[psych2_participant["trial"] == trial]
        if not psych2_trial.empty:  # Only process if trial exists for this participant
            abstract = 'Abstract: "' + psych2_trial["abstract_text"].iloc[0] + '"'
            decision1 = psych2_trial["decision1_resp"].iloc[0]
            for_resp = psych2_trial["for_resp_factor"].iloc[0]
            decision2 = psych2_trial["decision2_resp"].iloc[0]
            rethink_resp = psych2_trial["rethink_resp"].iloc[0]

            # store reaction times
            decision1_rt = psych2_trial["decision1_rt"].iloc[0].item()
            for_resp_rt = psych2_trial["for_rt"].iloc[0].item()
            decision2_rt = psych2_trial["decision2_rt"].iloc[0].item()
            rethink_rt = psych2_trial["rethink_rt"].iloc[0].item()
            rt_list_trial = [decision1_rt, for_resp_rt, decision2_rt, rethink_rt]
            rt_list.append(rt_list_trial)

            # Choose rethink instruction based on trial number
            rethink_instruction = trial_instruction_rethink_1 if trial == 0 else trial_instruction_rethink_2
            
            if rethink_resp == "Continue":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            elif rethink_resp == "Re-read the abstract":
                datapoint = f"{abstract} {trial_instruction_decision1_resp} You enter <<{decision1}>>. {trial_instruction_for_resp} You enter <<{for_resp}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {abstract} {trial_instruction_decision2_resp} You enter <<{decision2}>>.\n"
            individual_prompt += datapoint
    # unlist rt_list
    rt_list = [item for sublist in rt_list for item in sublist]
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "schiekiera2025metascience/psych2",
            "participant": participant,
            "RTs": rt_list
        }
    )


###########
# Psych3 #
###########

# Define number of participants and trials
participants_psych3 = psych3["id"].unique()
trials_psych3 = range(psych3["trial"].max() + 1)

# Psych3: Generate individual prompts for participants
for participant in participants_psych3:
    psych3_participant = psych3[psych3["id"] == participant]
    participant = participant.item()
    individual_prompt = instruction_exp3_and_4
    rt_list = []
    for trial in trials_psych3:
        psych3_trial = psych3_participant.loc[psych3_participant["trial"] == trial]
        if not psych3_trial.empty:  # Only process if trial exists for this participant
            abstract = 'Abstract: "' + psych3_trial["abstract_text"].iloc[0] + '"'
            decision1_read = psych3_trial["decision1_read_resp"].iloc[0]
            for_resp_read = psych3_trial["for_read_resp_factor"].iloc[0]
            decision2_read = psych3_trial["decision2_read_resp"].iloc[0]
            decision1_cite = psych3_trial["decision1_cite_resp"].iloc[0]
            for_resp_cite = psych3_trial["for_cite_resp_factor"].iloc[0]
            decision2_cite = psych3_trial["decision2_cite_resp"].iloc[0]
            rethink_resp = psych3_trial["rethink_resp"].iloc[0]

            # store reaction times
            decision1_rt_read = psych3_trial["decision1_read_rt"].iloc[0].item()
            for_resp_rt_read = psych3_trial["for_read_rt"].iloc[0].item()
            decision2_rt_read = psych3_trial["decision2_read_rt"].iloc[0].item()
            decision1_rt_cite = psych3_trial["decision1_cite_rt"].iloc[0].item()
            for_resp_rt_cite = psych3_trial["for_cite_rt"].iloc[0].item()
            decision2_rt_cite = psych3_trial["decision2_cite_rt"].iloc[0].item()
            rethink_rt = psych3_trial["rethink_rt"].iloc[0].item()
            rt_list_trial = [decision1_rt_read, for_resp_rt_read, decision2_rt_read, decision1_rt_cite, for_resp_rt_cite, decision2_rt_cite, rethink_rt]
            rt_list.append(rt_list_trial)

            # Choose rethink instruction based on trial number
            rethink_instruction = trial_instruction_rethink_1 if trial == 0 else trial_instruction_rethink_2
            
            if rethink_resp == "Continue":
                datapoint = f"{abstract} {trial_instruction_decision1_read} You enter <<{decision1_read}>>. {trial_instruction_decision1_cite} You enter <<{decision1_cite}>>. {trial_instruction_for_read} You enter <<{for_resp_read}>>. {trial_instruction_for_cite} You enter <<{for_resp_cite}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {trial_instruction_decision2_read} You enter <<{decision2_read}>>. {trial_instruction_decision2_cite} You enter <<{decision2_cite}>>.\n"
            elif rethink_resp == "Re-read the abstract":
                datapoint = f"{abstract} {trial_instruction_decision1_read} You enter <<{decision1_read}>>. {trial_instruction_decision1_cite} You enter <<{decision1_cite}>>. {trial_instruction_for_read} You enter <<{for_resp_read}>>. {trial_instruction_for_cite} You enter <<{for_resp_cite}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {abstract} {trial_instruction_decision2_read} You enter <<{decision2_read}>>. {trial_instruction_decision2_cite} You enter <<{decision2_cite}>>.\n"
            individual_prompt += datapoint
    # unlist rt_list
    rt_list = [item for sublist in rt_list for item in sublist]
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "schiekiera2025metascience/psych3",
            "participant": participant,
            "RTs": rt_list
        }
    )


###########
# Psych4 #
###########

# Define number of participants and trials
participants_psych4 = psych4["id"].unique()
trials_psych4 = range(psych4["trial"].max() + 1)

# Psych4: Generate individual prompts for participants
for participant in participants_psych4:
    psych4_participant = psych4[psych4["id"] == participant]
    participant = participant.item()
    individual_prompt = instruction_exp3_and_4
    rt_list = []
    for trial in trials_psych4:
        psych4_trial = psych4_participant.loc[psych4_participant["trial"] == trial]
        if not psych4_trial.empty:  # Only process if trial exists for this participant
            abstract = 'Abstract: "' + psych4_trial["abstract_text"].iloc[0] + '"'
            decision1_read = psych4_trial["decision1_read_resp"].iloc[0]
            for_resp_read = psych4_trial["for_read_resp_factor"].iloc[0]
            decision2_read = psych4_trial["decision2_read_resp"].iloc[0]
            decision1_cite = psych4_trial["decision1_cite_resp"].iloc[0]
            for_resp_cite = psych4_trial["for_cite_resp_factor"].iloc[0]
            decision2_cite = psych4_trial["decision2_cite_resp"].iloc[0]
            rethink_resp = psych4_trial["rethink_resp"].iloc[0]

            # store reaction times
            decision1_rt_read = psych4_trial["decision1_read_rt"].iloc[0].item()
            for_resp_rt_read = psych4_trial["for_read_rt"].iloc[0].item()
            decision2_rt_read = psych4_trial["decision2_read_rt"].iloc[0].item()
            decision1_rt_cite = psych4_trial["decision1_cite_rt"].iloc[0].item()
            for_resp_rt_cite = psych4_trial["for_cite_rt"].iloc[0].item()
            decision2_rt_cite = psych4_trial["decision2_cite_rt"].iloc[0].item()
            rethink_rt = psych4_trial["rethink_rt"].iloc[0].item()
            rt_list_trial = [decision1_rt_read, for_resp_rt_read, decision2_rt_read, decision1_rt_cite, for_resp_rt_cite, decision2_rt_cite, rethink_rt]
            rt_list.append(rt_list_trial)

            # Choose rethink instruction based on trial number
            rethink_instruction = trial_instruction_rethink_1 if trial == 0 else trial_instruction_rethink_2
            
            if rethink_resp == "Continue":
                datapoint = f"{abstract} {trial_instruction_decision1_read} You enter <<{decision1_read}>>. {trial_instruction_decision1_cite} You enter <<{decision1_cite}>>. {trial_instruction_for_read} You enter <<{for_resp_read}>>. {trial_instruction_for_cite} You enter <<{for_resp_cite}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {trial_instruction_decision2_read} You enter <<{decision2_read}>>. {trial_instruction_decision2_cite} You enter <<{decision2_cite}>>.\n"
            elif rethink_resp == "Re-read the abstract":
                datapoint = f"{abstract} {trial_instruction_decision1_read} You enter <<{decision1_read}>>. {trial_instruction_decision1_cite} You enter <<{decision1_cite}>>. {trial_instruction_for_read} You enter <<{for_resp_read}>>. {trial_instruction_for_cite} You enter <<{for_resp_cite}>>. {rethink_instruction} You enter <<{rethink_resp}>>. {abstract} {trial_instruction_decision2_read} You enter <<{decision2_read}>>. {trial_instruction_decision2_cite} You enter <<{decision2_cite}>>.\n"
            individual_prompt += datapoint
    # unlist rt_list
    rt_list = [item for sublist in rt_list for item in sublist]
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "schiekiera2025metascience/psych4",
            "participant": participant,
            "RTs": rt_list
        }
    )

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
