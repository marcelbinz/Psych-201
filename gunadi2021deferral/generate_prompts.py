import pandas as pd
import numpy as np
import json

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))  # A–Z
    return np.random.choice(choice_options, num_choices, replace=False)

def generate_prompts(input_csv, output_jsonl):
    df = pd.read_csv(input_csv)
    df.columns = ['DecrLow', 'DecrHigh', 'IncrLow', 'IncrHigh', 'Age', 'Gender']

    def extract_condition_response(row):
        for col, condition in [('DecrLow', 'decrease_single'),
                               ('DecrHigh', 'decrease_multiple'),
                               ('IncrLow', 'increase_single'),
                               ('IncrHigh', 'increase_multiple')]:
            val = str(row[col]).strip()
            if val and val.isdigit():
                return condition, int(val)
        return None, None

    df[['condition', 'raw_response']] = df.apply(lambda row: pd.Series(extract_condition_response(row)), axis=1)
    
    response_map = {
        1: 'I would buy the tickets now',
        2: 'I would buy the tickets later'
    }
    df['response'] = df['raw_response'].map(response_map)

    gender_map = {'1': 'female', '2': 'male', 1: 'female', 2: 'male'}
    df['Gender'] = df['Gender'].map(gender_map)

    df = df[['condition', 'response', 'Age', 'Gender']].dropna()

    condition_descriptions = {
        'decrease_single':   "Four weeks ago, the tickets were priced at $594. Three weeks ago, the tickets were priced at $594. Two weeks ago, the tickets were priced at $594. One week ago, the tickets were priced at $594. Currently the tickets cost $398.",
        'decrease_multiple': "Four weeks ago, the tickets were priced at $594. Three weeks ago, the tickets were priced at $572. Two weeks ago, the tickets were priced at $515. One week ago, the tickets were priced at $447. Currently the tickets cost $398.",
        'increase_single':   "Four weeks ago, the tickets were priced at $202. Three weeks ago, the tickets were priced at $202. Two weeks ago, the tickets were priced at $202. One week ago, the tickets were priced at $202. Currently the tickets cost $398.",
        'increase_multiple': "Four weeks ago, the tickets were priced at $202. Three weeks ago, the tickets were priced at $224. Two weeks ago, the tickets were priced at $281. One week ago, the tickets were priced at $349. Currently the tickets cost $398.",
    }

    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for idx, row in df.iterrows():
            keys = randomized_choice_options(2)
            key_map = {
                'I would buy the tickets now': keys[0],
                'I would buy the tickets later': keys[1]
            }
            chosen_key = key_map[row['response']]

            context = (
                "Imagine that you are buying flight tickets for your upcoming holidays. Only one airline "
                "flies directly to that destination.\n\n"
                f"{condition_descriptions[row['condition']]}\n\n"
                f"Would you buy the tickets now or later? You can press [{key_map['I would buy the tickets now']}] to buy now or "
                f"[{key_map['I would buy the tickets later']}] to buy later.\n"
                f"You press <<{chosen_key}>>."
            )

            prompt = {
                "text": context,
                "experiment": "gunadi2021deferral",
                "participant": f"participant_{idx + 1:05d}"
            }

            if pd.notna(row['Age']):
                prompt["age"] = int(row['Age'])
            if pd.notna(row['Gender']):
                prompt["gender"] = row['Gender']

            f.write(json.dumps(prompt) + '\n')

if __name__ == "__main__":
    generate_prompts("Study 1a - Data.csv", "prompts.jsonl")