#!/usr/bin/env python3
import os
import pandas as pd
import jsonlines

def main():
    # Define the output file name.
    output_file = "prompts.jsonl"
    
    # Check if the file already exists.
    if os.path.exists(output_file):
        raise FileExistsError(f"File '{output_file}' already exists. Please remove it or choose a different filename.")
    
    # Read the complete Stroop dataset.
    df = pd.read_csv("/Users/nuno/Downloads/Psych-201/busch2024_stroop/busch2024_stroop.csv")
    print(df)

    record = []
    
    # Open the JSON Lines file in exclusive creation mode ("x")
    with jsonlines.open(output_file, mode="x") as writer:

        # Group the data by participant
        for participant, df_participant in df.groupby("participant"):

            # initialize variables
            RTs = []
            prompt = 'In this task, you will be presented with color words. Once the stimulus is presented, you must respond to the ink color of the letters, ignoring the meaning of the word. Each of three possible ink colors has a corresponding response button (left, down, right).\nPlease respond as quickly and as accurately as possible. OK. Ready for the real thing? Remember, ignore the word itself; press: left for red LETTERS, down for green LETTERS, right for blue LETTERS. \n\n '


            # Iterate over each trial for this participant
            for idx, row in df_participant.iterrows():

                RTs.append(str(row["rt"]))
                prompt += 'The stimulus on the next trial is the word '+ str(row["text"]) + ', the letters of the word are colored in '+ str(row["letterColor"]) +'. '
                prompt += 'You press <<' + str(row["response"]) + '>> after '+ str(row["rt"]) +' milliseconds. The correct answer was pressing '+ str(row["corrAns"]) + '. '
                prompt += '\n'

            prompt = prompt[:-2]
            print(prompt)

            record.append({'text': prompt,
                'experiment': 'busch2024_stroop/',
                'participant': str(row["participant"]),
                'RTs': RTs,
                'age': str(row["age"])
            })

            # Write this record as a JSON line.
            # writer.write(record)
            with jsonlines.open('prompts.jsonl', 'w') as writer:
                writer.write_all(record)

if __name__ == "__main__":
    main()