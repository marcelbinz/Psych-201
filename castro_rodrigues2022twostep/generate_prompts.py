import sys
sys.path.append("..")

import numpy as np
import pandas as pd
import jsonlines

from utils import randomized_choice_options

# to read the data, we need the code provided by the authors, downloaded from
#   https://github.com/ThomasAkam/Two-step_explicit_knowledge
#   folder "code/Two_step"
#   the "Two_step" must be placed in the experiment folder "castro_rodrigues2022twostep"
from Two_step import  he

# log files downloaded from
#   https://github.com/ThomasAkam/Two-step_explicit_knowledge
#   folder "data"
#   the folder "data" must be placed in the source address "PSYCH-201" to be 
#   accessible functions in Two_step
datasets = ["healthy-volunteers_changing_no-debrief_LS",
            "healthy-volunteers_changing-task_debrief_LS",
            "healthy-volunteers_fixed-task_debrief_LS",
            "healthy-volunteers_fixed-task_debrief_NY",
            "healthy-volunteers_fixed-task_no-debrief_LS",
            "healthy-volunteers_slow-paced-task_debrief_LS",
            "mood-and-anxiety_fixed-task_debrief_LS",
            "mood-and-anxiety_fixed-task_debrief_NY",
            "OCD_fixed-task_debrief_LS",
            "OCD_fixed-task_debrief_NY"
            ]
conditions = ["healthy","healthy","healthy","healthy","healthy","healthy",
              "mood-and-anxiety","mood-and-anxiety","OCD","OCD"]
debriefing = [False,True,True,True,False,True,
              True,True,True,True]
changing = [True,True,False,False,False,True,
            False,False,False,False]
nTrials = [300,300,300,300,300,150,
           300,300,300,300]
session_inds = [1,2,3,4]
all_prompts = []

UpDown = ["up","down"]
LeftRight = ["left","right"]
Reward = ["a coin","no coin"]


debriefing_fixedA = "We will now explain the structure of the game.\n"\
    "In each trial, first the two central circles (upper and lower) are yellow, indicating that you can choose one of them.\n"\
    "If you press the upper arrow key, you will choose the upper circle. If you press the lower arrow key, you will choose the lower circle.\n"\
    "After you choose the upper or the lower circle, one of the two side circles will light up, i.e., will turn yellow (left or right).\n"\
    "After you press the arrow key that corresponds to the lateral circle that lit up (left or right), a coin may or may not appear.\n"\
    "The probability according to which the central circles give access to either one of the lateral circle also follows some rules.\n"\
    "If you choose the upper circle, one of two different things can happen. Most of the times (actually 80 percent of the times) the left side circle will light up.\n"\
    "Rarely, the right side circle will light up.\n"\
    "If you choose the lower circle, most of the times (actually 80 percent of the times) the right side circle will light up.\n"\
    "On the remaining occasions, the left side circle will light up.\n"\
    "The left and right circles give access to the rewards, which are symbolized as coins.\n"\
    "However, the probability of winning a coin is not equal on the left or on the right: it is always higher on one of the sides.\n"\
    "Sometimes it is higher on the left and sometimes it is higher on the right. The side in which that probability is higher changes after 20 or more trials.\n"\
    "You will now play a last session, with the same rules. Good luck!"


debriefing_fixedB = "We will now explain the structure of the game.\n"\
    "In each trial, first the two central circles (upper and lower) are yellow, indicating that you can choose one of them.\n"\
    "If you press the upper arrow key, you will choose the upper circle. If you press the lower arrow key, you will choose the lower circle.\n"\
    "After you choose the upper or the lower circle, one of the two side circles will light up, i.e., will turn yellow (left or right).\n"\
    "After you press the arrow key that corresponds to the lateral circle that lit up (left or right), a coin may or may not appear.\n"\
    "The probability according to which the central circles give access to either one of the lateral circle also follows some rules.\n"\
    "If you choose the upper circle, one of two different things can happen. Most of the times (actually 80 percent of the times) the right side circle will light up.\n"\
    "Rarely, the left side circle will light up.\n"\
    "If you choose the lower circle, most of the times (actually 80 percent of the times) the left side circle will light up.\n"\
    "On the remaining occasions, the right side circle will light up.\n"\
    "The left and right circles give access to the rewards, which are symbolized as coins.\n"\
    "However, the probability of winning a coin is not equal on the left or on the right: it is always higher on one of the sides.\n"\
    "Sometimes it is higher on the left and sometimes it is higher on the right. The side in which that probability is higher changes after 20 or more trials.\n"\
    "You will now play a last session, with the same rules. Good luck!"

debriefing_changing = "We will now explain the structure of the game.\n"\
    "In each trial, first the two central circles (upper and lower) are yellow, indicating that you can choose one of them.\n"\
    "If you press the upper arrow key, you will choose the upper circle. If you press the lower arrow key, you will choose the lower circle.\n"\
    "After you choose the upper or the lower circle, one of the two side circles will light up, i.e., will turn yellow (left or right).\n"\
    "After you press the arrow key that corresponds to the lateral circle that lit up (left or right), a coin may or may not appear.\n"\
    "The probability according to which the central circles give access to either one of the lateral circle also follows some rules.\n"\
    "The game is divided in two types of blocks.\n"\
    "In 'A' blocks, choosing the upper circle leads more frequently (80 percent of the times) to the lighting up of the right side circle.\n"\
    "On the other hand, in these blocks, choosing the lower circle, leads more frequently (80 percent of the times) to the lighting up of the left side circle.\n"\
    "In 'B' blocks, choosing the upper circle leads more frequently (80 percent of the times) to the lighting up of the left side circle.\n"\
    "On the other hand, in these blocks, choosing the lower circle, leads more frequently (80 percent of the times) to the lighting up of the right side circle.\n"\
    "Therefore, in 'A' blocks, if you choose the upper circle, one of two things can happen.\n"\
    "Most of the times (actually 80 percent of the times), the right side circle will light up.\n"\
    "Rarely (20 percent of the time), the left side circle will light up.\n"\
    "In these same 'A' blocks, if you choose the lower circle, one of two things can happen.\n"\
    "Most of the times (actually 80 percent of the times), the left side circle will light up.\n"\
    "Rarely (20 percent of the time), the right side circle will light up.\n"\
    "In 'B' blocks, if you choose the upper circle, one of two things can happen.\n"\
    "Most of the times (actually 80 percent of the times), the left side circle will light up.\n"\
    "Rarely (20 percent of the time), the right side circle will light up.\n"\
    "In these same 'B' blocks, if you choose the lower circle, one of two things can happen.\n"\
    "Most of the times (actually 80 percent of the times), the right side circle will light up.\n"\
    "Rarely (20 percent of the time), the left side circle will light up.\n"\
    "'A' blocks and 'B' blocks alternate between them after 20 or more trials.\n"\
    "The left and right circles give access to the rewards, which are symbolized as coins.\n"\
    "However, the probability of winning a coin is not the equal on the left or on the right: it is always higher on one of the sides.\n"\
    "Sometimes it is higher on the left and sometimes it is higher on the right.\n"\
    "The side in which that probability is higher changes after 20 or more trials.\n"\
    "You will now play a last session, with the same rules. Good luck!\n"

for i_dataset, dataset in enumerate(datasets):
    # loading experimental data
    print(dataset)
    exp = he.experiment(dataset)
    participants = exp.subject_IDs

    for participant in participants:
        RTs = []

        # general instruction
        prompt = "In this task, you will play a game in order to gain of as many rewards as possible.\n"\
            "Rewards will be represented in the screen as coins.\n"\
            "Every time you get a coin, it will show up in the screen and it will be added to your total number of rewards.\n"\
            "The number of coins you get will determine the value of the reward that you will receive at the end of your participation.\n"\
            "You will perform " + str(nTrials[i_dataset] * 4) + " trials distributed in 4 sessions.\n"\
            "In each trial, you see four circles on the screen: two central circles (upper and lower) flanked by two side circles (left and right).\n"\
            "The circles can be yellow or black.\n"\
            "You can interact with the screen by pressing the arrow keys (up, down, left or right).\n"\
            "In each trial, you can get either one coin or no coin.\n"\
            "At the end of those " + str(nTrials[i_dataset] * 4) + " trials, " + str(int(nTrials[i_dataset] * 4/3)) + " will be randomly chosen to count the final number of coins.\n"\
            "Once the session is completed, a sentence thanking you for your participation will show up in the screen.\n"

        for i_session in session_inds:
            session = exp.get_sessions(participant,i_session)[0]
            # actions
            at = session.trial_data['choices']          # 1 = up; 0 = down
            # second step states
            st = session.trial_data['second_steps']     # 1 = left; 0 = right
            # outcome
            ot = session.trial_data['outcomes']         # 1 = rewarded

            # raction times
            rt1 = session.times['choice']    - session.times['trial_start']
            rt2 = session.times['ss_action'] - session.times['second_step']


            prompt += "Welcome to Session " + str(i_session) + ".\n"
            # debriefing for session 4
            if debriefing[i_dataset] & (i_session == 4):
                # checking whether the participant is in the fixed group
                if changing[i_dataset]:
                    prompt += debriefing_changing
                else:
                    # checking whether the participant is assigned to block A or B
                    if (session.blocks['transition_states'][0] == 1):
                        prompt += debriefing_fixedA
                    else:
                        prompt += debriefing_fixedB
            # going over trials
            for index_trial in range(len(at)):
                trial = index_trial + 1
                prompt += 'Trial ' + str(trial) + '\n'
                prompt += "There are four circles on the screen: two central circles (upper and lower) flanked by two side circles (left and right).\n"
                prompt += "The central circles are yellow, and the side circles are black.\n"
                prompt += 'You press the arrow key for <<' + UpDown[at[index_trial]] + '>>.\n'
                RTs.append(rt1[index_trial])
                prompt += "The central circles turn black.\n"
                prompt += "The " + LeftRight[st[index_trial]] + " circle lights up and becomes yellow.\n"
                prompt += 'You press the arrow key for <<' + LeftRight[st[index_trial]] + '>>.\n'
                RTs.append(rt2[index_trial])
                prompt += 'You received ' + Reward[ot[index_trial]] + ' in this trial.\n'
                
            prompt += "Thank for your participation. You just completed Session " + str(i_session) + ".\n"
        prompt += '\n'

        prompt = prompt[:-2]
        # print(prompt)

        all_prompts.append({'text': prompt,
            'experiment': 'castro_rodrigues2022twostep/data/' + dataset,
            'participant': str(participant),
            'RTs': RTs,
            'condition': conditions[i_dataset],
            'debriefing': debriefing[i_dataset],
            'changing': changing[i_dataset]
        })


with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
