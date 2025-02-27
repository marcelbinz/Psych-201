import pandas as pd
import json
import zipfile
import os

# paths to datasets
file_paths = {
    "Study 1": "Datasets/Study 1 Data.csv",
    "Study 2": "Datasets/Study 2 Data.csv",
    "Study 3": "Datasets/Study 3 Data.csv"
}

# life events (stimuli) transcribed from https://osf.io/4387b
life_events = {
    1: "Be exactly the same weight in 10 years time",
    2: "Last the whole of next winter without catching a minor cold",
    3: "Participate in a game of sport in the next four weeks",
    4: "Clean the bathroom in the next four weeks",
    5: "50 or more hours of sleep in a single week in the next four weeks",
    6: "Fix a broken possession in the next four weeks",
    7: "Get a haircut in the next four weeks",
    8: "Have your photo taken in the next four weeks",
    9: "Play a board game in the next four weeks",
    10: "Shop for clothes in the next four weeks",
    11: "Try a new hobby, craft, or sport in the next four weeks",
    12: "Receive a utility bill in the next four weeks",
    13: "Win a competitive game of sport in the next four weeks",
    14: "Burn something that you are cooking in the next four weeks",
    15: "Embarrass yourself in the next four weeks",
    16: "Get lost in the next four weeks",
    17: "Have a disagreement with a friend in the next four weeks",
    18: "Have a headache in the next four weeks",
    19: "Be ill one day because of over-drinking in the next four weeks",
    20: "Stay up past 2 AM for school or work in the next four weeks",
    21: "Get teased at/made fun of in the next four weeks",
    22: "Get lied to in the next four weeks",
    23: "Get stuck in traffic in the next four weeks",
    24: "The next car that passes is a BMW",
    25: "Have a vegan meal in the next four weeks",
    26: "Make a purchase by contactless card in the next four weeks",
    27: "Check your phone more than 100 times in one day in the next four weeks",
    28: "The next car that passes is the colour black",
    29: "Receive a phone call from an unknown number in the next four weeks",
    30: "Buy a non-dairy milk alternative in the next four weeks",
    31: "Spend more than £121 on dinners out over the next four weeks",
    32: "Spend less than £89 on commuting over the next four weeks",
    33: "Send fewer than 106 text messages over the next four weeks",
    34: "Feel a phantom phone vibration in the next four weeks",
    35: "Walk less than seven miles over the next four weeks",
    36: "That your next flight will have a minor delay (i.e., 15 minutes or less)",
    37: "That the next store you visit is air conditioned",
    38: "Receive junk mail in the next four weeks",
    39: "Drink between 56 and 84 cups of coffee over the next four weeks",
    40: "Make your bed every day for the next four weeks",
    41: "Use more than 3.7GB of mobile data over the next four weeks",
    42: "Check your mobile data usage in your phone's settings in the next four weeks",
    43: "Spend more than 40 hours online in the next week",
    44: "The next car you ride in, other than your own, is the colour white",
    45: "Take the Eurostar train service in the future",
    46: "Own a pet",
    47: "Live in a home that was originally built before 1900",
    48: "Move homes more than 10 times in your lifetime",
    49: "Enrol in private health insurance",
    50: "Meet your future spouse through an online dating service",
    51: "Marry someone with a different political affiliation to you"
}

# valence mapping
valence_mapping = {
    1: "extremely negative",
    2: "somewhat negative",
    3: "neither positive nor negative",
    4: "somewhat positive",
    5: "extremely positive"
}

# study-specific prompts
study_prompts = {
    "Study 1": "You will be asked to estimate the likelihood of you personally experiencing a life event on a 0-100% scale, where 0% means you are absolutely certain that you will not experience the event and 100% means you are absolutely certain that you will experience the event. " 
                 "You will also be asked to estimate the likelihood of an average person experiencing the same life event. "
                 "You will then be shown the actual likelihood for an average person to experience the life event, according to official sources, and then you will be asked to revise your estimate of the likelihood that you will personally experience the life event. "
                 "Once you have provided initial and revised estimates for each life event, you will then be asked to rate each of those events based on how positive or negative you feel about them on a 5-point scale where 1 is \"extremely negative\", 2 is \"somewhat negative\", 3 is \"neither positive nor negative\", 4 is \"somewhat positive\" and 5 is \"extremely positive\". ",
    
    "Study 2": "You will be asked to estimate the likelihood of you personally experiencing a life event on a 0-100% scale, where 0% means you are absolutely certain that you will not experience the event and 100% means you are absolutely certain that you will experience the event. " 
                 "You will also be asked to estimate the likelihood of an average person experiencing the same life event. "
                 "You will then be shown the actual likelihood for an average person to experience the life event, according to official sources. "
                 "Once you have provided initial estimates for each life event, and you will then be shown each life again and asked to provide a revised estimate of the likelihood that you will personally experience the life event. "
                 "Once you have provided initial and revised estimates for each life event, you will then be asked to rate each of those events based on how positive or negative you feel about them on a 5-point scale where 1 is \"extremely negative\", 2 is \"somewhat negative\", 3 is \"neither positive nor negative\", 4 is \"somewhat positive\" and 5 is \"extremely positive\". ",
    
    "Study 3": "You will be asked to estimate the likelihood of you personally experiencing a life event on a 0-100% scale, where 0% means you are absolutely certain that you will not experience the event and 100% means you are absolutely certain that you will experience the event. " 
                 "You will also be asked to estimate the likelihood of an average person experiencing the same life event. "
                 "You will then be shown the actual likelihood for an average person to experience the life event, according to official sources, and then you will then be asked to rate the event based on how positive or negative you feel about it on a 5-point scale where 1 is \"extremely negative\", 2 is \"somewhat negative\", 3 is \"neither positive nor negative\", 4 is \"somewhat positive\" and 5 is \"extremely positive\". "
                 "Once you have provided initial estimates and rated how positive or negative you feel about each life event, and you will then be shown each life event again and asked to provide a revised estimate of the likelihood that you will personally experience the life event. "
}

# experiment ids
experiment_ids = {
    "Study 1": "burton2022optimism/1",
    "Study 2": "burton2022optimism/2",
    "Study 3": "burton2022optimism/3"
}

# create output file
output_file = "prompts.jsonl"

# open output file for writing
with open(output_file, "w") as outfile:
    for study, path in file_paths.items():
        # read in a study's dataset as df
        df = pd.read_csv(path)
        
        # group data by participant
        for participant, group in df.groupby("Participant"):
            experiment_texts = [study_prompts[study]]
            event_texts = []
            event_texts2 = []
            valence_texts = []
            
            for _, row in group.iterrows():
                valence_text = valence_mapping.get(row['Valence'], "unknown")
                event_description = life_events.get(row['Event'], "Unknown event")
                
                if study == "Study 1":
                    event_texts.append(
                        f"You view the following event: '{event_description}'. "
                        f"How likely do you think it is that you will personally experience this event? You enter <<{row['E1']}%>> "
                        f"How likely do you think it is that an average person experiences this event? You enter <<{row['eBR']}%>> "
                        f"You learn that there is actually a {row['BR']}% chance that an average person experiences this event, according to official sources. "
                        f"Now, how likely do you think it is that you will personally experience this event? You enter <<{row['E2']}%>> "
                    )
                    valence_texts.append(
                        f"You view event following event again: '{event_description}'. "
                        f"How would you feel about experiencing this event? You indicate it would be <<{valence_text}>> "
                    )
                elif study == "Study 2":
                    event_texts.append(
                        f"You view the following event: '{event_description}'. "
                        f"How likely do you think it is that you will personally experience this event? You enter <<{row['E1']}%>> "
                        f"How likely do you think it is that an average person experiences this event? You enter <<{row['eBR']}%>> "
                        f"You learn that there is actually a {row['BR']}% chance that an average person experiences this event, according to official sources. "
                    )
                    event_texts2.append(
                        f"You view event following event again: '{event_description}'. "
                        f"Now, how likely do you think it is that you will personally experience this event? You enter <<{row['E2']}%>> "
                    )
                    valence_texts.append(
                        f"You view event following event again: '{event_description}'. "
                        f"How would you feel about experiencing this event? You indicate it would be <<{valence_text}>> "
                    )
                elif study == "Study 3":
                    event_texts.append(
                        f"You view the following event: '{event_description}'. "
                        f"How likely do you think it is that you will personally experience this event? You enter <<{row['E1']}%>> "
                        f"How likely do you think it is that an average person experiences this event? You enter <<{row['eBR']}%>> "
                        f"You learn that there is actually a {row['BR']}% chance that an average person experiences this event, according to official sources. "
                        f"How would you feel about experiencing this event? You indicate it would be <<{valence_text}>> "
                    )
                    event_texts2.append(
                        f"You view event following event again: '{event_description}'. "
                        f"Now, how likely do you think it is that you will personally experience this event? You enter <<{row['E2']}%>> "
                    )
            
            experiment_texts.extend(event_texts)
            experiment_texts.extend(event_texts2)
            experiment_texts.extend(valence_texts)
            entry = {"text": " ".join(experiment_texts), "experiment": experiment_ids[study], "participant": participant}
            outfile.write(json.dumps(entry) + "\n")

# create a zip 
zip_filename = "prompts_jsonl.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(output_file)

# delete the jsonl file
os.remove(output_file)