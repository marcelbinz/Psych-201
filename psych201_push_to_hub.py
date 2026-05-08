from datasets import load_dataset
from collections import defaultdict, Counter
import numpy as np 
from transformers import AutoTokenizer
import re

psych201 = load_dataset("json", data_files="psych201.jsonl")['train']
print(psych201)

PAT = re.compile(r"<<(.*?)>>", flags=re.DOTALL)

def remove_chevrons_except_single_upper(text: str) -> str:
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        return m.group(0) if re.fullmatch(r"[A-Z]", inner) else inner
    return PAT.sub(repl, text)


exclude_studies = {
    "demircan2024evaluatingcategory",
    "demircan2024evaluatingreward",
    "feher2020humans",
    "xu2021novelty",
    "singh2022representing",
    "jansen2021logic",
}

single_character_experiments = [
    'Thoma_et_al_2025_probability_learning', 'Thoma_et_al_2025_risky_choice', 'aggarwal2023/iag/iag_exp', 'agrawal2024stress/april2020_covid_problems.csv', 
    'agrawal2024stress/june2020_covid_problems.csv', 'agrawal2024stress/march2020_covid_problems.csv', 'agrawal2024stress/nov2020_covid_problems.csv', 
    'akata2023repeatedgames/repgames.csv', 'anvari2024armed_bandit/', 'anvari2024sampling_paradigm/', 'awad2018moral/SharedResponses.csv', 'badham2017deficits/exp1.csv', 
    'bahrami2020four/exp.csv', 'bavard2018magnitude/"Experiment0"', 'bavard2018magnitude/"Experiment1"', 'bavard2021range/1.0', 'bavard2021range/2.0', 'bavard2021range/3.0', 
    'bavard2021range/4.0', 'bavard2021range/5.0', 'bavard2021range/6.0', 'bavard2021range/7.0', 'bavard2021range/8.0', 'bavard2023functional/exp1.csv', 
    'bavard2023functional/exp2.csv', 'binz2022heuristics/exp1.csv', 'binz2022heuristics/exp2.csv', 'binz2022heuristics/exp4.csv', 'breslav2022shuffle/exp1', 
    'busch2024_navon/', 'chambon2020feedback/1', 'chambon2020feedback/2', 'chambon2020feedback/3', 'decker2016twostep', 'demircan2024evaluatingcategory', 
    'demircan2024evaluatingreward', 'dezfouli2019/choices_diagno.csv', 'dubois2022value/exp1.csv', 'enkavi2019adaptivenback/exp1.csv', 'enkavi2019gonogo/exp1.csv', 
    'enkavi2019recentprobes/exp1.csv', 'evangelidis2023upscaling', 'fan2022trait/exp1_bandit_task_scale.csv', 'feher2020humans/exp1.csv', 'feng2021dynamics/exp1.csv', 
    'flesch2018comparing/exp1.csv', 'franke2024bayesian/data-raw-human.csv', 'frankedegen2016reasoning-exp1', 'frankedegen2016reasoning-exp2', 'frey2017cct/exp1.csv', 
    'frey2017lotteries/', 'frey2017mpl/', 'frey2017risk/exp1.csv', 'gershman2018deconstructing/exp1.csv', 'gershman2018deconstructing/exp2.csv', 'gershman2020reward/exp1.csv', 
    'gillan2016characterizing/exp1.csv', 'gillan2016characterizing/exp2.csv', 'guenther2020LDT', 'guenther2020TS', 'guenther2023Grammaticality', 'gunadi2021deferral', 
    'haines2020/intertemporal_choice', 'hebart2023things/exp1.csv', 'heffner2022economicgames/ug_data.csv', 'hilbig2014generalized/exp1.csv', 'hu2023lm-pragmatics', 
    'kool2016when/exp1.csv', 'kool2016when/exp2.csv', 'kool2017cost/exp1.csv', 'kool2017cost/exp2.csv', 'lefebvre2017behavioural/exp1.csv', 'lefebvre2017behavioural/exp2.csv', 
    'ludwig2023human/exp0.csv', 'ludwig2023human/exp1.csv', 'ludwig2023human/exp2.csv', 'marshall_2022_brightness/data_Marshall2022_birghtness_Psych-201.csv', 
    'nasioulas2024feedback/exp1', 'nasioulas2024feedback/exp2', 'nasioulas2024feedback/exp3', 'nasioulas2024feedback/exp4', 'nasioulas2024feedback/exp5', 
    'nasioulas2024feedback/exp6', 'nasioulas2024feedback/exp7', 'nussenbaum2020twostep', 'nussenbaum2023novelty', 'olschewski2024skewness/study01.csv', 
    'olschewski2024skewness/study02.csv', 'olschewski2024skewness/study03.csv', 'olschewski2024skewness/study04.csv', 'olschewski2024skewness/study05.csv', 
    'olschewski2024skewness/study06.csv', 'olschewski2024skewness/study07.csv', 'olschewski2025optimal/1', 'palminteri2017confirmation', 'peterson2021using/exp1.csv', 
    'pike2023catastrophizing/', 'pirrone_2018_dots/data_Pirrone2018_dots_Psych-201.csv', 'pirrone_unpublished_food/data_Pirrone_food_Psych-201.csv', 
    'pirrone_unpublished_lottery/data_Pirrone_utility_Psych-201.csv', 'plonsky2018when/exp1.csv', 'potter2017twostep', 'rosenbaum2022valence/MemDF.csv', 
    'ruggeri2022globalizability/exp1.csv', 'russek2024heuristics/exp.csv', 'sadeghiyeh2020temporal/exp1.csv', 'sandbrink2024metacontrol/behavior_24-01-22_day1.pkl', 
    'sandbrink2024metacontrol/behavior_24-01-22_day2.pkl', 'sandbrink2024metacontrol/behavior_24-01-22_day2B.pkl', 'sandbrink2024metacontrol/behavior_24-01-22_day3.pkl', 
    'sandbrink2024metacontrol/behavior_24-01-22_day3B.pkl', 'sandbrink2024metacontrol/behavior_24-01-29_day1.pkl', 'sandbrink2024metacontrol/behavior_24-01-29_day2.pkl', 
    'sandbrink2024metacontrol/behavior_24-01-29_day2B.pkl', 'sandbrink2024metacontrol/behavior_24-01-29_day3.pkl', 'sandbrink2024metacontrol/behavior_24-01-29_day3B.pkl', 
    'shahar2019twosteptask/TST_nspn.csv', 'singh2019phishing/experiment1 - outcomefeedback.csv', 'singh2019phishing/experiment2 - incentivemanipulation.csv', 
    'singh2019phishing/experiment3 - detailfeedback.csv', 'somerville2017charting/exp1.csv', 'speekenbrink2008learning/exp1.csv', 'spektor2019contexteffects/exp1.csv', 
    'spektor2019contexteffects/exp2.csv', 'spektor2019contexteffects/exp3.csv', 'spektor2019contexteffects/exp3r.csv', 'spektor2019contexteffects/exp4.csv', 
    'spektor2024lossaversion/exp1.csv', 'spektor2024lossaversion/exp2.csv', 'spektor2024lossaversion/exp3.csv', 'steingroever2015data/exp1.csv', 'steingroever2015data/exp2.csv', 
    'steingroever2015data/exp3.csv', 'suthaharan2021paranoia/exp_Reed_2020.csv', 'suthaharan2021paranoia/exp_Suthaharan_2021.csv', 'tomov2021multitask/exp1.csv', 
    'tomov2021multitask/exp3.csv', 'vandendriessche2022depression', 'waltz2020differential/exp1.csv', 'wilson2014humans/exp1.csv', 'wilson2014humans/exp2.csv', 
    'wilson2014humans/exp3.csv', 'wilson2014humans/exp4.csv', 'wilson2014humans/exp5.csv', 'witte_thalmann2024exploration/', 'wu2023chunking/exp1.csv', 'wu2023chunking/exp2.csv', 
    'wulff2018description/exp1.csv', 'wulff2018sampling/exp1.csv', 'xiong2023neural/exp1.csv', 'xu2021novelty/exp.csv', 'xu2023augmenting/../../../exp1.csv', 'zhu2024games', 'zorowitz2023data/exp1.csv'
]

psych201 = psych201.filter(
    lambda ex: ex["study"] not in exclude_studies,
    num_proc=8
)

psych201 = psych201.shuffle()

participant_counters = defaultdict(int)

def add_participant_index(example):
    exp = example["study"]
    if example["is_psych101"]:
        if example["is_psych101_test"]: 
            exp = 'test_' + exp
        else:
            exp = 'train_' + exp
    idx = participant_counters[exp]
    participant_counters[exp] += 1
    return {"participant_reindexed": str(idx)}

psych201 = psych201.map(add_participant_index, num_proc=1)
print(psych201)

exp_counts = Counter(psych201["study"])

max_eval_per_exp = {
    exp: min(int(np.floor(0.1 * n)), 100)
    for exp, n in exp_counts.items()
}

for i in max_eval_per_exp:
    print(i, max_eval_per_exp[i])

def mark_eval(example):
    if example["is_psych101"] and not example["is_psych101_test"]:
        return {"in_eval": False}
    
    exp = example["study"]
    idx = int(example["participant_reindexed"])
    return {"in_eval": idx < max_eval_per_exp[exp]}

def transform_example(ex):
    ex["text"] = remove_chevrons_except_single_upper(ex["text"])
    return ex

psych201 = psych201.map(mark_eval, num_proc=8)
print(psych201)

psych201eval = psych201.filter(lambda ex: ex["in_eval"], num_proc=8)
psych201eval = psych201eval.filter(lambda ex: '<<' in ex["text"], num_proc=8) # filter out two weird ones
print(psych201eval)

psych201train = psych201.filter(lambda ex: not ex["in_eval"], num_proc=8)
psych201train = psych201train.filter(lambda ex: '<<' in ex["text"], num_proc=8) # filter out two weird ones
print(psych201train)

#tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B-Base", use_fast=True)

#def tok_fn(ex):
#    return tokenizer(ex["text"], truncation=False)

#psych201discrete = psych201train.filter(lambda ex: ex["experiment"] in single_character_experiments, num_proc=8)
#psych201discrete = psych201discrete.map(tok_fn, batched=True, num_proc=8)
#psych201discrete = psych201discrete.filter(lambda ex: len(ex["input_ids"]) <= (8192 * 1), num_proc=8)
psych201discrete = psych201train.map(transform_example)
psych201discrete = psych201discrete.filter(lambda ex: int(ex["participant_reindexed"]) < (9999999 if ex["is_psych101"] else 15100), num_proc=8)
psych201discrete = psych201discrete.filter(lambda ex: '<<' in ex["text"], num_proc=8) # filter out two weird ones
print(psych201discrete)

discrete_counts = Counter(psych201discrete["experiment"])
for exp, n in sorted(discrete_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{exp}: {n}")

#psych201discreteeval = psych201eval.filter(lambda ex: ex["experiment"] in single_character_experiments, num_proc=8)
#psych201discrete = psych201discrete.map(tok_fn, batched=True, num_proc=8)
#psych201discrete = psych201discrete.filter(lambda ex: len(ex["input_ids"]) <= (8192 * 1), num_proc=8)
#psych201discreteeval = psych201discreteeval.filter(lambda ex: int(ex["participant_reindexed"]) < (9999999 if ex["is_psych101"] else 14735), num_proc=8)
psych201discreteeval = psych201eval.map(transform_example)
psych201discreteeval = psych201discreteeval.filter(lambda ex: '<<' in ex["text"], num_proc=8) # filter out two weird ones
print(psych201discreteeval)

discrete_counts = Counter(psych201discreteeval["experiment"])
for exp, n in sorted(discrete_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{exp}: {n}")


psych201train.push_to_hub("marcelbinz/Psych-201")

psych201eval.push_to_hub("marcelbinz/Psych-201-test")

psych201discrete.push_to_hub("marcelbinz/Psych-201-discrete")

psych201discreteeval.push_to_hub("marcelbinz/Psych-201-discrete-test")
