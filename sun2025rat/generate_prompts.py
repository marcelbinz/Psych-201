import numpy as np
import pandas as pd
import jsonlines

dataset = [] #TODO EXPERIMENT 2
all_prompts = []

file_name = "RAT/RAT.csv"
df = pd.read_csv(file_name, sep='\t')

num_tasks = 15
start_prompt = '''In each of the following questions, you will see three stimulus words. Your task is to come up with a fourth word that is related to all three of them. This fourth word should be the best possible answer.
1. Your answer must be a complete word consisting of 2 to 3 Chinese characters. It cannot be part of a word, a number, or an English word.
2. The answer must be directly or specifically related to each of the three words. The connection can be semantic (related in meaning), antonymous (opposite in meaning), or part of a common phrase.
3. The answer cannot be a proper noun, such as a person’s name, place name, or title of a work.
'''

items_data = {
    1: ["眼泪", "蔬菜", "刺鼻"],
    2: ["救国", "函数", "丰满"],
    3: ["新闻", "负责", "战地"],
    4: ["黄金", "协调", "数字"],
    5: ["气球", "骄傲", "欲望"],
    6: ["眼睛", "效果", "冲击"],
    7: ["骏马", "高山", "危险"],
    8: ["甜的", "罐子", "炮弹"],
    9: ["有害", "二手", "压力"],
    10: ["植物", "年华", "女子"],
    11: ["正直", "测量", "塑料"],
    12: ["打仗", "象棋", "官职"],
    13: ["书籍", "习惯", "深度"],
    14: ["情侣", "鸭子", "棍棒"],
    15: ["山谷", "反射", "回信"]
}

for i, r in df.iterrows():
    prompt = start_prompt
    for task in items_data:
        stimulus_words = ', '.join(items_data[task])
        answer = r[f'answer_{task}']
        score = r[f'score_{task}']
        if pd.isna(answer) or answer is None:
            answer = ""
        prompt += f'\nStimulus words: {stimulus_words}. You enter <<{answer}>>. Score: {score}.'

    print(prompt)

    all_prompts.append({
        'text': prompt,
        'experiment': file_name,
        'participant': r['id'],
        'gender': r['gender'],
        'age': r['age'],
        'employment': r['employment'],
        'education': r['education'],
        'area of study': r['area of study']
    })

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)