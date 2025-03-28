""" Questions are reproduced from the Qualtrics file https://osf.io/cz9yh """
import pandas as pd
import random
import numpy as np
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

all_prompts = []
df = pd.read_csv("exp1.csv")
q = ['Q' + str(i) for i in range(1, 21)]
questions = {
    'Q1': {'text': 'Q1. Life imitates art. Which of the following, if true, most strongly supports the previous statement?',
           'answers': {'When Warren Beatty filmed Reds, he tried to suggest not only the chaos of the Russian Revolution but also its relationship to the present.': '',
            'The number of professional ballet companies has increased over the last five years, but the number of dance majors has decreased.': '',
            'On Tuesday, the business section of the newspaper had predicted the drop in interest rates that occurred on Friday.': '',
            'Truman Capote wrote In Cold Blood as a result of a series of brutal slayings by two crazed killers.': '',
            'Soon after the advent of color television, white shirts became less popular as dressy attire for men, and pastel-colored shirts began to sell well.': '',}
            },
    'Q2': {'text': 'Q2. On average, federal workers receive salaries 35.5 percent higher than private-sector salaries. For instance, federal workers in California average $19,206 a year, 25 percent higher than the average pay in the private sector, which is $15,365. This information would best support which of the following opinions?',
           'answers': {'Private-sector salaries in California are above average.': '',
           'The private sector is being paid fairly.': '',
           'Federal jobs are more secure than private-sector jobs.': '',
           'Public-sector work is more difficult than private-sector work.': '',
           'Federal pay is out of line.': '',},
            },
    'Q3': {'text': 'Q3. No high jumper entered the track meet unless he or she was a track club member. No track club member both entered the meet and was a high jumper. Which of the following conclusions can be correctly drawn from the two previous sentences?',
           'answers': {'No one but high jumpers entered the meet.': '',
           'Only track club members entered the meet.': '',
           'No track club members entered the meet.': '',
           'No high jumper entered the meet.': '',
           'Some track club members entered the meet.': '',},
            },
    'Q4': {'text': 'Q4. About 33% of American men between 25 and 50 are overweight. Research has shown that in most cases men between 25 and 50 who are overweight are more subject to heart disease than men who are not overweight. Which of the following is the most logical conclusion to this argument?',
           'answers': {'Therefore, 33% of the American men between 25 and 50 should lose weight.': '',
           'Therefore, if 33% of the American men between 25 and 50 were to lose weight, they would reduce their risk of heart disease.': '',
           'Therefore, if the men between 25 and 50 who are overweight were to lose weight, they would reduce their risk of heart disease by 33%.': '',
           'Therefore, if 33% of American men were to lose weight, they would reduce their risk of heart disease.': '',
           'Therefore, if the overweight men between 25 and 50 were to lose weight, their risk of heart disease would be reduced.': "",},
            },
    'Q5': {'text': "Q5. All computer geniuses are also brilliant mathematicians. Therefore, some computer geniuses don't require calculators for simple multiplication facts. Which of the following is the least necessary assumption for the previous conclusion to be logically correct?",
           'answers': {"Some brilliant mathematicians don't require calculators for simple multiplication facts.": "",
           "All brilliant mathematicians don't require calculators for simple multiplication facts.": "",
           "Some brilliant mathematicians require calculators for simple multiplication facts.": "",
           "All computer geniuses who require calculators for simple multiplication facts are brilliant mathematicians.": "",
           "Only computer geniuses are also brilliant mathematicians.": "",},
            },
    'Q6': {'text': 'Q6. A researcher has concluded that women are just as capable as men in math but that their skills are not developed because society expects them to develop other and more diverse abilities. Which of the following is a basic assumption of the researcher?',
           'answers': {'Ability in math is more important than ability in more diverse subjects.': '',
           'Ability in math is less important than ability in more diverse subjects.': '',
           'Women and men should be equally capable in math.': '',
           'Women might be more capable than men in math.': '',
           'Women tend to conform to social expectations.': '',},
            },
    'Q7': {'text': 'Q7. Jonathan Swift said, \"Laws are like cobwebs which may catch small flies but let wasps and hornets break through.\" Jonathan Swift would most likely believe that',
           'answers': {'prosecutors should be tough on criminals': '',
           'pesticides should be used to deter large insects': '',
           'small crimes should not be prosecuted': '',
           'the powerful can often avoid serious criminal sentences': '',
           'laws do not stop people from committing crimes': '',},
            },
    'Q8': {'text': "Q8. When Mom cooks, we all eat a delicious dinner. But Mom didn't cook today, so we won't be eating a delicious dinner. Which of the following is logically most similar to the previous argument?",
           'answers': {"When food is cooked, it always burns.  But our food isn't burned, so therefore it wasn't cooked.": '',
           'When silverware is used at the dining table, we usually have guests.  Today we have guests, so we are using the silverware.': '',
           "When the dog has fleas, he always scratches.  But the dog doesn't have fleas, so he won't be scratching.": '',
           'When a person is fortunate, he or she has great good luck.  So a fortunate person will always be lucky.': '',
           'When a university finishes admitting entering students, the freshman class is complete.  Since the freshman class is not complete, the university has not finished admitting entering students.': '',},
            },
    'Q9': {'text': 'Q9. Without sign ordinances, everyone with the price of a can of spray paint can suddenly decide to publicly create their own personal Picassos, and soon the entire town would start to look like something out of Alice in Wonderland. Therefore we need sign ordinances. All of the following are assumptions underlying the previous argument EXCEPT',
           'answers': {'spray paint can be used to create graffiti': '',
           'the town looking like Alice in Wonderland is undesirable': '',
           'sign ordinances are effective': '',
           'no other effective means of deterring graffiti presently exist': '',
           'sign ordinances are rarely, if ever effective': '',},
            },
    'Q10': {'text': 'Q10. When Louis Pasteur said, \"Chance favors the prepared mind,\" the famous French scientist most nearly meant',
            'answers': {"take a chance only if you're prepared": '',
            'pasteurization was a chance that Pasteur prepared for': '',
            'being prepared will be favorable to those who take chances': '',
            'happenstance will be more beneficial to those who are prepared': '',
            'we all have a chance to be prepared': '',},
            },
    'Q11': {'text': 'Q11. All acts have consequences. Given this fact, we may wish to play it safe by never doing anything. The speaker implies that',
            'answers': {'we may prefer to live safely': '',
            'all acts have consequences': '',
            'consequentiality is not safe': '',
            'doing nothing has lesser consequences': '',
            "not doing anything is not an act": '',},
            },
    'Q12': {'text': "Q12. Voltaire once said, \"Common sense is not so common.\" Which of the following most nearly parallels Voltaire's statement?",
            'answers': {'God must have loved the common man; he certainly made enough of them.': '',
            'The common good is not necessarily best for everyone.': '',
            'Jumbo shrimp may not actually be very big.': '',
            'Good people may not necessarily have good sense.': '',
            'Truth serum cannot contain the truth.': '',},
            },
    'Q13': {'text': 'Q13. It has been proven that the \"lie detector\" can be fooled. If one is truly aware that one is lying, when in fact one is, then the \"lie detector\" is worthless. The author of this argument implies that',
            'answers': {'the lie detector is a useless device': '',
            "a good liar can fool the device": '',
            'a lie detector is often inaccurate': '',
            'the lie detector is sometimes worthless': '',
            'no one can fool the lie detector all of the time': '',},
            },
    'Q14': {'text': 'Q14. It has been proven that the \"lie detector\" can be fooled. If one is truly aware that one is lying, when in fact one is, then the \"lie detector\" is worthless. This argument would be strengthened most by',
            'answers': {"demonstrating that one's awareness of truth or falsity is always undetectable": '',
            'citing evidence that there are other means of measuring truth which are consistently less reliable than the lie detector': '',
            'citing the number of cases in which the lie detector mistook falsehood for truth': '',
            'claiming that ordinary, unbiased people are the best \"lie detectors\"': '',
            'showing that the \"truth\" of any statement always relies on a subjective assessment': '',},
            },
    'Q15': {'text': 'Q15. It has been proven that the \"lie detector\" can be fooled. If one is truly aware that one is lying, when in fact one is, then the \"lie detector\" is worthless. Without contradicting his or her own statements, the author of the above statement might present which of the following arguments as a strong point in favor of the lie detector?',
            'answers': {'The methodology used by investigative critics of the lie detector is itself highly flawed.': '',
            'Circumstantial evidence might be more useful in a criminal case than is personal testimony.': '',
            'The very threat of a lie-detector test has led to a significant number of criminals to confess.': '',
            'People are never \"truly unaware\" that they are lying.': '',
            'Law-enforcement agencies have purchased too many detectors to abandon them now.': '',},
            },
    'Q16': {'text': 'Q16. English automobiles leak oil. All sportscars need some repair every month. Since the vehicle I recently purchased leaks oil and needs repair every month, I must have purchased an English sportscar. Which of the following, if true, would logically weaken the previous conclusion?',
            'answers': {'Only English sportscars need repair every month.': '',
            'Not all English sedans leak oil.': '',
            'Some sportscars need repair every two weeks.': '',
            'Danish automobiles also leak oil.': '',
            'American sportscars never need repair.': '',},
            },
    'Q17': {'text':"Q17. By appropriating bailout money for the depressed housing industry, Congress is opening the door to a flood of special relief programs for other recession-affected businesses. The author's attitude toward the Congress' action is probably",
            'answers': {'neutral': '',
            'disapproving': '',
            'confused': '',
            'happy': '',
            'irate': '',},
            },
    'Q18': {'text': 'Q18. We have been warned that if we stop watering our lawn, then not only will our grass die and our trees turn brown, but also the gophers will find the dry, hard soil a stimulus for ravaging whatever vegetation happens to survive. Therefore, we have decided to continue to water our lawn. All of the following can be reasonably inferred as goals of the author except',
            'answers': {'the grass is not dying': '',
            'the trees not turning brown': '',
            'the gophers not ravaging remaining vegetation': '',
            'the soil not becoming dry and hard': '',
            'water conservation': '',},
            },
    'Q19': {'text': "Q19. According to a recent study by the National Academy of Public Administration, postal patrons are regularly affronted by out-of-order stamp vending machines, branch post office lobbies locked at night, and twenty-nine cent letters that take as long to get there as thirteen-cent letters did a decade ago. Which of the following, if true, would weaken the implication of one of the author's observations?",
            'answers': {'Most out-of-order vending machines are located in run-down neighborhoods.': '',
            'Late-night vandalism has plagued post offices nationwide.': '',
            'Postage rates rose over a hundred percent from 1983 to 1993, but the cost of first class mail is still cheaper in the US than anywhere else.': '',
            'As a public corporation, the Postal Service has increased its capital assets by $3 billion.': '',
            'Ten years ago, most letters reached their destination within twenty-four hours.': '',},
            },
    'Q20': {'text': 'Q20. If I do not get at least a B on the final exam, I will definitely fail my geology course. From the previous statement, it most logically follows that if I do get a B on the final exam in geology, I then',
            'answers': {'may or may not pass the course': '',
            'will definitely pass the course': '',
            'will probably not pass the course': '',
            'will probably pass the course': '',
            'will definitely not pass the course': '',},
            },
}

for participant in df.participant.unique():
    print(participant)
    df_participant = df[(df['participant'] == participant)]
    buttons = list(randomized_choice_options(num_choices=5))
    questions_participant = questions
    for question in q:
        b = random.sample(buttons, len(buttons))
        questions_participant[question]['answers'] = {k: b.pop() for k in questions[question]['answers'].keys()}

    prompt = "You're about to answer a set of 20 questions about logical reasoning. How many of the 20 questions do you think you will answer correctly?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="absAssess0"].choice.item()}>>.\n'
    prompt += "Compared to other participants in this study, how well do you think you will do? Marking 90% means you will do better than 90% of participants, marking 10% means you will do better than only 10%, and marking 50% means that you will perform better than half of the participants.\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="relAssess0"].choice.item()}>>%.\n'
    prompt += "On a scale of 0 to 10, how difficult is solving logical reasoning problems for the average participant?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="diffOther0"].choice.item()}>>.\n'
    prompt += "On a scale of 0 to 10, how difficult is solving logical reasoning problems for you?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="diffSelf0"].choice.item()}>>.\n\n'

    prompt += 'You will be presented with brief passages or statements and will be required to evaluate their reasoning or determine what inferences you can logically draw from the passage.\n'

    prompt += f"Your task is to use the buttons {buttons[0]}, {buttons[1]}, {buttons[2]}, {buttons[3]}, and {buttons[4]} to select the best answer choice, even though more than one choice may present a possible answer.\n\n"

    for question in q:
        prompt += f"{questions_participant[question]['text']}\nThe choices are:\n"
        for key, value in questions_participant[question]['answers'].items():
            prompt += f'{value}: {key}\n'
        prompt += f"You press <<{questions_participant[question]['answers'][df_participant[df_participant['question']==question].choice.item()]}>>.\n\n"


    prompt += "How many of the 20 logical reasoning problems you just completed do you think you answered correctly?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="absAssess1"].choice.item()}>>.\n'
    prompt += "Compared to other participants in this study, how well do you think you performed? Marking 90% means you will do better than 90% of participants, marking 10% means you will do better than only 10%, and marking 50% means that you will perform better than half of the participants.\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="relAssess1"].choice.item()}>>%.\n'
    prompt += "On a scale of 0 to 10, how difficult was solving these logical reasoning problems for the average participant?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="diffOther1"].choice.item()}>>.\n'
    prompt += "On a scale of 0 to 10, how difficult was solving these logical reasoning problems for you?\n"
    prompt += f'You say <<{df_participant[df_participant["question"]=="diffSelf1"].choice.item()}>>.'
    all_prompts.append({'text': prompt, 'experiment': 'jansen2021logic/exp1.csv', 'participant': str(participant)})
    if participant == 0:
        print(prompt)

assert len(all_prompts) == df.participant.nunique(), f'The original dataset contains {df.participant.nunique()} experiments, but {len(all_prompts)} prompts have been generated.'

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
