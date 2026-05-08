
import jsonlines
from datasets import load_dataset

datasets = ['testing_t1']

side_information = {}
for dataset in datasets:
    file = 'psych101_side_information_' + dataset + '.jsonl'
    with jsonlines.open(file) as reader:
        for obj in reader:
            dict_partcipants = {}
            dict_partcipants['experiment'] = obj['experiment']
            dict_partcipants['participant'] = obj['participant']

            if 'RTs' in obj.keys():
                dict_partcipants['RTs'] = obj['RTs']
            else:
                dict_partcipants['RTs'] = []

            if 'gender' in obj.keys():
                dict_partcipants['gender'] = obj['gender']
            else:
                dict_partcipants['gender'] = 'N/A'

            if 'age' in obj.keys():
                dict_partcipants['age'] = obj['age']
            else:
                dict_partcipants['age'] = 'N/A'

            if 'nationality' in obj.keys():
                dict_partcipants['nationality'] = obj['nationality']
            else:
                dict_partcipants['nationality'] = 'N/A'

            if 'education' in obj.keys():
                dict_partcipants['education'] = obj['education']
            else:
                dict_partcipants['education'] = 'N/A'

            if 'diagnosis' in obj.keys():
                dict_partcipants['diagnosis'] = obj['diagnosis']
            else:
                dict_partcipants['diagnosis'] = 'N/A'

            side_information[(obj['experiment'], obj['participant'])] = dict_partcipants

full_data = []
for dataset in datasets:
    file = 'psych101_' + dataset + '.jsonl'
    with jsonlines.open(file) as reader:
        for obj in reader:
            # if side information is available
            if (str(obj['experiment']), str(obj['participant'])) in side_information.keys():
                assert len(obj['experiment'].split('/')) == 2
                full_data.append({
                    'text': obj['text'],
                    'study': str(obj['experiment']).split('/')[0],
                    'experiment': str(obj['experiment']),
                    'participant': str(obj['participant']),
                    'RTs': side_information[(str(obj['experiment']), str(obj['participant']))]['RTs'],
                    'gender': side_information[(str(obj['experiment']), str(obj['participant']))]['gender'],
                    'age': side_information[(str(obj['experiment']), str(obj['participant']))]['age'],
                    'nationality': side_information[(str(obj['experiment']), str(obj['participant']))]['nationality'],
                    'education': side_information[(str(obj['experiment']), str(obj['participant']))]['education'],
                    'diagnosis': side_information[(str(obj['experiment']), str(obj['participant']))]['diagnosis'],
                })
            # if no side information is available
            else:
                assert len(obj['experiment'].split('/')) == 2
                full_data.append({
                    'text': obj['text'],
                    'study': str(obj['experiment']).split('/')[0],
                    'experiment': str(obj['experiment']),
                    'participant': str(obj['participant']),
                    'RTs': [],
                    'gender': 'N/A',
                    'age': 'N/A',
                    'nationality': 'N/A',
                    'education': 'N/A',
                    'diagnosis': 'N/A',
                })


print(len(full_data))
with jsonlines.open('psych101-testing/psych101_with_side_information.jsonl', 'w') as writer:
    writer.write_all(full_data)
