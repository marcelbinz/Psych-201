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

psych201discrete = psych201train.map(transform_example)
psych201discrete = psych201discrete.filter(lambda ex: int(ex["participant_reindexed"]) < (9999999 if ex["is_psych101"] else 15100), num_proc=8)
psych201discrete = psych201discrete.filter(lambda ex: '<<' in ex["text"], num_proc=8) # filter out two weird ones
print(psych201discrete)

discrete_counts = Counter(psych201discrete["experiment"])
for exp, n in sorted(discrete_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{exp}: {n}")

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
