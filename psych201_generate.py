
import jsonlines
import json
from glob import glob
import numpy as np
import pandas as pd
from utils import *
import math

def map_experiment_name(old_name, text):
    remapping = {
        'riskRatings': 'hussain2024risk/riskRatings',
        'psychRatings': 'hussain2024risk/psychRatings',
        'dezfouli//Users/elifkara/Desktop/Helmholtz/dezfouili/dezfouli2019/choices_diagno.csv': 'dezfouli2019/choices_diagno.csv',
        'Adolescent': 'giron2023developmentalExploration/adolescent',
        'sampling_paradigm': 'anvari2024sampling_paradigm/',
        'Decisions From Experience': 'frey2017dfe/',
        'Lotteries': 'frey2017lotteries/',
        'exp2': 'cheung2025omissionyesnobias/exp2',
        'alien_game': 'anvari2024alien/',
        'MPL': 'frey2017mpl/',
        'observe_or_bet': 'anvari2024observe_bet/',
        'multi_armed_bandit': 'anvari2024armed_bandit/',
        'exp4.csv': 'vantiel2021probabilisticpragmatics/exp4.csv',
        'RAT/RAT.csv': 'sun2025rat/',
        'exp3': 'cheung2025omissionyesnobias/exp3',
    }

    if 'online public goods game' in text:
        return 'alsobay2025publicGoodsGame/'

    if old_name in remapping.keys():
        #print('renaming...')
        return remapping[old_name]
    else:
        return old_name

def map_text(text, experiment):
    if experiment in ['vantiel2020probabilistic_pragmatics/exp2a.csv', 'vantiel2022meaninguse/exp2', 'vantiel2021probabilisticpragmatics/exp4.csv', 'vantiel2020probabilistic_pragmatics/exp2b.csv', 'olschewski2025optimal/1', 'witte2024interventionStudy', 'hu2023lm-pragmatics', 'Ying2023NIPE']:
      text = text.replace(">>\n", ">>.\n")
    if experiment == 'pirrone_2018_dots/data_Pirrone2018_dots_Psych-201.csv':
      text = text.replace(">>, t", ">>. T")
      text = text.replace(">>, and", ">> and")
    if experiment in ['heffner2022economicgames/prd_data.csv', 'heffner2022economicgames/pgg_data.csv']:
      text = text.replace("$<<", "<<")
      text = text.replace(">>", ">> dollars")
    if experiment == 'holton2024goalcommitment':
      text = text.replace("collect<<", "collect <<")

    text = text.replace("<<skip>>", "<<skip>>.").replace("<<-", "<< -").replace("<<think>>", "<< think>>").replace("More Details >>", "More Details ->")

    return text


files = glob('*/*.jsonl')
print(files)
print(len(files))

l_symb = '<<'
r_symb = '>>'

all_keys = set()

full_data = []
number_participants = []
total_experiments = 0
total_choices = 0

for file in files:

    total_experiments += 1
    exp_participants = 0

    if True:
        with jsonlines.open(file, loads=json.loads) as reader:
            # study name
            study_name = file.split('/')[0]
            print(study_name)

            for obj in reader:
                # check that mandatory keys are there
                assert 'text' in obj.keys()
                assert 'participant' in obj.keys()
                assert 'experiment' in obj.keys()
                all_keys.update(obj.keys())

                # check that RTs match number of choices
                if 'RTs' in obj.keys():
                    if len(obj['RTs']) > 0:
                        assert len(obj['RTs']) == obj['text'].count(l_symb), (obj['experiment'], obj['participant'], len(obj['RTs']), obj['text'].count(l_symb))

                # create dictionary
                if study_name == 'psych101':
                    dict_partcipants = {
                        'text': obj['text'],
                        'study': obj['study'],
                        'experiment': str(obj['experiment']),
                        'participant': str(obj['participant']),
                        'is_psych101': True,
                        'is_psych101_test': False,
                    }
                elif study_name == 'psych101-testing':
                    dict_partcipants = {
                        'text': obj['text'],
                        'study': obj['study'],
                        'experiment': str(obj['experiment']),
                        'participant': str(obj['participant']),
                        'is_psych101': True,
                        'is_psych101_test': True,
                    }
                else:
                    fixed_experiment_name = map_experiment_name(str(obj['experiment']), obj['text'])
                    dict_partcipants = {
                        'text': map_text(obj['text'], fixed_experiment_name),
                        'study': study_name,
                        'experiment': fixed_experiment_name,
                        'participant': str(obj['participant']),
                        'is_psych101': False,
                        'is_psych101_test': False,
                    }

                # rename variables
                if "STICSAsoma" in obj.keys():
                    obj["STICSA-T somatic"] = obj.pop("STICSAsoma")
                if "STICSAcog" in obj.keys():
                    obj["STICSA-T cognitive"] = obj.pop("STICSAcog")
                if "STAI" in obj.keys():
                    obj["STAI-S"] = obj.pop("STAI")
                if "stai" in obj.keys():
                    obj["STAI-T"] = obj.pop("stai")
                if "stai_total" in obj.keys():
                    obj["STAI-T"] = obj.pop("stai_total")
                if "BIS" in obj.keys():
                    obj["bis"] = obj.pop("BIS")
                if "audit_total" in obj.keys():
                    obj["AUDIT"] = obj.pop("audit_total")
                if "bis_total" in obj.keys():
                    obj["BIS-10"] = obj.pop("bis_total")
                if "sex" in obj.keys():
                    obj["gender"] = obj.pop("sex")
                if "location" in obj.keys():
                    obj["nationality"] = obj.pop("location")

                # case as needed
                if ('RTs' in obj.keys()) and (len(obj['RTs']) > 0):
                    dict_partcipants['RTs'] = cast_rts(obj['RTs'])
                else:
                    dict_partcipants['RTs'] = obj['text'].count(l_symb) * [math.nan]

                if 'gender' in obj.keys():
                    dict_partcipants['gender'] = cast_gender(obj['gender'])
                else:
                    dict_partcipants['gender'] = 'N/A'

                if 'age' in obj.keys():
                    dict_partcipants['age'] = cast_age(obj['age'])
                else:
                    dict_partcipants['age'] = 'N/A'

                if 'nationality' in obj.keys():
                    dict_partcipants['nationality'] = cast_nationality(obj['nationality'])
                else:
                    dict_partcipants['nationality'] = 'N/A'

                if 'education' in obj.keys():
                    dict_partcipants['education'] = cast_education(obj['education'])
                else:
                    dict_partcipants['education'] = 'N/A'

                if 'diagnosis' in obj.keys():
                    dict_partcipants['clinical diagnosis'] = cast_diagnosis(obj['diagnosis'])
                else:
                    dict_partcipants['clinical diagnosis'] = 'N/A'

                # add questionaire stuff
                if 'STICSA-T somatic' in obj.keys():
                    dict_partcipants['STICSA-T somatic'] = str(obj['STICSA-T somatic'])
                else:
                    dict_partcipants['STICSA-T somatic'] = 'N/A'

                if 'STICSA-T cognitive' in obj.keys():
                    dict_partcipants['STICSA-T cognitive'] = str(obj['STICSA-T cognitive'])
                else:
                    dict_partcipants['STICSA-T cognitive'] = 'N/A'

                if 'STAI-S' in obj.keys():
                    dict_partcipants['STAI-S'] = str(obj['STAI-S'])
                else:
                    dict_partcipants['STAI-S'] = 'N/A'

                if 'STAI-T' in obj.keys():
                    dict_partcipants['STAI-T'] = str(int(obj['STAI-T']))
                else:
                    dict_partcipants['STAI-T'] = 'N/A'

                if 'IUS' in obj.keys():
                    dict_partcipants['IUS'] = str(obj['IUS'])
                else:
                    dict_partcipants['IUS'] = 'N/A'

                if 'RRQ' in obj.keys():
                    dict_partcipants['RRQ'] = str(obj['RRQ'])
                else:
                    dict_partcipants['RRQ'] = 'N/A'

                if 'AUDIT' in obj.keys():
                    dict_partcipants['AUDIT'] = cast_int(obj['AUDIT'])
                else:
                    dict_partcipants['AUDIT'] = 'N/A'

                if 'DAST' in obj.keys():
                    dict_partcipants['DAST'] = str(obj['DAST'])
                else:
                    dict_partcipants['DAST'] = 'N/A'

                if 'pswq' in obj.keys():
                    dict_partcipants['PSWQ'] = str(obj['pswq'])
                else:
                    dict_partcipants['PSWQ'] = 'N/A'

                if 'gad7' in obj.keys():
                    dict_partcipants['GAD-7'] = str(obj['gad7'])
                else:
                    dict_partcipants['GAD-7'] = 'N/A'

                if 'sds_total' in obj.keys():
                    dict_partcipants['SDS'] = str(int(obj['sds_total']))
                else:
                    dict_partcipants['SDS'] = 'N/A'

                if 'oci_total' in obj.keys():
                    dict_partcipants['OCI'] = str(int(obj['oci_total']))
                else:
                    dict_partcipants['OCI'] = 'N/A'

                if 'PHQ' in obj.keys():
                    dict_partcipants['PHQ-9'] = str(int(obj['PHQ']))
                else:
                    dict_partcipants['PHQ-9'] = 'N/A'

                if 'phq8' in obj.keys():
                    dict_partcipants['PHQ-8'] = str(int(obj['phq8']))
                else:
                    dict_partcipants['PHQ-8'] = 'N/A'

                if 'bas_drive' in obj.keys():
                    dict_partcipants['BAS Drive'] = str(int(obj['bas_drive']))
                else:
                    dict_partcipants['BAS Drive'] = 'N/A'

                if 'bas_fun_seeking' in obj.keys():
                    dict_partcipants['BAS Fun Seeking'] = str(int(obj['bas_fun_seeking']))
                else:
                    dict_partcipants['BAS Fun Seeking'] = 'N/A'

                if 'bas_reward_response' in obj.keys():
                    dict_partcipants['BAS Reward Responsiveness'] = str(int(obj['bas_reward_response']))
                else:
                    dict_partcipants['BAS Reward Responsiveness'] = 'N/A'

                if 'BDI-II score' in obj.keys():
                    dict_partcipants['BDI-II'] = str(int(obj['BDI-II score']))
                else:
                    dict_partcipants['BDI-II'] = 'N/A'

                if 'bis' in obj.keys():
                    dict_partcipants['BIS-11'] = str(cast_int(obj['bis']))
                else:
                    dict_partcipants['BIS-11'] = 'N/A'

                if 'BIS-10' in obj.keys():
                    dict_partcipants['BIS-10'] = str(cast_int(obj['BIS-10']))
                else:
                    dict_partcipants['BIS-10'] = 'N/A'


                full_data.append(dict_partcipants)
                exp_participants += 1
                total_choices += dict_partcipants['text'].count("<<")

    number_participants.append(exp_participants)

print('Number of participants:', len(full_data))
print('Maximum number of participants', np.array(number_participants).max())
print('Total choices:', total_choices)

print(all_keys)
# save all data sets
with jsonlines.open('psych201.jsonl', 'w') as writer:
    writer.write_all(full_data)
