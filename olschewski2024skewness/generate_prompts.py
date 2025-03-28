import numpy as np
import pandas as pd
import json
import jsonlines
def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

all_prompts = []

instructions = {
    2 : f'Welcome to the Broker Game!\nIn the Broker Game, you will encounter 18 different stock markets. In each of them, you will encounter two unique stocks.\nThe stocks generate dividends and you can decide which stock you want to obtain.\nIn the beginning, you will have no information about what dividends to expect from the stocks. However, you will observe 30 dividends from each stock to learn what dividends the stocks offer.\nA stock market comprises of two boxes that represent its two stocks.\nThe dividends will appear within the boxes.\nAll dividends will be presented automatically in a quick succession, so please pay careful attention!\nAfter you have observed the stocks{"'"} dividends, you can choose the stock you would like to gain a dividend from.\nYou can click on the stock you want to obtain a dividend from.\nYou cannot revise your choice, so please choose carefully. There are no right or wrong answers, we are just interested to know which stock you prefer to have.\nAll dividends will be generated according to a mechanism, so you can learn from the observed dividends about what to expect from the respective stock.\nHowever, the stocks and hence the mechanisms are different in every stock market. You have to pay attention what dividends the stocks offer in each of the stock markets.\nYou are now ready to start to choose your favorite stocks.',
    5 : 'In the following "broker game", you will encounter six stock markets.\nIn each of them, you will see two different stocks.\nThe stocks generate dividends according to some mechanism.\nAcross 30 periods, you will make repeated choices among them.\nIn the beginning, you will have no information about the mechanisms that generate the dividends.\nOn each period, every stock generates a dividend according to its mechanism.\nYou will also see what dividends the other stock yielded.\nThe mechanisms generating the dividends do not change within a given stock market.\nBy pressing the corresponding key you choose one of the stocks.\nRemember the following rules:\nThe dividend-generating mechanism of each option does NOT change.\nAll dividend-generating mechanisms follow some distribution, so there is always something to learn.\nThe broker game is about to start.',
}

instructions[1] = instructions[2].replace('18', '14')
instructions[3] = instructions[2]
instructions[4] = instructions[2]
instructions[6] = instructions[5].replace('six', 'seven').replace('two', 'two or three').replace('You will also see what dividends the other stock yielded', 'You will also see what dividends the other stock(s) yielded')
instructions[7] = instructions[5].replace('six', 'three').replace('two', 'three').replace('30 periods', '60 periods').replace('You will also see what dividends the other stock yielded', 'You will also see what dividends the other stocks yielded')

subject_variable = {xyz : 'participant.label' for xyz in [1, 2, 3, 4]}
subject_variable[5] = 'subject_id'
subject_variable[6] = 'subject_id'
subject_variable[7] = 'subject_id'

for experiment in [1, 2, 3, 4, 5, 6, 7]:
    data = pd.read_csv('datasets/study{:02d}.csv'.format(experiment))
    participants = np.sort(data[subject_variable[experiment]].unique())
    for participant in participants:
        participant_data = data[data[subject_variable[experiment]] == participant]
        choice_options = randomized_choice_options(num_choices=3)
        prompt = instructions[experiment]
        option_label = 'Stock'
        if (experiment == 4):
            if (participant_data['player.stockintro'].unique()[0] == 0):
                prompt = f'Welcome to this study!\nIn this study you will encounter 17 different rounds.\nImagine for each round that we have two extremely large bags of ping pong balls: Bag {choice_options[0]} and Bag {choice_options[1]}. Each ball has a value between 0 and 10 written on it.\nWe will randomly choose 30 balls from each bag.\nWe will show you their values, two at a time, very quickly. You will see the value of the ball from Bag {choice_options[0]} on the left side of the screen and the value of the ball from Bag {choice_options[1]} on the right side of the screen.\nSay each value to yourself as it passes before your eyes; try to remember as much as you can. Going through all the 30 balls from each bag will take about 40 seconds.\nAfter seeing the 30 balls from each bag, you will be asked to choose one bag. One ball will be drawn from the bag you chose.\nYou will get a bonus that will be calculated based on the value shown on the ball - drawn from the bag you choose. The higher the value, the higher your bonus.\nThere will be 17 rounds and the bags are different in every round.'
                option_label = 'Bag'
                pass
            pass
        if experiment <= 5:
            prompt += f"\nThe {option_label.lower()}s' names are {choice_options[0]} and {choice_options[1]}."
            pass
        else:
            prompt += f"\nThe {option_label.lower()}s' names are {choice_options[0]}, {choice_options[1]}, and {choice_options[2]}."
            pass
        prompt += 2*'\n'
        if experiment in [1, 2, 3, 4]:
            stock_markets = participant_data.index
            for stock_market_no in range(len(stock_markets)):
                if (experiment == 4):
                    if (participant_data['player.stockintro'].unique()[0] == 0):
                        prompt += f'Round {stock_market_no+1}:\n'
                        pass
                    pass
                else:
                    prompt += f'Stock market {stock_market_no+1}:\n'
                    pass
                outcomes = np.array([np.array(json.loads(participant_data.loc[stock_markets[stock_market_no], 'player.samplesleft'])).astype(int), np.array(json.loads(participant_data.loc[stock_markets[stock_market_no], 'player.samplesright'])).astype(int)]).T
                prompt += '\n'.join([f'{option_label} {choice_options[0]} yields {outcomes[xxx, 0]} points. {option_label} {choice_options[1]} yields {outcomes[xxx, 1]} points.' for xxx in range(len(outcomes))])
                prompt += f'\nYou choose {option_label} <<{choice_options[participant_data.loc[stock_markets[stock_market_no], 'player.choice']]}>>.'
                prompt += '\n\n'
                pass
            pass
        else:
            stock_markets = np.sort(participant_data['block_no'].unique())
            for stock_market_no in stock_markets:
                prompt += f'Stock market {stock_market_no if experiment != 7 else (stock_market_no+1)}:\n'
                stock_market_data = participant_data[participant_data['block_no'] == stock_market_no].sort_values(by='trial_no' if experiment != 7 else 'trial').copy()
                stock_market_data['choice'] = stock_market_data['choice'].replace(dict(zip(['A', 'B', 'C'] if experiment != 7 else [0, 1, 2], choice_options)))
                if experiment == 5:
                    three_opts = False
                    pass
                if experiment == 7:
                    three_opts = True
                    pass
                if experiment == 6:
                    if len(stock_market_data['outcomeC'].unique()) != 1:
                        prompt += f'There are three {option_label.lower()}s to choose from.\n'
                        three_opts = True
                        pass
                    else:
                        prompt += f'There are two {option_label.lower()}s to choose from.\n'
                        three_opts = False
                        pass
                    pass
                prompt += '\n'.join([f'You choose <<{stock_market_data.loc[iii, 'choice']}>>. {option_label} {choice_options[0]} yields {stock_market_data.loc[iii, 'outcomeA' if experiment != 7 else 'outcome_right']} points. {option_label} {choice_options[1]} yields {stock_market_data.loc[iii, 'outcomeB' if experiment != 7 else 'outcome_left']} points.' + (f' {option_label} {choice_options[2]} yields {stock_market_data.loc[iii, 'outcomeC' if experiment != 7 else 'outcome_decoy']} points.' if three_opts else '') for iii in stock_market_data.index])                
                prompt += '\n\n'                
                pass
            pass
        prompt = prompt[:-2]
        all_prompts.append({'text': prompt, 'experiment': 'olschewski2024skewness/study{:02d}.csv'.format(experiment), 'participant': int(participant)})
        pass
    pass
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
    pass