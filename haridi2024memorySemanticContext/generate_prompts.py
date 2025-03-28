import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

# set working directory to current directory
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# check what the current working directory is
print(os.getcwd())


datasets = ["ExperimentDataExp3.csv"] 
all_prompts = []

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)
    # transform RT into ms
    df['rt'] = df['rt'] * 1000

    num_tasks = df.Block.max() + 1


    for participant in df['subject_id'].unique():
        RTs = []
        condition =[]

        df_participant = df[(df['subject_id'] == participant)]

        # do the learning phase
        prompt = "The experiment consists of four blocks that each have three parts.\n"\
            "In the first part you learn a list of word pairs.\n"\
            "Your task in this first part is to try to remember the word pairs and immediatly test your memory by typing each word given the other word of the word pair you just learned.\n"\
            "In the second part you will be performing a short letter memory task.\n"\
            "And finally, in the third part you have to recall the words you learned in the first part of each block.\n"\
            "The words have to be recalled using one of the words in each word pair as a cue.\n"\
            "So if you learned the word pair ruin - shape and we present you with the word ruin your task is to recall the word shape\n"\
            "The background pictures (if present) are semantically meaningful and wll be shown both during learning and recall.\n"\
            "Each block is entirely seperate and you will be allowed to take a short break of max 1 minute between the blocks.\n\n"\

        for task in range(1, int(num_tasks)):
            df_task = df_participant[(df_participant['Block'] == task)]
            # check if the context size is NaN and if so, append "NoneContext"
            if pd.isnull(df_task.ContextSize.iloc[0]):
                condition.append("NoneContext")
            else:
                condition.append(df_task.ContextSize.iloc[0])

            prompt += 'Block ' + str(task) + ':\n'

            # learning phase
            prompt += "In the next part, we will start the learning of the word pairs.\n\n"
            "Please try your best to remember the word pairs so you can remember them later.\n"
            "You get to immediatly test your memory by typing each word given the other word of the word pair you just learned.\n"
            "Providing only the first three letters of the target word is allowed.\n\n"

            # only get the trials for the Phase LearningResponse
            df_learning = df_task[df_task['Phase'] == 'LearningResponse']
            num_trials_learning = df_learning.shape[0]

            for trial in range(0, num_trials_learning):
                df_trial = df_learning.iloc[trial]
                word1 = df_trial.word1
                word2 = df_trial.word2
                cue = df_trial.cue
                response = df_trial.response
                correct = df_trial.correct
                Context = df_trial.Context
                Context = Context.split('/')[-1].split('.')[0]

                if not isinstance(response, str):
                    response = ''
                if correct == "TRUE":
                    correct_text = 'correct'
                else:
                    correct_text = 'incorrect'
                if Context == "NoneContext":
                    prompt += 'You see the word pair ' + word1 + ' - ' + word2 + '.\n'
                else:
                    prompt += 'You see the word pair ' + word1 + ' - ' + word2 + ' on top of the image of some ' + Context +'.\n'
                prompt += 'You see the word ' + cue + '. You respond with <<'+ response +'>>.\n'
                prompt += 'That was ' + correct_text + '.\n'
                RTs.append(df_trial.rt.item())
            prompt += '\n'

            #Distractor task
            prompt += "In the next part, you will be performing a short letter memory task.\n\n"
            "You will see a sequence of letters and your task is to remember the letters in the order they were presented.\n"
            
            df_letter_response = df_task[df_task['Phase'] == 'LetterRecallResponse']
            num_trials_letter = df_letter_response.shape[0]

            for trial in range(0, num_trials_letter):
                df_trial = df_letter_response.iloc[trial]
                letters = df_trial.sequence
                correct = df_trial.correct
                response = df_trial.response
                if not isinstance(response, str):
                    response = ''
                if correct == "TRUE":
                    correct_text = 'correct'
                else:
                    correct_text = 'incorrect'
                # present each letter one by one
                for letter in letters:
                    prompt += 'You see the letter ' + letter + '.\n'
                prompt += 'Please type the letters you saw in the order they were presented.\n'
                prompt += 'You responded with <<'+ response +'>>.\n'
                prompt += 'That was ' + correct_text + '.\n'
                RTs.append(df_trial.rt)


            #Recall phase
            prompt += "In the next part, you have to remeber the words from the first part of the block.\n\n"
            "Please try your best to remember the word pairs and be as fast and accurate as possible.\n\n"
            "Providing only the first three letters of the target word is allowed.\n\n"
            "If you cant remember the target word, please respond with 0.\n\n"

            df_recall = df_task[df_task['Phase'] == 'RecallResponse']
            df_recall_cue = df_task[df_task['Phase'] == 'CuePresentation']
            num_trials_recall = df_recall.shape[0]

            for trial in range(0, num_trials_recall):
                df_trial = df_recall.iloc[trial]
                cue = df_trial.cue
                response = df_trial.response
                if not isinstance(response, str):
                    response = ''
                correct = df_trial.correct
                if correct == "TRUE":
                    correct_text = 'correct'
                else:
                    correct_text = 'incorrect'
                if Context == "NoneContext":
                    prompt += 'You see the word pair ' + word1 + ' - ' + word2 + '.\n'
                else:
                    prompt += 'You see the word ' + cue + ' on top of the image of some ' + Context +'.\n'
                prompt += 'You respond with <<'+ response +'>>.\n'
                RTs.append(df_recall_cue.iloc[trial].rt)


        prompt = prompt[:-2]
        print(prompt)
        #print(RTs)

        all_prompts.append({'text': prompt,
            'experiment': 'haridi2024memory_1/' + dataset,
            'participant': str(participant),
            'RTs': RTs,
            "age": str(df_participant.Age.iloc[0]),
            'condition': condition
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)