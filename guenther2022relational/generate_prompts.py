import pandas as pd
import jsonlines

# load data
df = pd.read_csv('relations_compounds_cleaned.csv')

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant', 'trial_index'])

# Remap participant IDs to sequential integers starting from 1
df['participant'] = df['participant'].map({p: i+1 for i, p in enumerate(df.participant.unique())})

# Get unique participants and trial indices
participants = df['participant'].unique()
trials = range(df['trial_index'].max() + 1)


# Define experiment instructions shown to participants
# define initial prompt
instruction = 'In the following study, you will see 55 different expressions such as face room. Please indicate, for each expression, what you think it means.\n'\
    'More specifically, your task is to choose, for each expression, one of sixteen different relations connecting the two words. You can use the following table to get familiar with these relations and some examples:\n'\
    'Relation\tExample\tExample with relation\n'\
    'word2 ABOUT word1\tnewsflash\tflash ABOUT news\n'\
    'word2 BY word1\thandclap\tclap BY hand(s)\n'\
    'word2 CAUSES word1\tjoyride\tride CAUSES joy\n'\
    'word2 CAUSED BY word1\tsunbeam\tbeam CAUSED BY sun\n'\
    'word2 DERIVED FROM word1\tseafood\tfood DERIVED FROM sea\n'\
    'word2 DURING word1\tnightlife\tlife DURING night\n'\
    'word2 FOR word1\tmealtime\ttime FOR meal\n'\
    'word2 HAS word1\tbookstore\tstore HAS book(s)\n'\
    'word1 HAS word2\tdoorframe\tdoor HAS frame\n'\
    'word2 LOCATION IS word1\tfarmyard\tyard LOCATION IS farm\n'\
    'word1 LOCATION IS word2\tneckline\tneck LOCATION IS line\n'\
    'word2 MADE OF word1\tsnowman\tman MADE OF snow\n'\
    'word2 MAKES word1\thoneybee\tbee MAKES honey\n'\
    'word2 IS word1\tgirlfriend\tfriend IS girl\n'\
    'word2 USES word1\tsteamboat\tboat USES steam\n'\
    'word2 USED BY word1\twitchcraft\tcraft USED BY witch(es)\n'\
    '\n'\
    'For example, you could interpret face room as, among others, room HAS face (a magical room with a large living face on its wall), or room FOR face (the make-up artist room at a film set). Please only select one possible interpretation for each expression - the one that seems most likely to you. Of course, there are no correct or wrong answers in this task.\n'\
    'If you want to have a look at this table during the study, you can open it in a new tab using the following link:\n'\
    'Reference Sheet\n'\
    'You will not be able to return to earlier answers.\n'

# Generate individual prompts for each participant
all_prompts = []
for participant in participants:
    # Get data for current participant
    df_participant = df[df['participant'] == participant]
    participant = participant.item()
    age = df_participant['age'].iloc[0].item()
    
    # Start with instruction text
    prompt = instruction
    rt_list = []
    
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_index'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            datapoint = f'What does "{word}" mean?. You answer <<{response}>>.\n'
            prompt += datapoint    
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2022Relational',
        'participant': participant,
        'age': age
    })

# Save all prompts to JSONL file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
