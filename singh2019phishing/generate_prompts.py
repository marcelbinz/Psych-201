import pandas as pd
import sys
sys.path.append('..')
from utils import randomized_choice_options
from string import Template
import jsonlines

user_action3_desc =  """ 
1 - Respond to this
2 - Click Link open attachement
3 - Check sender
4 - Check link
5 - Delete email
6 - Report this email
"""

cover_story_template_1 = Template(
    "In this experiment, you'll classify emails as either ham (legitimate) or phishing (malicious). For each correct classification, you'll earn $reward point and for each incorrect classification, you'll lose $penalty point. "
    "Respond with $choice1 for ham, and $choice2 for phishing.\n\n"
    "The experiment has three phases:\n"
    "- Phase 1: Classify emails without feedback.\n"
    "- Phase 2: Receive feedback to improve accuracy.\n"
    "- Phase 3: Classify emails again without feedback.\n\n"
    "Feedback Type: You will be informed whether your classification was correct.\n\n"
    "Your goal is to maximize your score.\n"
)

cover_story_template_2 = Template(
    "In this experiment, you'll classify emails as either ham (legitimate) or phishing (malicious). For each correct classification, you'll earn $reward point and for each incorrect classification, you'll lose $penalty point. "
    "Respond with $choice1 for ham, and $choice2 for phishing.\n\n"
    "The experiment has three phases:\n"
    "- Phase 1: Classify emails without feedback.\n"
    "- Phase 2: Receive feedback to improve accuracy.\n"
    "- Phase 3: Classify emails again without feedback.\n\n"
    "Feedback Type:\n"
    "- Accuracy: You will be informed whether your classification was correct.\n"
    "- Email Characteristics: Each email has six key features (described below). After classification, you’ll see which of these features were flagged as suspicious by experts—helping you learn to spot common signs of phishing. \n"
    "    -- Sender mismatch: A sender mismatch is present if the email sender identity is different from what it pretends. It may be because of a spoofed display of the name or domain or because of misspelled words in an email address\n"
    "    -- Request credentials: If the phishing email contains a request for personal and sensitive or confidential information in the email.\n"
    "    -- Urgent: If the phishing email creates a sense of urgency, fear, or threat, a common technique found in phishing emails.\n"
    "    -- Offer: If the phishing emails present a reward or prize, another common phishing tactic.\n"
    "    -- Suspicious subject: If the subject line depicts urgency, fear, threat, offer or reward.\n"
    "    -- Link mismatch: A mismatch between the content of the email and the actual link may indicate this is a phishing email. Also, phishers may use an IP address instead of a URL to request personal information.\n\n"
    "Your goal is to maximize your score.\n"

)

email_template = Template(
    "\nSender: $sender\n"
    "Subject: $subject\n"
    "Body: $body\n"
)

response_template = Template(
    "You press <<$choice>>. Total Score: $score\n"
)

feedback_template_1 = Template(
    "Feedback: This was a $label email, and you detected it $correctly.\n"
)

feedback_template_2 = Template(
    "Feedback:"
    "\n- Accuracy: This was a $label email, and you detected it $correctly."
    "\n- Email Characteristics: \n"
    "    -- Sender mismatch: $sender_mismatch\n"
    "    -- Request credentials: $request_credentials\n"
    "    -- Urgent: $urgent\n"
    "    -- Offer: $offer\n"
    "    -- Suspicious subject: $suspicious_subject\n"
    "    -- Link mismatch: $link_mismatch\n"    
)

def get_email(email_id):
    row = df_email.iloc[email_id-1]
    return email_template.substitute(sender=row['Sender'], subject=row['Subject'], body=row['Body'])

def get_response(choice_options, user_action1, cum_score):
    return response_template.substitute(choice=choice_options[user_action1], score=cum_score)

def get_feedback(email_id, user_action1, feedback_template):
    row = df_email.iloc[email_id-1]
    gt = 0 if row['Type'] == 'ham' else 1
    feedback = 'correctly' if user_action1 == gt else 'incorrectly'
    # check number of vars in feedback_template
    if len(feedback_template.template.split('$')) == 2:
        return feedback_template.substitute(label=row['Type'], correctly=feedback)
    else:
        def to_yes_no(value):
            return "Yes" if value == 1 else "No"
        return feedback_template.substitute(
                label=row['Type'],
                correctly=feedback,
                sender_mismatch=to_yes_no(row['sender_mismatch']),
                request_credentials=to_yes_no(row['request_credentials']),
                urgent=to_yes_no(row['urgent']),
                offer=to_yes_no(row['offer']),
                suspicious_subject=to_yes_no(row['subject_suspecious']), 
                link_mismatch=to_yes_no(row['link_mismatch'])
            )
    
email_dataset = 'phishemailsdata_cleaned.csv'
df_email = pd.read_csv(email_dataset)
datasets = ['experiment1 - outcomefeedback.csv', 'experiment2 - incentivemanipulation.csv', 'experiment3 - detailfeedback.csv']
all_prompts = []

for dataset in datasets:

    if 'outcomefeedback' in dataset or 'incentivemanipulation' in dataset:
        cover_story_template = cover_story_template_1
        feedback_template = feedback_template_1
        
        if 'outcomefeedback' in dataset:
            reward = 1
            penalty = 0
            baseline = 0
        else:
            reward = 1
            penalty = 1
            baseline = 60              # starting score is from 60 for some reason
    
    elif 'detailfeedback' in dataset:
        cover_story_template = cover_story_template_2
        feedback_template = feedback_template_2
        reward = 1
        penalty = 0
        baseline = 0

    df = pd.read_csv(dataset)
    df = df[df['email_type']!='check'] # remove check trials  
    df['phase']=df['phase'].astype(int)
    df['trial']=df['trial'].astype(int) 
    
    num_participants = df['Mturk_id'].nunique()
    # map from Mturk_id to [0, num_participants)
    participant_map = {participant: i for i, participant in enumerate(df['Mturk_id'].unique())}
    num_trials = 60

    for participant in df['Mturk_id'].unique():

        print(f"\nParticipant: {participant_map[participant]} Mturk_id: {participant}")
        df_participant = df[df['Mturk_id'] == participant]
        df_participant = df_participant.sort_values(by=['phase', 'trial'])
        choice_options = randomized_choice_options(num_choices=2)
        cover_story = cover_story_template.substitute(choice1=choice_options[0], choice2=choice_options[1], reward=reward, penalty=penalty)
        
        prompt = cover_story

        for trial in range(num_trials):
            if trial == 0:
                prompt += '\n\nPhase 1:'
            elif trial == 10:
                prompt += '\n\nPhase 2:'
            elif trial == 50:
                prompt += '\n\nPhase 3:'
            row = df_participant.iloc[trial]
            
            email = get_email(row['email_id'])
            prompt += email

            response = get_response(choice_options, row['user_action1'], row['cum_score'] - baseline)
            prompt += response
            
            if trial >= 10 and trial < 50:
                feedback = get_feedback(row['email_id'], row['user_action1'], feedback_template)
                prompt += feedback
            
          
        all_prompts.append({
            'text': prompt, 
            'experiment': 'singh2019phishing/' + dataset , 
            'participant': participant_map[participant], 
            'timestamp': df_participant['time'].values.tolist(),
            'confidence (0-100)': df_participant['user_action2'].values.tolist(), 
            'next action': {
                'desc': user_action3_desc,
                'values': df_participant['user_action3'].values.tolist()
            }
            })
        
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)

