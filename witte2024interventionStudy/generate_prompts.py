import numpy as np
import pandas as pd
import jsonlines
#from utils import randomized_choice_options

data_path = "/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/intervention_study.csv"
data = pd.read_csv(data_path)

intervention_data = pd.read_csv("/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/intervention.csv")
wantInfo_data = pd.read_csv("/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/worry.csv")
nervous_data = pd.read_csv("/Users/kristinwitte/Library/CloudStorage/OneDrive-Personal/CPI/hackathons/psych201/nervous.csv")

print(len(data["x"].dropna()))
IDs = set(data["ID"])
Nblocks = len(data["block"].unique())

control_preamble = "In this study you will be playing a novel game that we designed quite recently. \n" \
  "Since it is so new, we don't know whether people will like and what kind of strategies they will use when playing the game.\n"\
  "We would therefore like for you to be one of our test subjects. You will receive a tutorial for the game, then play 6 rounds to get familiar with it.\n "\
  "After that we will ask you some questions about how you liked the game. After that, you will play another 5 rounds of the game so that you can see, whether having more experience changes how you feel about the game.\n"\
  "You will then have the possibility to change your answers, if playing for more rounds changed your mind on some of them. \n" \
  "To make your experience of the game exactly the way our future participants will experience it, you will also be able to get a bonus payment depending on how well you do in the game, so try to do your best.\n"\
  "Some people have told us that the game made them feel nervous. We will therefore ask you from time to time how nervous you felt during the previous round. Please answer this honestly and not based on what you think we would like to hear!\n"\
"Let's get started with the game tutorial!"


intervention_preamble = "In this study, we would like to get some help from you in designing an intervention, that will make people less anxious. \n" \
 "More precisely: We designed a game that often makes people feel anxious and makes them worry. We would now like to help people be less anxious, worry less and thereby do better in the game. \n"\
 "For you to be able to help us in designing this intervention, you first need to know what the game is about. You will therefore first get a tutorial on the game and play a couple of rounds of the game before we tell you more about the strategy we would like to convey.\n" \
"After helping us design the instructions for the strategy, you will get to play the game again to see whether the strategy fits the game. If you realise at this point, that you are not happy with the way you designed the strategy, you will have the opportunity to change it after you finished playing the game for the second time.\n" \
"To make your experience of the game exactly the way our future participants will experience it, you will also be able to get a bonus payment depending on how well you do in the game, so try to do your best.\n"\
"We will also ask you from time to time, how nervous you felt during the previous round, to gather more data on what aspects of the game make people nervous. Please answers this honestly and not based on what you think we would like to hear!\n"\
"Let's get started with the game tutorial!"

intervention_texts = ["As we mentioned in the beginning, people have told us that they tend to worry about not having found the optimal square or that they feel anxious about finding the Kraken. We would like to give people a strategy that might help them not feel this way.\n A central aspect of this strategy is that worrying is unnecessary, no matter the content of the worries. This is because all thoughts, no matter their validity, are just thoughts, not facts.\n We would like your help in making people understand and use this strategy. We will now try to explain this strategy to you. We hope it makes sense. What we need your help with is to come up with a better explanation that would help others really understand it better than from our own explanations. Please think carefully about your answers. After you submit the study, we will review your responses and if they are nonsensical, we will not be able to pay you your bonus payment.\n",
    "How could you explain to someone that it is possible to be well prepared without worrying?",
    "Studies have shown that worrying is a controllable process. Please give us an example of when you managed to control worries that shows to others that worrying is a controllable process.",
    "If worrying were an effective problem-solving strategy, people who worry more would have fewer problems. Science has shown that the opposite is actually the case and people that worry more report having more problems. What would you say to somebody to convince them of this?",
    "Imagine a person who worried a lot during the game you just played. Would the person still have been able to solve the game, if they had not worried? How?",
    "One idea for people to detach from their worries is to get them to see their thoughts as just passing mental events rather than facts. What could we say to people who worry in the game to help them see their worries as just passing thoughts? Just telling people to do this doesn't work so well, so we need some more intuitive explanation of why this would be helpful. ",
    "Thank you for your answers! You will now play the game again for 5 more rounds. During the game, please think about your answers and whether you would like to change anything about them.\n" 
  ]

control_texts = ["As we announced in the beginning, we would like some feedback on how you are finding the game so far. Please think carefully about your answers. After you submit the study, we will review your responses and if they are nonsensical, we will not be able to pay you your bonus payment.\n",
    "How would you explain the game to someone who has never played it before?",
    "What was your strategy to gain more points?",
    "What was your strategy to avoid the kraken?",
   "What did you like about the game?",
    "What did you dislike about the game?",
    "Thank you for your answers! You will now play the game again for 5 more rounds.\n"
]


#TODO
instr = "Welcome to the game! In this game you play the role of a sailor trying to catch fish from the ocean.\n" \
    "You can choose to go fishing in any of the squares of an 11-by-11 grid representing the ocean. The squares are indexed by their row (0-10) and their column (0-10). To select a square you provide its location like [x_index, y_index]. Once you select a square, you will be told the number of fish you caught in that square.\n" \
    "One square will be selected for you at the start of each round, and you'll be told the number of fish in that square." \
    "You will have to work out which locations are likely to contain the most fish in order to maximise your score. If one square has a high number of fish, it's likely that nearby squares will also have a lot of fish. If a square has few fish, nearby squares are likely to also have few fish.\n" \
    "You can select the same square several times. Each time you will get a similar number of fish.\n" \
    "However, there is a dangerous creature called the Kraken lurking in the ocean somewhere, which feeds on fish. You must avoid finding the Kraken. If you do, it will steal all the fish you have collected in that round! When the kraken is nearby, you will be told so in the begginning of the round. Sometimes the kraken will be somewhere else, and you won't be at risk of finding it. \n" \
    "Areas where the Kraken lurks will have very few fish as it has started to eat them. When the kraken is nearby, if you find a square with 50 fish or fewer, there is a 100 percent chance that the Kraken will be there. If you find a square with more than 50 fish, you'll always be safe. \n" \
    "The number of fish in the ocean does not decrease as the task goes on, or when you click on a square more than once."

def do_intervention(ID):
    inter_dat = intervention_data.loc[intervention_data["ID"] == ID]
    #reset index
    inter_dat = inter_dat.reset_index(drop=True)
    # questions about worrying and reclicking
    out_text = "In the game you just played, you will never have all the information about all the squares in the ocean. What do you think is a better strategy: clicking as many squares as possible to find out as much information as possible or re-clicking the squares with the most fish? Answer using a number between 0 and 100 with 0 meaning clicking as many squares as possible and 100 meaning re-clicking.\n"
    #print()
    out_text += "You answered: <<" + str(inter_dat["reclicking"].item()) + ">>\n"
    out_text += "Still in the context of the fishing game you just played, do you think that worrying about whether you found the best square helps you be better at the game? Answer using a number between 0 and 100 with 0 meaning worrying helps you be better at the game and 100 meaning worrying does not help you be better at the game.\n"
    out_text += "You answered: <<" + str(inter_dat["worryHelpful"].item()) + ">>\n"
    # actual intervention
    out_text += intervention_texts[0]
    out_text += "1. " + intervention_texts[1] + "\n You answered: "
    out_text += inter_dat["text1"][0]
    out_text += "\n\n2. " + intervention_texts[2] + "\n You answered: "
    out_text += inter_dat["text2"][0]
    out_text += "\n\n3. " + intervention_texts[3] + "\n You answered: "
    out_text += inter_dat["text3"][0]
    out_text += "\n\n4. " + intervention_texts[4] + "\n You answered: "
    out_text += inter_dat["text4"][0]
    out_text += "\n\n5. " + intervention_texts[5] + "\n You answered: "
    out_text += inter_dat["text5"][0]
    out_text += "\n" + intervention_texts[6] # end of intervention text

    return out_text


#print(do_intervention(8))

def do_control_intervention(ID):
    inter_dat = intervention_data.loc[intervention_data["ID"] == ID]
    inter_dat = inter_dat.reset_index(drop=True)
    # actual intervention
    out_text = control_texts[0]
    out_text += "1. " + control_texts[1] + "\n You answered: "
    out_text += inter_dat["text1"][0]
    out_text += "\n\n2. " + control_texts[2] + "\n You answered: "
    out_text += inter_dat["text2"][0]
    out_text += "\n\n3. " + control_texts[3] + "\n You answered: "
    out_text += inter_dat["text3"][0]
    out_text += "\n\n4. " + control_texts[4] + "\n You answered: "
    out_text += inter_dat["text4"][0]
    out_text += "\n\n5. " + control_texts[5] + "\n You answered: "
    out_text += inter_dat["text5"][0]
    out_text += "\n" + control_texts[6] # end of intervention text

    return out_text

#print(do_control_intervention(1))

def get_prompt(ID, cond):
    prompt = instr

    dat = data.loc[(data["ID"] == ID)]

    for block in range(1, Nblocks+1):

        # go to intervention first if it is time
        if block==6 :
            if cond == "intervention":
                prompt += do_intervention(ID)
            else:
                prompt += do_control_intervention(ID)
            


        block_dat = dat.loc[dat["block"] == block]
        if len(block_dat["x"].dropna()) == 0: # in case there is no data
            continue

        prompt += "Round " + str(block) + " of " + str(Nblocks) + ".\n"
        # ask if they want info
        prompt += "Would you like to hear from three people, whether they found the next ocean difficult for the price of 5 points?\n"
        infodat = wantInfo_data.loc[(wantInfo_data["ID"] == ID) & (wantInfo_data["block"] == block)]
        if infodat["wantInfo"].item() == "yes":
            prompt += "Your answer: <<Yes, please>>\n"
            prompt += "Here is the information you requested:\n"
            prompt += infodat["people1"].item() + "thought the ocean was "+ infodat["info1"].item() + ".\n"
            if ID != 92: # for some reason I only have one name and one rating for this participant and I can't be bothered to dig through the absolute raw data to find the other two
                prompt += infodat["people2"].item() + "thought the ocean was "+ infodat["info2"].item() + ".\n"
                prompt += infodat["people3"].item() + "thought the ocean was "+ infodat["info3"].item() + ".\n"

        else:
            prompt += "Your answer: <<No, thank you>>\n"
        


            # number of trials might be less than 25 if kraken is found
        ntrials = len(block_dat["x"].dropna())
        
        chosen_x = np.int64(block_dat.loc[block_dat["trial"] == 1, "x"].item())
        chosen_y = np.int64(block_dat.loc[block_dat["trial"] == 1, "y"].item())

        prompt += "The square [" + str(chosen_x) + ", " + str(chosen_y) + "] has already been revealed for you. It contains " + str(np.int64(block_dat.loc[block_dat["trial"] == 1, "z"].item())) + " fish.\n"

        for trial in range(2,(ntrials+1)):
            chosen_x = np.int64(block_dat.loc[block_dat["trial"] == trial, "x"].item())
            chosen_y = np.int64(block_dat.loc[block_dat["trial"] == trial, "y"].item())
            prompt += "On trial " + str(trial-1) + " of 25 you picked the square <<[" + str(chosen_x) + ", " + str(chosen_y) + "]>> and received " + str(np.int64(block_dat.loc[block_dat["trial"] == trial, "z"].item())) + " fish.\n"

        if block_dat["krakenFound"].unique() == 1:
            prompt += "You found the kraken! It stole all fish you found on this round. The round is over.\n"
        
        else:
            prompt += "End of the round.\n"

        # ask about nervousness if block is in [2,4,6,7,9,11]
        if block in [2,4,6,7,9,11]:
           prompt += "What was the most nervous you felt during this round? Please answer using a number between 0 and 100 with 0 meaning not nervous at all and 100 meaning extremely nervous.\n"
           prompt += "Your answer: <<" + str(nervous_data.loc[(nervous_data["ID"] == ID) & (nervous_data["block"] == block), "nervous"].item()) + ">>\n"



    return prompt

print(get_prompt(1, "control"))

all_prompts = []


for ID in IDs:
#for ID in [2]:
    #choice_options = randomized_choice_options(num_choices=4)
    condition = data.loc[data["ID"] == ID, "cond"].unique().item()
    if condition == "control":
        txt = control_preamble
    else:
        txt = intervention_preamble


    txt += get_prompt(ID, condition)

    #print(prompt)
    all_prompts.append({'text': txt,
                        'experiment': 'witte2024interventionStudy',
                        'participant': ID,
                        'STICSAcog': data.loc[data["ID"] == ID, "STICSAcog"].unique().item(),
                        'STICSAsoma': data.loc[data["ID"] == ID, "STICSAsoma"].unique().item(),
                        "MCQ": data.loc[data["ID"] == ID, "MCQ"].unique().item(),
                        "MCQpos": data.loc[data["ID"] == ID, "MCQpos"].unique().item(),
                        "MCQneg": data.loc[data["ID"] == ID, "MCQneg"].unique().item(),
                        "MCQconf": data.loc[data["ID"] == ID, "MCQconf"].unique().item(),
                        "MCQcontrol": data.loc[data["ID"] == ID, "MCQcontrol"].unique().item(),
                        "MCQselfcons": data.loc[data["ID"] == ID, "MCQselfcons"].unique().item(),
                        "MWQfreq": data.loc[data["ID"] == ID, "MWQfreq"].unique().item(),
                        "MWQbelief": data.loc[data["ID"] == ID, "MWQbelief"].unique().item(),
                        "CASpre": data.loc[data["ID"] == ID, "CASpre"].unique().item(),
                        "CASpost": data.loc[data["ID"] == ID, "CASpost"].unique().item(),
                        "CASchange": data.loc[data["ID"] == ID, "CASchange"].unique().item(),
                        "PHQ": data.loc[data["ID"] == ID, "PHQ"].unique().item()})

with jsonlines.open('witte2024interventionStudy/prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
