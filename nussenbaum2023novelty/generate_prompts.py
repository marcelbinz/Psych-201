# git clone the exploration git of Nussenbaum into this folder to run this script
import jsonlines
from scipy.io import loadmat
import glob
import pandas as pd
import re
import sys
sys.path.append("..")
from utils import randomized_choice_options


# gather creatureNames and sceneNames for the corresponding blocks and subjects.
## gather memory task data
mem_task = glob.glob('exploration/data/raw_mat_files/memoryTask/*.mat')
mem_task_data = pd.DataFrame({'subID': [], 'blockID': [], 'sceneNames': [], 'creatureNames': []})

for file_path in mem_task:
    mat_data = loadmat(file_path)
    sub_id = file_path.split('/')[-1].split('_')[0]
    if 'probeAnalysis' not in mat_data.keys():
        continue
    else: 
        scene_names = mat_data['probeAnalysis']['sceneNames'][0][0][0]
        scene_names = [str(s[0]) for s in scene_names]
        creature_names = mat_data['probeAnalysis']['creatureNames'][0][0][0]
        creature_names = [str(n[0]) for n in creature_names]
        block_id = [i for i in range(1, 11)]
        temp_df = pd.DataFrame({'subID': [sub_id]*10, 'blockID': block_id, 'sceneNames': scene_names, 'creatureNames': creature_names})
        mem_task_data = pd.concat([mem_task_data, temp_df])

## gather exploration task data
explo_task = glob.glob('exploration/data/raw_mat_files/exploTask/*.mat')
explo_task_data = pd.DataFrame({'subID': [], 'blockID': [], 'sceneNames': [], 'creatureNames': []})

for file_path in explo_task:
    mat_data = loadmat(file_path)
    sub_id = file_path.split('/')[-1].split('_')[0]
    if 'probeStruct' not in mat_data.keys():
        continue
    else: 
        scene_names = mat_data['probeStruct']['sceneNames'][0][0][0]
        scene_names = [str(s[0]) for s in scene_names]
        creature_names = mat_data['probeStruct']['creatureNames'][0][0][0]
        creature_names = [str(n[0]) for n in creature_names]
        block_id = [i for i in range(1, 11)]
        temp_df = pd.DataFrame({'subID': [sub_id]*10, 'blockID': block_id, 'sceneNames': scene_names, 'creatureNames': creature_names})
        explo_task_data = pd.concat([explo_task_data, temp_df])

## generate dicts to replace image path with names
creatures_dict = {
    "creature_Angry_Owl.jpeg": "angry owl",
    "creature_Big_Foot.jpeg": "big foot",
    "creature_Centaur.jpeg": "centaur",
    "creature_Charmed_Rabbit.jpeg": "charmed rabbit",
    "creature_Dragon.jpeg": "dragon",
    "creature_Elf.jpeg": "elf",
    "creature_Enchanted_Deer.jpeg": "enchanted deer",
    "creature_Fairy.jpeg": "fairy",
    "creature_Gnome.jpeg": "gnome",
    "creature_Monster.jpeg": "monster",
    "creature_Talking_Bear.jpeg": "talking bear",
    "creature_Troll.jpeg": "troll",
    "creature_Unicorn.jpeg": "unicorn",
    "creature_Winged_Lion.jpeg": "winged lion",
    "creature_Witch.jpeg": "witch"
}

regions_dict = {
    "region_Blue_Mountain_Lake.jpg": "Blue Mountain Lake",
    "region_Coconut_Beach.jpg": "Coconut Beach",
    "region_Dusk_Forest.jpg": "Dusk Forest",
    "region_Green_Hill_Meadow.jpg": "Green Hill Meadow",
    "region_Hanging_Vine_Jungle.jpg": "Hanging Vine Jungle",
    "region_Mystery_Swamp.jpg": "Mystery Swamp",
    "region_Pine_Mountain_Forest.jpg": "Pine Mountain Forest",
    "region_Pink_Mountain_Valley.jpg": "Pink Mountain Valley",
    "region_Purple_Lake.jpg": "Purple Lake",
    "region_Redwood_Forest.jpg": "Redwood Forest",
    "region_Stone_Hill.jpg": "Stone Hill",
    "region_Sunrise_River.jpg": "Sunrise River",
    "region_Tall_Tree_Forest.jpg": "Tall Tree Forest",
    "region_Three_Peak_Mountain.jpg": "Three Peak Mountain",
    "region_Trim_Tree_Woods.jpg": "Trim Tree Woods"
}

stimuli_dict = {
    "": "",
    "1_antHill.jpeg": "an ant hill",
    "1_appleTree.jpeg": "an apple tree",
    "1_barn.jpeg": "a barn",
    "1_birdNest.jpeg": "a bird nest",
    "1_bridge.jpeg": "a bridge",
    "1_cabin.jpeg": "a cabin",
    "1_campfire.jpeg": "a campfire",
    "1_carrots.jpeg": "carrots",
    "1_cattail.jpeg": "a cattail",
    "1_cave.jpeg": "a cave",
    "1_cherryBlossom.jpeg": "a cherry blossom",
    "1_corn.jpeg": "corn",
    "1_fort.jpeg": "a fort",
    "1_hay.jpeg": "hay",
    "1_iris.jpeg": "an iris",
    "1_leaves.jpeg": "leaves",
    "1_log.jpeg": "a log",
    "1_mossRock.jpeg": "a moss rock",
    "1_mushroom.jpeg": "a mushroom",
    "1_pumpkinCluster.jpeg": "a pumpkin cluster",
    "1_rockPile.jpeg": "a rock pile",
    "1_treeDoor.jpeg": "a tree door",
    "1_vines.jpeg": "vines",
    "1_watermelon.jpeg": "a watermelon",
    "1_well.jpeg": "a well",
    "1_windmill.jpeg": "a windmill",
    "1_yellowTree.jpeg": "a yellow tree",
    "2_beets.jpeg": "beets",
    "2_birdHouse.jpeg": "a bird house",
    "2_blackberryBush.jpeg": "a blackberry bush",
    "2_bush.jpeg": "a bush",
    "2_christmasTree.jpeg": "a christmas tree",
    "2_clayHouse.jpeg": "a clay house",
    "2_crystal.jpeg": "a crystal",
    "2_flowerField.jpeg": "a flower field",
    "2_gingerbreadHouse.jpeg": "a gingerbread house",
    "2_gopherHole.jpeg": "a gopher hole",
    "2_grass.jpeg": "grass",
    "2_graves.jpeg": "graves",
    "2_greenTree.jpeg": "a green tree",
    "2_lilypad.jpeg": "a lilypad",
    "2_mushroomPile.jpeg": "a mushroom pile",
    "2_pearTree.jpeg": "a pear tree",
    "2_picnicBasket.jpeg": "a picnic basket",
    "2_picnicTable.jpeg": "a picnic table",
    "2_pinecones.jpeg": "pinecones",
    "2_pumpkin.jpeg": "a pumpkin",
    "2_purpleTree.jpeg": "a purple tree",
    "2_rock.jpeg": "a rock",
    "2_roses.jpeg": "roses",
    "2_stone.jpeg": "a stone",
    "2_thornyBeanstalk.jpeg": "a thorny beanstalk",
    "2_treehouse.jpeg": "a treehouse",
    "2_treeStump.jpeg": "a tree stump",
    "2_tulips.jpeg": "tulips"
}


#### create exploration dataset
choice_df = pd.read_csv('exploration/data/explo_choice_data.csv')[['subID', 'blockID', 'trialID', 'trialStimID_1', 'trialStimID_2', 'selectedStimID', 'rejectedStimID', 'reward', 'RT']]
stim_df = pd.read_csv('exploration/data/explo_stim_data.csv')

# Convert 'subID' to integer in both dataframes
explo_task_data['subID'] = explo_task_data['subID'].astype(int)
mem_task_data['subID'] = mem_task_data['subID'].astype(int)

exploration_df = pd.merge(choice_df, explo_task_data, on=['subID', 'blockID'])
exploration_df['selectedStimName'] = ""
exploration_df['rejectedStimName'] = ""
for index, row in exploration_df.iterrows():
    stim1 = stim_df.loc[(stim_df['subID'] == row['subID']) & (stim_df['stimNum'] == row['selectedStimID']), 'stimNames'].values
    stim2 = stim_df.loc[(stim_df['subID'] == row['subID']) & (stim_df['stimNum'] == row['trialStimID_1']), 'stimNames'].values
    stim3 = stim_df.loc[(stim_df['subID'] == row['subID']) & (stim_df['stimNum'] == row['trialStimID_2']), 'stimNames'].values

    if stim1.size != 1:
        continue
    else:
        exploration_df.loc[index, 'selectedStimName'] = stim1[0]
        exploration_df.loc[index, 'trialStimID_1Name'] = stim2[0]
        exploration_df.loc[index, 'trialStimID_2Name'] = stim3[0]

# replace the names with the names from the dictionary
exploration_df['selectedStimName'] = exploration_df['selectedStimName'].replace(stimuli_dict)
exploration_df['trialStimID_1Name'] = exploration_df['trialStimID_1Name'].replace(stimuli_dict)
exploration_df['trialStimID_2Name'] = exploration_df['trialStimID_2Name'].replace(stimuli_dict)

exploration_df['creatureNames'] = exploration_df['creatureNames'].replace(creatures_dict)
exploration_df['sceneNames'] = exploration_df['sceneNames'].replace(regions_dict)

mem_task_data['creatureNames'] = mem_task_data['creatureNames'].replace(creatures_dict)
mem_task_data['sceneNames'] = mem_task_data['sceneNames'].replace(regions_dict)

# remove the rows where the names were not found
exploration_df = exploration_df[exploration_df['selectedStimName'] != ""]

#### create memory dataset
mem_df = pd.read_csv('exploration/data/explo_mem_data.csv')

# replace all the image names with the corresponding names from the dictionary
mem_df['highRewImage'] = mem_df['highRewImage'].replace(stimuli_dict)
mem_df['lowRewImage'] = mem_df['lowRewImage'].replace(stimuli_dict)
mem_df['medRewImage'] = mem_df['medRewImage'].replace(stimuli_dict)
mem_df['highRewDiffImage'] = mem_df['highRewDiffImage'].replace(stimuli_dict)
mem_df['newImage'] = mem_df['newImage'].replace(stimuli_dict)

# replace imageOrder_1 - imageOrder_5 with the corresponding image name from columns highRewImage (1), lowRewImage (2), medRewImage (3), (4) highDiff, (5) newImage
mem_df['imageOrder_1_name'] = mem_df['imageOrder_1'].replace([1, 2, 3, 4, 5], [mem_df['highRewImage'], mem_df['lowRewImage'], mem_df['medRewImage'], mem_df['highRewDiffImage'], mem_df['newImage']])
mem_df['imageOrder_2_name'] = mem_df['imageOrder_2'].replace([1, 2, 3, 4, 5], [mem_df['highRewImage'], mem_df['lowRewImage'], mem_df['medRewImage'], mem_df['highRewDiffImage'], mem_df['newImage']])
mem_df['imageOrder_3_name'] = mem_df['imageOrder_3'].replace([1, 2, 3, 4, 5], [mem_df['highRewImage'], mem_df['lowRewImage'], mem_df['medRewImage'], mem_df['highRewDiffImage'], mem_df['newImage']])
mem_df['imageOrder_4_name'] = mem_df['imageOrder_4'].replace([1, 2, 3, 4, 5], [mem_df['highRewImage'], mem_df['lowRewImage'], mem_df['medRewImage'], mem_df['highRewDiffImage'], mem_df['newImage']])
mem_df['imageOrder_5_name'] = mem_df['imageOrder_5'].replace([1, 2, 3, 4, 5], [mem_df['highRewImage'], mem_df['lowRewImage'], mem_df['medRewImage'], mem_df['highRewDiffImage'], mem_df['newImage']])
mem_df['respKey_name'] = mem_df['respKey'].replace([1, 2, 3, 4, 5], [mem_df['imageOrder_1_name'], mem_df['imageOrder_2_name'], mem_df['imageOrder_3_name'], mem_df['imageOrder_4_name'], mem_df['imageOrder_5_name']])

# load the demographics dataset
demographics_df = pd.read_csv('exploration/data/explo_demographics.csv')

reward_dict = {'0': 'do not find a coin',
               '1': 'find one coin'
}

all_prompts = []

for sub_id in exploration_df['subID'].unique():
    exp_df = exploration_df[exploration_df['subID'] == sub_id]
    demo_df = demographics_df[demographics_df['subID'] == sub_id]
    mem_df = mem_df[mem_df['subID'] == sub_id]

    sex = demo_df.sex.values[0]
    age = demo_df.age.values[0]
    WASI_rawV = demo_df.WASI_rawV.values[0]
    WASI_rawMR = demo_df.WASI_rawMR.values[0]
    WASI_verbalT = demo_df.WASI_verbalT.values[0]
    WASI_mrT = demo_df.WASI_mrT.values[0]
    IQ = demo_df.IQ.values[0]
    nativeEnglish = demo_df.nativeEnglish.values[0]

    RTs = []

    explo_options = randomized_choice_options(num_choices=2)
    instructions_exploration = """Welcome to the Enchanted Kingdom
    Once upon a time, in a far corner of the world, an enormous earthquake separated the Enchanted Kingdom in half.
    In order to unite the kingdom, a large bridge needs to be built to connect the now separate land masses.
    The King and Queen need your help to raise money to help build the bridge.
    They have asked you to collect coins from regions around the kingdom until there is enough money to build a large bridge.
    Every region is owned by a magical creature, that has its own favorite spots to hide coins.
    Each creature hides their coins in 3 different hiding spots.
    You will see two hiding spots at a time and have to choose which hiding spot the creature likes best.
    Your goal is to collect as many magical coins as you can in order to build the bridge and unite the kingdom.
    Every round you will be shown 2 potential hiding spots and asked to pick one. Some spots will have lots of coins and others might have less.
    Hiding spots appear on the left or on the right totally at random. Position does not affect whether or not you will find more coins from a hiding spot.
    The background shows you what region you are in, with the creature that lives there located on the right corner.
    This will help remind you which region you are currently visiting.
    You can select the hiding spot on the left by pressing '"""+str(explo_options[0])+"""', or the hiding spot on the right by pressing '"""+str(explo_options[1])+"""'.
    Once you select a hiding spot, you will see if you have found a coin or not.
    Remember, each hiding spot has its own number of coins.
    You should try to figure out which hiding spots are the creature's favorite so you can collect the most coins.
    You can collect one coin at a time.
    It is important to remember that every creature has a hiding spot it likes most. Even if the hiding spots look the same in different regions, not every creature likes the same hiding spot.
    The gnome might love rocks and will hide more coins there, while the elf might prefer the pumpkin patch and hide more coins over there.
    Here is what you might expect in a hiding spot that looks the same in two different regions.
    - The badger doesn't like sunflowers so he hid a small amount of coins there (out of three rounds, only in round one a coin was found in the sunflowers.)
    - While the fox loves sunflowers so he hid many coins there. (out of three rounds a coin was found between the sunflowers in two rounds)
    At the end of the testing session you'll be awareded a bonus based on the number of coins you collect.
    You are ready to start!

    """

    prompt = instructions_exploration

    for block in range(1,11):
        block_data = exp_df[(exp_df['blockID'] == block)].iloc[0]
        if block_data.size != 0:
            block_data = block_data
            scene = block_data['sceneNames']
            creature = block_data['creatureNames']
            prompt += f"You have entered {scene}. This region is owned by the {creature}.\n"\

            for trial in range(1,16):
                trial_data = exp_df[(exp_df['blockID'] == block) & (exp_df['trialID'] == trial)] 
                if trial_data.size != 0:  
                    trial_data = trial_data.iloc[0]          
                    trial_stim1 = trial_data['trialStimID_1Name']
                    trial_stim2 = trial_data['trialStimID_2Name']
                    selected_stim = trial_data['selectedStimName']
                    key = 0 if selected_stim == trial_stim1 else 1
                    reward = trial_data['reward']
                    prompt += f"You see two hiding spots: On the left side {trial_stim1} ({explo_options[0]}) and on the right side {trial_stim2} ({explo_options[1]}).\n"\
                            f"Which hiding spot do you choose?\n"\
                            f"You select <<{explo_options[key]}>> and {reward_dict[str(int(reward))]}.\n"
                    
                    rt = trial_data['RT']

                    RTs.append(rt)
    prompt += "\n"

    if mem_df.size != 0 and mem_task_data[mem_task_data['subID'] == sub_id].size != 0: 

        instructions_memory = """Now that you've finished playing the game, we'd like to ask you a few questions about the different spots each creature used to hide their coins.
        For each creature you will be asked if you remember their favorite hiding spot.
        This is an example of what you will see at the start of each question.

        You see the magical fox in Blue Sky Woods and the following hiding spots:
        | a bird nest (M) | acrons (E) | an ant hill (X) | an apple tree (U) | a barn (T) |

        Your task will be to select the fox's favorite spot to hide coins by pressing the respective letter of the hiding spot. 
        You might see different hiding spots that the fox used to hide coins, but do your best to remember which hiding spot was the fox's favorite.
        For example, let's imagine the fox hid most of his coins behind the apple tree.
        To select the apple tree press 'U'.
        Please respond as accurately as you can.

        """
        prompt += instructions_memory
        for block in range(1,11): 
            mem_opts = randomized_choice_options(num_choices=5)
            mem_data = mem_df[mem_df['explorationBlock'] == block].iloc[0]
            mem_task = mem_task_data[(mem_task_data['subID'] == sub_id) & (mem_task_data['blockID'] == block)].iloc[0]
            prompt += f"You see the {mem_task['creatureNames']} in {mem_task['sceneNames']} and the following hiding spots:\n" \
                    f"| {mem_data['imageOrder_1_name']} ({mem_opts[0]}) | {mem_data['imageOrder_2_name']} ({mem_opts[1]}) | {mem_data['imageOrder_3_name']} ({mem_opts[2]}) | {mem_data['imageOrder_4_name']} ({mem_opts[3]}) | {mem_data['imageOrder_5_name']} ({mem_opts[4]}) |\n" \
                    f"Please select the favorite hiding spot of the {mem_task['creatureNames']}.\n\n" \
                    f"You select <<{mem_opts[mem_data['respKey']-1]}>>.\n\n"

    prompt = prompt[:-2]
    all_prompts.append({'text': prompt,
                        'experiment': 'nussenbaum2023novelty',
                        'participant': int(sub_id),
                        'RTs': RTs,
                        'age': round(float(age),2),
                        'sex': sex,
                        'WASI_rawV': str(WASI_rawV),
                        'WASI_rawMR': str(WASI_rawMR),
                        'WASI_verbalT': str(WASI_verbalT),
                        'WASI_mrT': str(WASI_mrT),
                        'IQ': str(IQ),
                        'nativeEnglish': bool(nativeEnglish)})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)