
import jsonlines
from glob import glob

files = glob('*/prompts*.jsonl')
print(files)
total_choices = 0
total_participants = 0
total_length = 0
total_experiments = 0
l_symb = '<<'
r_symb = '>>'


for file in files:
    print(file)
    total_experiments += 1
    with jsonlines.open(file) as reader:
        for obj in reader:
            total_participants += 1
            total_choices += obj['text'].count(l_symb)
            total_length += len(obj['text'])

print(total_participants)
print(total_choices)
print(total_length)
print(total_experiments)
print()
print(total_choices + 10681650)
print(total_participants + 60092)
