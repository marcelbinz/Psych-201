import pandas as pd
from string import Template
import sys
sys.path.append('..')
from utils import randomized_choice_options
import jsonlines

rt_map = {                                                  # map from target to reward and penalty and coverage probability (fixed for all participants)   
  "R1T1": {"reward": 2, "penalty": -1, "mprob": 0.22},
  "R1T2": {"reward": 8, "penalty": -5, "mprob": 0.51},
  "R1T3": {"reward": 9, "penalty": -9, "mprob": 0.42},
  "R1T4": {"reward": 9, "penalty": -10, "mprob": 0.40},
  "R1T5": {"reward": 2, "penalty": -6, "mprob": 0.08},
  "R1T6": {"reward": 5, "penalty": -5, "mprob": 0.36},

  "R2T1": {"reward": 5, "penalty": -3, "mprob": 0.41},
  "R2T2": {"reward": 8, "penalty": -5, "mprob": 0.48},
  "R2T3": {"reward": 7, "penalty": -6, "mprob": 0.41},
  "R2T4": {"reward": 8, "penalty": -9, "mprob": 0.37},
  "R2T5": {"reward": 5, "penalty": -7, "mprob": 0.27},
  "R2T6": {"reward": 2, "penalty": -4, "mprob": 0.05},

  "R3T1": {"reward": 3, "penalty": -3, "mprob": 0.30},
  "R3T2": {"reward": 9, "penalty": -4, "mprob": 0.60},
  "R3T3": {"reward": 6, "penalty": -6, "mprob": 0.40},
  "R3T4": {"reward": 5, "penalty": -8, "mprob": 0.29},
  "R3T5": {"reward": 3, "penalty": -6, "mprob": 0.20},
  "R3T6": {"reward": 2, "penalty": -2, "mprob": 0.20},

  "R4T1": {"reward": 4, "penalty": -3, "mprob": 0.37},
  "R4T2": {"reward": 6, "penalty": -3, "mprob": 0.51},
  "R4T3": {"reward": 7, "penalty": -7, "mprob": 0.40},
  "R4T4": {"reward": 5, "penalty": -10, "mprob": 0.24},
  "R4T5": {"reward": 5, "penalty": -9, "mprob": 0.26},
  "R4T6": {"reward": 3, "penalty": -4, "mprob": 0.23}
}

cover_story_template = Template(
    "# Insider Attacker Game: A fun game of decision making to help keep our systems safe!!\n\n"
    "Welcome to a decision-making game where you play as an insider attacker trying to steal proprietary by attacking computers. "
    "There are six target computers. Only two are monitored at any time, randomly chosen each trial.\n\n"
    "Each target is described by a 3-tuple: (reward, penalty, mProb)\n"
    "- reward: Points earned if the attack succeeds\n"
    "- penalty: Points lost if the target is monitored\n"
    "- mProb: Probability the target is monitored\n\n"
    "How to Play:\n"
    "1. Play 4 rounds (25 trials each). Target stats change each round.\n"
    "2. In each trial, choose one of six targets:\n"
    "   - $choice1 for Target 1\n"
    "   - $choice2 for Target 2\n"
    "   - $choice3 for Target 3\n"
    "   - $choice4 for Target 4\n"
    "   - $choice5 for Target 5\n"
    "   - $choice6 for Target 6\n"
    "3. Then, decide whether to proceed with the attack:\n"
    "   - $proceed for yes\n"
    "   - $withdraw for no\n"
    "4. Outcomes:\n"
    "   - Proceed + unmonitored = gain reward\n"
    "   - Proceed + monitored = lose penalty\n"
    "   - Withdraw = 0 points\n\n"
    "Your goal: earn as many points as possible.\n\n"
)

target_summary_template = Template(
    "In this round, the targets are:\n"
    "| Target | Reward | Penalty | mProb |\n"
    "|--------|--------|---------|-------|\n"
    "| $choice1 | $reward1 | $penalty1 | $mprob1 |\n"
    "| $choice2 | $reward2 | $penalty2 | $mprob2 |\n"
    "| $choice3 | $reward3 | $penalty3 | $mprob3 |\n"
    "| $choice4 | $reward4 | $penalty4 | $mprob4 |\n"
    "| $choice5 | $reward5 | $penalty5 | $mprob5 |\n"
    "| $choice6 | $reward6 | $penalty6 | $mprob6 |\n"
)

response_template = Template(
    "You press <<$selection>>.$signal$fi Do you want to access this computer? You press <<$action>>.\n"
)

cover_story = cover_story_template.substitute(
    choice1="Target 1", choice2="Target 2", choice3="Target 3", choice4="Target 4", choice5="Target 5", choice6="Target 6",
    proceed="Proceed", withdraw="Withdraw"
)

target_summary = target_summary_template.substitute(
    choice1="Target 1", choice2="Target 2", choice3="Target 3", choice4="Target 4", choice5="Target 5", choice6="Target 6",
    reward1=rt_map["R1T1"]["reward"], penalty1=rt_map["R1T1"]["penalty"], mprob1=rt_map["R1T1"]["mprob"],
    reward2=rt_map["R1T2"]["reward"], penalty2=rt_map["R1T2"]["penalty"], mprob2=rt_map["R1T2"]["mprob"],
    reward3=rt_map["R1T3"]["reward"], penalty3=rt_map["R1T3"]["penalty"], mprob3=rt_map["R1T3"]["mprob"],
    reward4=rt_map["R1T4"]["reward"], penalty4=rt_map["R1T4"]["penalty"], mprob4=rt_map["R1T4"]["mprob"],
    reward5=rt_map["R1T5"]["reward"], penalty5=rt_map["R1T5"]["penalty"], mprob5=rt_map["R1T5"]["mprob"],
    reward6=rt_map["R1T6"]["reward"], penalty6=rt_map["R1T6"]["penalty"], mprob6=rt_map["R1T6"]["mprob"]
)

def get_target_summary(target_choices, round):
    return target_summary_template.substitute(
        choice1=target_choices[0], choice2=target_choices[1], choice3=target_choices[2], choice4=target_choices[3], choice5=target_choices[4], choice6=target_choices[5],
        reward1=rt_map[f"R{round}T1"]["reward"], penalty1=rt_map[f"R{round}T1"]["penalty"], mprob1=rt_map[f"R{round}T1"]["mprob"],
        reward2=rt_map[f"R{round}T2"]["reward"], penalty2=rt_map[f"R{round}T2"]["penalty"], mprob2=rt_map[f"R{round}T2"]["mprob"],
        reward3=rt_map[f"R{round}T3"]["reward"], penalty3=rt_map[f"R{round}T3"]["penalty"], mprob3=rt_map[f"R{round}T3"]["mprob"],
        reward4=rt_map[f"R{round}T4"]["reward"], penalty4=rt_map[f"R{round}T4"]["penalty"], mprob4=rt_map[f"R{round}T4"]["mprob"],
        reward5=rt_map[f"R{round}T5"]["reward"], penalty5=rt_map[f"R{round}T5"]["penalty"], mprob5=rt_map[f"R{round}T5"]["mprob"],
        reward6=rt_map[f"R{round}T6"]["reward"], penalty6=rt_map[f"R{round}T6"]["penalty"], mprob6=rt_map[f"R{round}T6"]["mprob"]
    )

def get_choice_response_score_summary(row, target_choice_options, action_choice_options):
    selection = target_choice_options[row["TargetNum"]-1]
    signal_str = " This computer is being monitored!" if row['Warning'] == 1 else ""
    fi_str = f" {100-int(row['Best_Signal']*100)}% of the time this computer appears as \"monitored\" the analyst is NOT present." if "FI" in row['Condition'] and row['Warning'] == 1 else ""
    # inverse mapping from action to action_choice_options
    action = action_choice_options[0] if row["Action"] == 1 else action_choice_options[1]
    return response_template.substitute(
        selection=selection, signal=signal_str, fi=fi_str, action=action
    )

all_prompts = []
df = pd.read_csv('2022-MURIBookChapter-FullData-IAG (1).csv')
df['uid'] = df['MturkID'].astype(str) + '-' + df['Condition'].astype(str)  # some participants did the task multiple times for different conditions, so we need to distinguish them

num_participants = len(df['uid'].unique())
# map from uid to [0, num_participants)
uid_map = dict(zip(df['uid'].unique(), range(num_participants)))

num_trials = 100

for participant in df['uid'].unique():
    
    participant_df = df[df['uid'] == participant]
    # sort by round and trial
    participant_df = participant_df.sort_values(by=['Round', 'Trial'])
    participant_id = uid_map[participant]

    print('Participant:', participant_id, participant)
    
    choice_options = randomized_choice_options(num_choices=8)
    target_choice_options = choice_options[:6]
    action_choice_options = choice_options[6:]
    cover_story = cover_story_template.substitute(
        choice1=target_choice_options[0], choice2=target_choice_options[1], choice3=target_choice_options[2], choice4=target_choice_options[3], choice5=target_choice_options[4], choice6=target_choice_options[5],
        proceed=action_choice_options[0], withdraw=action_choice_options[1]
    )

    prompt = cover_story
    prev_cum_outcome = 0

    for trial in range(num_trials):
        if trial == 0:
            prompt += f"Round 1:\n\n"
            prompt += get_target_summary(target_choice_options, 1)
        elif trial == 25:
            prompt += f"\n\nRound 2:\n"
            prompt += get_target_summary(target_choice_options, 2)
        elif trial == 50:
            prompt += f"\n\nRound 3:\n"
            prompt += get_target_summary(target_choice_options, 3)
        elif trial == 75:
            prompt += f"\n\nRound 4:\n"
            prompt += get_target_summary(target_choice_options, 4)

        row = participant_df.iloc[trial]
        prompt += get_choice_response_score_summary(row, target_choice_options, action_choice_options)

        if trial == 24 or trial == 49 or trial == 74 or trial == 99:
            prompt += f"End of Round, you score for this round is {int(row['Cum_Outcome']-prev_cum_outcome)} and your total score is {int(row['Cum_Outcome'])} \n"
            prev_cum_outcome = row['Cum_Outcome']

    print(prompt)
    all_prompts.append({'text': prompt, 
                        'experiment': 'aggarwal2023/iag/' + 'iag_exp', 
                        'participant': participant_id,
                        'condition': row['Condition'],
                        'age': int(row['Age']),
                        'sex': row['Sex']
                        }) 

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts) 


    

    
    
    



