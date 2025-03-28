import sys
sys.path.append("..")

import numpy as np
import pandas as pd
import jsonlines

from utils import randomized_choice_options

# CSV file downloaded from
#   https://arc-git.mpib-berlin.mpg.de/ciranka/developing_marbles 
#   folder A_raw_data
datasets = ["TidyMarbleNew.csv"] 
all_prompts = []


sexfromGerman = {
  'Maennlich': 'M',
  'Weiblich': 'F'
}

choice_options = randomized_choice_options(num_choices=2)
jarindex = {
  70: 0,
  74: 1
}
jarindex_inverted = {
  70: 1,
  74: 0
}
def convert_X(X, Y):
    if ',' in X:
        # Convert to a list of integers
        return list(map(int, X.split(','))), list(map(int, Y.split(','))), True
    else:
        # Convert to a single integer
        return int(X), int(Y), False
def xMarble(x):
    if x == 1:
        return str(x) + ' marble'
    elif x > 1:
        return str(x) + ' marbles'
def xMarblewas(x):
    if x == 0:
        return 'no marble was'
    elif x == 1:
        return str(x) + ' marble was'
    elif x > 1:
        return str(x) + ' marbles were'

for dataset in datasets:
    df = pd.read_csv(dataset)
    print(df)


    for participant in df['subject'].unique():
        RTs = []

        df_participant = df[(df['subject'] == participant)]
        age = df_participant.age.iloc[0]
        sex = sexfromGerman[df_participant.sex.iloc[0]]

        df_participant_solo   = df_participant[(df_participant.test_part == 'SoloChoice')]
        df_participant_social = df_participant[(df_participant.test_part == 'SocialChoice')]

    
        # general instruction
        prompt = "In this task, you are repeatedly presented with two marble jars labeled " + choice_options[0] + " and " +  choice_options[1] + ".\n"\
            "At each trial, you have to decide which of the two jars you want to draw a marble from.\n"\
            "You can choose a jar by pressing its corresponding key.\n"\
            "When you select one of the jars, a marble is randomly drawn from that jar at the end of the trial.\n"\
            "There are more than 1000 marbles in each jar, which is a lot.\n"\
            "When a blue marble is drawn, you will be credited with the bonus points corresponding to that jar.\n"\
            "These bonus boints of each jar will be communicated with you at each trial.\n"\
            "If a red marble is drawn, you do not receive a bonus.\n"\
            "At each trial, one of the two jars conatins only blue marbles.\n"\
            "A jar full of blue marbles is a safe bet if you choose to go for it.\n"\
            "This means that, if you choose this jar in the trial, then you will receive the bonus points of this jar with a probability of 100 percent.\n"\
            "The other jar offers higher bonus points.\n"\
            "But there can be both blue and red marbles in this jar!\n"\
            "This means that if you choose this jar, you will not get the bonus with the 100 percent probability. So, we call this jar the risky jar.\n"\
            "For example, there may be half blue and half red marbles in the risky jar.\n"\
            "You can decide for yourself at each trial whether you want to choose the risky jar with red and blue marbles or the safe jar with only blue marbles.\n"\
            "If you choose the risky jar, then you may get a larger bonus than what you would get by choosing the safe jar, but you may also not get a bonus at all.\n"\
            "Think carefully about your decision every time! It's worth it!\n"\
            "At some trials, there is an additional challenge: The risky jar is opaque!\n"\
            "This means that you do not know the ratio of blue and red marbles at the beginning of the trial\n"\
            "Before you make your decision on an opaque risky jar, you can learn something about how likely it is that a blue or a red marble is drawn.\n"\
            "This means that you can learn something about how likely it is that you will win the bonus if you choose the opaque risky jar.\n"\
            "So that you can learn something about probability, we will pull some marbles out of the jar 5 times in a row.\n"\
            "Then we will tell you how many of them were blue and how many were red.\n"\
            "This will help you estimate how many blue and how many red marbles are in the jar.\n"\
            "Important! You don't see all the marbles in the jar. In reality, there are more than 1000 marbles in a jar, so that's a lot of marbles!\n"\
            "In trials when the risky jar is opaque, we ask you tell us your estimate of the ratio of blue marbles in the jar.\n"\
            "We ask you to report this before you choose a jar. Only then can you choose one of the jars.\n"\
            "From time to time we would like to know how sure you are about this assessment.\n"\
            "To do this, please report the percentage of (from 0 to 100) how sure you are that the ratio of blue marbles you entered is correct.\n"\
            "Now the experiment starts.\n"\
            "Remember that you choose your jar by pressing the corresponding key for the marble jar: " + choice_options[0] + " or " +  choice_options[1] + ".\n\n"

        trial = 0
        # solo condition
        for index_trial, df_trial in df_participant_solo.iterrows():
            # jar indices
            safe_jar   = jarindex_inverted[df_trial.riskyKey]
            risky_jar  = jarindex[df_trial.riskyKey]
            chosen_jar = jarindex[df_trial.key_press]
            # jar values
            safe_value  = df_trial.valueSure
            risky_value = df_trial.valueGamble
            p_blue = df_trial.probGamble * 100
            # sampling of marbles
            n_blue, n_red, ifopaque = convert_X(df_trial.red_marbles, df_trial.blue_marbles)
            p_blue_hat = df_trial.PercentBlueEstimate
            p_blue_hat_conf = df_trial.HowSure
            # payoff
            reward = df_trial.payoff
            total_reward = df_trial.cumulatedPayoff
            trial += 1
            prompt += 'Trial ' + str(trial) + '\n'
            if ifopaque:
                prompt += 'In this trial, the risky jar is opaque.\n'
                prompt += 'For 5 consecutive times, we sampled some marbles from this jar. Here are the results:\n'
                for i in range(5):
                    prompt += 'In sampling round ' + str(i+1) + ', we drew ' + xMarble(n_blue[i] + n_red[i]) + ', among which, '
                    prompt += xMarblewas(n_blue[i]) + ' blue, and ' + xMarblewas(n_red[i]) + ' red.\n'
                prompt += 'You report <<' + str(p_blue_hat) + '>> percent as your estimate of the ratio of blue marbles in the opaque risky jar.\n'
                RTs.append(np.nan)
                if p_blue_hat_conf > -1:
                    prompt += 'In this trial, you are also asked to report (from 0 to 100) how sure you are that the ratio of blue marbles you entered is correct.\n'
                    prompt += 'You report <<' + str(p_blue_hat_conf) + '>>.\n'
                    RTs.append(np.nan)
            else:
                prompt += 'In this trial, ' + str(p_blue) + ' percent of marbles in the risky jar are blue, and the other ' + str(100 - p_blue) + ' percent of marbles are red.\n'

            prompt +=     'Jar ' + choice_options[safe_jar]  + ' is the safe jar with '  + str(safe_value)  + ' bonus points, '
            prompt += 'and jar ' + choice_options[risky_jar] + ' is the risky jar with ' + str(risky_value) + ' bonus points.\n'
            prompt += 'You choose jar <<' + choice_options[chosen_jar] + '>>.\n'
            RTs.append(df_trial.rt)

            if trial % 5 == 0:
                prompt += 'So far in the experiment, you recived ' + str(total_reward) + ' bonus points in total.\n'
        prompt += '\n'

        # instruction for social part
        prompt += "Now we come to the second part of the task.\n"\
            "This part is very similar to the previous one in the sense that you are repeatedly presented with two marble jars labeled " + choice_options[0] + " and " +  choice_options[1] + ".\n"\
            "At each trial, you have to decide which of the two jars you want to draw a marble from.\n"\
            "You can choose a jar by pressing its corresponding key.\n"\
            "However, there is also a small change.\n"\
            "Our database stores the decisions of people who have completed a similar experiment before you.\n"\
            "Our algorithm found a person whose decisions were similar to yours.\n"\
            "This person made his or her decisions based on the same probabilities and the same amount of bonus points as you just did.\n"\
            "At each trial, we will show you their decisions before you make your choice in the next rounds.\n"\
            "Otherwise everything remains as usual.\n"\
            "Whether it is worth taking the risk of choosing the jar with blue and red marbles is something you have to decide for yourself each time.\n"\
            "If you choose the risky jar, you may get a large bonus, but you may also get no bonus at all.\n"\
            "If you choose the safe jar with only blue marbles, you always get the indicated bonus.\n"\
            "Now the experiment starts.\n"\
            "Remember that you choose your jar by pressing the corresponding key for the marble jar: " + choice_options[0] + " or " +  choice_options[1] + ".\n\n"

        # social condition
        for index_trial, df_trial in df_participant_social.iterrows():
            # jar indices
            safe_jar   = jarindex_inverted[df_trial.riskyKey]
            risky_jar  = jarindex[df_trial.riskyKey]
            chosen_jar = jarindex[df_trial.key_press]
            # jar values
            safe_value  = df_trial.valueSure
            risky_value = df_trial.valueGamble
            p_blue = df_trial.probGamble * 100
            # sampling of marbles
            n_blue, n_red, ifopaque = convert_X(df_trial.red_marbles, df_trial.blue_marbles)
            p_blue_hat = df_trial.PercentBlueEstimate
            p_blue_hat_conf = df_trial.HowSure
            # payoff
            reward = df_trial.payoff
            total_reward = df_trial.cumulatedPayoff
            # the advice choice
            if df_trial.OtherChoseRisk == 0:
                adviced_choice = safe_jar
            elif df_trial.OtherChoseRisk == 1:
                adviced_choice = risky_jar

            trial += 1
            prompt += 'Trial ' + str(trial) + '\n'
            if ifopaque:
                prompt += 'In this trial, the risky jar is opaque.\n'
                prompt += 'For 5 consecutive times, we sampled some marbles from this jar. Here are the results:\n'
                for i in range(5):
                    prompt += 'In sampling round ' + str(i+1) + ', we drew ' + xMarble(n_blue[i] + n_red[i]) + ', among which, '
                    prompt += xMarblewas(n_blue[i]) + ' blue, and ' + xMarblewas(n_red[i]) + ' red.\n'
                prompt += 'You report <<' + str(p_blue_hat) + '>> percent as your estimate of the ratio of blue marbles in the opaque risky jar.\n'
                RTs.append(np.nan)
                if p_blue_hat_conf > -1:
                    prompt += 'In this trial, you are also asked to report (from 0 to 100) how sure you are that the ratio of blue marbles you entered is correct.\n'
                    prompt += 'You report <<' + str(p_blue_hat_conf) + '>>.\n'
                    RTs.append(np.nan)
            else:
                prompt += 'In this trial, ' + str(p_blue) + ' percent of marbles in the risky jar are blue, and the other ' + str(100 - p_blue) + 'percent of marbles are red.\n'

            prompt +=     'Jar ' + choice_options[safe_jar]  + ' is the safe jar with '  + str(safe_value)  + ' bonus points,'
            prompt += 'and jar ' + choice_options[risky_jar] + ' is the risky jar with ' + str(risky_value) + ' bonus points.\n'
            prompt += 'The other person chose jar ' + choice_options[adviced_choice] + '.\n'
            prompt += 'You choose jar <<' + choice_options[chosen_jar] + '>>.\n'
            RTs.append(df_trial.rt)

            if trial % 5 == 0:
                prompt += 'So far in the experiment, you recived ' + str(total_reward) + ' bonus points in total.\n'
        prompt += '\n'


        prompt = prompt[:-2]
        print(prompt)

        all_prompts.append({'text': prompt,
            'experiment': 'fciranka_vandenbos_2024/' + dataset,
            'participant': str(participant),
            'RTs': RTs,
            'age': str(age),
        })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
