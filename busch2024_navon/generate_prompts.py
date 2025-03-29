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
    
    # Read the complete Navon dataset.
    df = pd.read_csv("/Users/nuno/Downloads/Psych-201/busch2024_navon/busch2024_navon.csv")
    print(df)

    record = []
    
    # Open the JSON Lines file in exclusive creation mode ("x")
    with jsonlines.open(output_file, mode="x") as writer:

        # Group the data by participant
        for participant, df_participant in df.groupby("participant"):

            # initialize variables
            RTs = []
            prompt = 'In this experiment you will be presented with a large letter made up of smaller letters. Your task is to respond by pressing s if the SMALL letters are S, and by pressing h if the SMALL letters are H. Try to respond as quickly and as accurately as possible. Responses have to be given within 7000 milliseconds after the stimulus appears. \n\n '


            # Iterate over each trial for this participant
            for idx, row in df_participant.iterrows():

                RTs.append(str(row["rt"]))
                prompt += 'After an inter-stimulus interval of 1000 milliseconds with a black screen, the next trial starts. It begins with a fixation cross that is presented in the center of the screen for 1000 milliseconds. '
                prompt += 'Subsequently, the stimulus appears in the '+ str(row["location"]) +' quadrant of the display. The stimulus is a large letter '+ str(row["letter_big"]) + ' that is comprised of small letters '+ str(row["letter_small"]) +'. After 200 milliseconds, the stimulus is masked for 500 milliseconds with multiple dots, hiding the letters, before it disappears and the screen turns black. '
                prompt += 'You press <<' + str(row["response"]) + '>> after '+ str(row["rt"]) +' milliseconds. The correct answer was pressing '+ str(row["corrAns"]) + '. '
                prompt += '\n'

            prompt = prompt[:-2]
            print(prompt)

            record.append({'text': prompt,
                'experiment': 'busch2024_navon/',
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