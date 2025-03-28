import pandas as pd
import numpy as np
import json

def randomized_choice_options(num_choices):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)

def generate_prompts(input_csv, output_jsonl):
    df = pd.read_csv(input_csv)
    
    stimuli_prompts = {
        "BackTwo": {
            "prompt": "Imagine that you consider buying a backpack. You have the following options:",
            "options": [
                "capacity: 30L, price: $29.99",
                "capacity: 40L, price: $39.99"
            ],
            "labels": {1: 0, 2: 1, 5: None}
        },
        "BackThree": {
            "prompt": "Imagine that you consider buying a backpack. You have the following options:",
            "options": [
                "capacity: 30L, price: $29.99",
                "capacity: 40L, price: $39.99",
                "capacity: 30L, price: $39.99"
            ],
            "labels": {1: 0, 2: 1, 5: 2, 6: None}
        },
        "SpeaTwo": {
            "prompt": "Imagine that you consider buying a Bluetooth speaker. In your search, you find the following options:",
            "options": [
                "Amazon rating: 3.6/5, price: $39.99",
                "Amazon rating: 4.5/5, price: $69.99"
            ],
            "labels": {1: 0, 2: 1, 3: None}
        },
        "SpeaThree": {
            "prompt": "Imagine that you consider buying a Bluetooth speaker. In your search, you find the following options:",
            "options": [
                "Amazon rating: 3.6/5, price: $39.99",
                "Amazon rating: 4.5/5, price: $69.99",
                "Amazon rating: 3.6/5, price: $69.99"
            ],
            "labels": {1: 0, 2: 1, 3: 2, 4: None}
        },
        "HDTwo": {
            "prompt": "Imagine that you consider buying an external hard drive. You have the following options:",
            "options": [
                "capacity: 1TB, price: $39.99",
                "capacity: 2TB, price: $79.99"
            ],
            "labels": {1: 0, 2: 1, 4: None}
        },
        "HDThree": {
            "prompt": "Imagine that you consider buying an external hard drive. You have the following options:",
            "options": [
                "capacity: 1TB, price: $39.99",
                "capacity: 2TB, price: $79.99",
                "capacity: 1TB, price: $79.99"
            ],
            "labels": {1: 0, 2: 1, 4: 2, 5: None}
        },
        "HotelTwo": {
            "prompt": "Imagine that you are searching for a hotel room for your upcoming summer holidays. In your search, you find the following options:",
            "options": [
                "price: $79, hotel rating: 3-star",
                "price: $109, hotel rating: 4-star"
            ],
            "labels": {1: 0, 2: 1, 3: None}
        },
        "HotelThree": {
            "prompt": "Imagine that you are searching for a hotel room for your upcoming summer holidays. In your search, you find the following options:",
            "options": [
                "price: $79, hotel rating: 3-star",
                "price: $109, hotel rating: 4-star",
                "price: $109, hotel rating: 3-star"
            ],
            "labels": {1: 0, 2: 1, 3: 2, 4: None}
        },
        "TVTwo": {
            "prompt": "Suppose you consider buying a new TV. You pass by an electronics store that is having a oneday clearance sale. They offer the following products:",
            "options": [
                "resolution: 1920x1080, quality: good, price: $199",
                "resolution: 3840x2160, quality: excellent, price: $399"
            ],
            "labels": {1: 0, 2: 1, 3: None}
        },
        "TVThree": {
            "prompt": "Suppose you consider buying a new TV. You pass by an electronics store that is having a oneday clearance sale. They offer the following products:",
            "options": [
                "resolution: 1920x1080, quality: good, price: $199",
                "resolution: 3840x2160, quality: excellent, price: $399",
                "resolution: 1920x1080, quality: good, price: $399"
            ],
            "labels": {1: 0, 2: 1, 3: 2, 4: None}
        }
    }

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for idx, row in df.iterrows():
            for stim, config in stimuli_prompts.items():
                val = row.get(stim)
                if pd.notna(val):
                    try:
                        code = int(str(val).strip())
                        label_idx = config["labels"].get(code)

                        # Determine if there's a search option
                        total_keys = len(config["options"]) + 1
                        keys = randomized_choice_options(total_keys)

                        key_map = {i: keys[i] for i in range(len(config["options"]))}
                        search_key = keys[-1] 

                        # Construct choice text
                        options_text = "\n".join([f"Option {key_map[i]}: {desc}" for i, desc in enumerate(config["options"])])

                        instruction_line = f"What would you do? You can choose an option by pressing the corresponding key or decide to search for other options by pressing [{search_key}]."
                        chosen_key = key_map[label_idx] if label_idx is not None else search_key
                        choice_line = f"You press <<{chosen_key}>>."

                        full_prompt = f"{config['prompt']}\n\n{options_text}\n\n{instruction_line}\n{choice_line}"

                        prompt_dict = {
                            "text": full_prompt,
                            "experiment": "evangelidis2023upscaling",
                            "participant": f"participant_{idx + 1:05d}"
                        }

                        if 'Age' in row and not pd.isna(row['Age']):
                            prompt_dict["age"] = int(row['Age'])

                        gender_map = {'1': 'female', '2': 'male', 1: 'female', 2: 'male'}
                        if 'Gender' in row and not pd.isna(row['Gender']):
                            gender_value = row['Gender']
                            prompt_dict["gender"] = gender_map.get(gender_value, str(gender_value))

                        f.write(json.dumps(prompt_dict) + "\n")
                        break
                    except ValueError:
                        continue

if __name__ == "__main__":
    generate_prompts("Study 1 Data.csv", "prompts.jsonl")