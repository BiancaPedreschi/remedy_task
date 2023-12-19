# -*- coding: utf-8 -*-


########################################################### REMEDY - WAKING TASK 3 ##############################################################################

#----------------------- General info:

#   REMEDY Pre-sleep task 3 [session 1 & session 2]
#   Task: 
#   Goal: create association bteween odor-category pairs for cued image memorisation


#----------------------- Original design versions:

#   ASUS ExpertBook 
#   Processor Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz / 1800 Mhz / 4 Core(s) / 8 Logical Processor(s)
#   Microsoft Windows 10 Home - Version 10.0.19042 Build 19042
#   Python 3.6.5 (v3.6.5:f59c0932b4, Mar 28 2018, 16:07:46) [MSC v.1900 32 bit (Intel)] on win32
#       PsychoPy 3.0.4
#       Numpy 1.15.4

#----------------------- Import libraries/modules
import glob
import pickle
import random
import os
import time
import serial

from psychopy import visual, core, event, gui
from statistics import mean             # TESTING PURPOSES ONLY - Image rating timing
import random, time, glob
import numpy as np
import csv

#----------------------------- Define functions

def get_categs_id(part_id, categories=['Buildings', 'Children', 'Food', 'Mammals', 'Vehicles', 'Water']):
    # This function will either create or import the specific randomised category order for a given participant.
    # Input: participant ID
    # Ouput: list of randomised categories
    
    # Define the file where the variable containing the variable for the specific partitipant
    pkl_path = f'p{part_id}_categs.pkl'
    # Check if the file exists
    if os.path.exists(pkl_path):
        # If the file exists, load the variable
        with open(pkl_path, 'rb+') as f:
            pkl_data = pickle.load(f)
            if 'categories' not in pkl_data:
                # If the variable is not yet defined, shuffle the category list
                random.shuffle(categories)
                pkl_data['categories'] = categories
                # Store the variable to the file
                with open(pkl_name, 'wb') as f:
                    pickle.dump(pkl_data, f)
            else:
                # It he variable is already defined, load it
                categories = pkl_data['categories']
    else:
        # If the file does not exist, shuffle the variable
        random.shuffle(categories)
        
        # Store the variable to the file
        with open(pkl_path, 'wb') as f:
            pkl_data = {
            'categories': categories
            }
            pickle.dump(pkl_data, f)
    return categories


def get_categs_session(categs, sess):
    if sess == 1:
        return categs[:3]
    if sess == 2:
        return categs[3:]


def create_blocks(category, path=os.getcwd()):
    # Navigate to or define path as parent folder containing all category subfolders.
    # For a folder containing 33 valenced image files with a name starting with 'Pos'/'Neu'/'Neg', this function allows to split the images into 3 lists of 11 elements with balanced valences (min. 3 images/valence/list).
   
    # Input: category (should be a string among ['Buildings', 'Children', 'Food', 'Mammals', 'Vehicles', 'Water']); path should point to the mother directory containing the category subfolders containing the images.
    # Output: 3 lists with 11 items balanced across valences
         # items_block1 will have 4 positive, 4 negative and 3 neutral items
         # items_block2 will have 4 positive, 3 negative and 4 neutral items
         # items_block2 will have 3 positive, 4 negative and 4 neutral items

    filepath = os.path.join(path, category)
    os.chdir(filepath)

    # Import items of each valence into separate lists
    items_pos = [file for file in glob.glob('Pos*.jpg')]
    items_neg = [file for file in glob.glob('Neg*.jpg')]
    items_neu = [file for file in glob.glob('Neu*.jpg')]

    # Shuffle the items list to get a random order
    random.shuffle(items_pos)
    random.shuffle(items_neg)
    random.shuffle(items_neu)

    items_all = [items_pos, items_neg, items_neu]

    # Split the items into a new lists with sequentially ordered valenced items (pos-neg-neu-pos-neg-neu....)
    items_mixed = [item for sublist in zip(*items_all) for item in sublist]

    items_block1 = items_mixed[:11]
    items_block2 = items_mixed[11:22]
    items_block3 = items_mixed[22:]

    # Reshuffle the items list to get a random sequence
    random.shuffle(items_block1)
    random.shuffle(items_block2)
    random.shuffle(items_block3)

    os.chdir(path)

    return items_block1, items_block2, items_block3


def get_categs2odors(part_id, categories=['Buildings', 'Children', 'Food', 'Mammals', 'Vehicles', 'Water'], odors=['A', 'B', 'C', 'D', 'E', 'G']):
    # This function will either create or import the specific odor-category pairing for a given participant. 
    # Input: participant ID
    # Ouput: dictionary with category as key and associated odor as value

    # Define the file where the variable containing the randomised category order for the specific participant is stored
    pkl_name = f'p{part_id}_categs.pkl'
    # Check if the file exists
    if os.path.exists(pkl_name):
        # If the file exists, load the variable
        with open(pkl_name, 'rb+') as f:
            pkl_data = pickle.load(f)
            if 'pairs' not in pkl_data:
                # If the variable is not yet defined, shuffle the odor list
                random.shuffle(odors)
                # Create a list with tuples containing as 1st element a category and as 2nd element the paired odor
                pairs = list(zip(categories, odors))
                pkl_data['pairs'] = pairs
                # Store the variable to the file
                with open(pkl_name, 'wb') as f:
                    pickle.dump(pkl_data, f)
            else:
                # It he variable is already defined, load it
                pairs = pkl_data['pairs']
    else:
        # If the file does not exist, shuffle the odor list
        random.shuffle(odors)
        # Create a list with tuples containing as 1st element a category and as 2nd element the paired odor
        pairs = list(zip(categories, odors))
        # Store the variable to the file
        with open(pkl_name, 'wb') as f:
            pkl_data = {
            'pairs': pairs
            }
            pickle.dump(pkl_data, f)
    return dict(pairs)


def categ_current_block(block, dic_blocks={}):
    # This function takes a list of image names (block) as input and gives the corresponding category as an output.
    categ_map = {tuple(block): categ for categ in dic_blocks for block in dic_blocks[categ]}
    categ = categ_map[tuple(block)]
    return categ


def olfactometer_init(com_port="COM6",baudrate=9600):
    # WINDOWS: verify port after connecting devide [Device Manager] / MacOS: change name
    # Output: object allowing olfactometer control
    ser = serial.Serial(com_port, baudrate)
    ser.setDTR(True)    # square wave low (closed - off)
    return ser


def present_odor(ON=1, duration=0, olfactometer=0):
    # Controller for odor presentation. May be used as a timer for presentation by specifying duration as input, else will work as a ON(1)/OFF(0) switch.
    if olfactometer==0:
        if duration != 0:
            print('Odor presentation started.')  # square wave high (open - on)
            time.sleep(duration)
            print('Odor presentation stopped.')
        else:
            if ON==1:
                print('Odor presentation started.')
            if ON==0:
                print('Odor presentation stopped.')
    else:
        if duration == 0:
            olfactometer.setDTR(False)  # square wave high (open - on)
            time.sleep(duration)
            olfactometer.setDTR(True)
        else:
            if ON==1:
                olfactometer.setDTR(False)  # square wave high (open - on)
            if ON==0:
                olfactometer.setDTR(True)  # square wave high (open - on)

#-----------

def wait_kbd(okkeys=["space","escape"]):
    mykey = event.waitKeys(keyList=okkeys)
    if mykey == ["space"]:
        return
    elif mykey == ["escape"]:
        core.quit()
    else:
      return mykey


# # Pause until a specified key is hit and save the hit key
# def get_kbd(okkeys=None):
#     pressedkeys=[]
#     while True:
#         mykey = event.waitKeys(keyList=okkeys)
#         print(mykey)
#         if mykey == ["space"]:
#            return pressedkeys
#         elif mykey == ["escape"]:
#             core.quit()
#         else:
#             pressedkeys.append(mykey)
#             print(pressedkeys)


# Write outputLog to disk after test (csv format)
def save2csv(filename, myvars):
    with open(filename, 'w+') as csvdump:
        csvwriter = csv.writer(csvdump, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(myvars)


# Clearer if function
def show(stim):
    stim.draw()
    stim.win.flip()  # needed for two window setup - vs win.flip()


# Clearer if function
def sleep(secs):
    core.wait(secs / 1.0)        # May be edited for testing purposes -> allows to modify waiting periods (change to / 1.0 when exp)


# # Save subject kb input directly as integers
# def str2num(resp):
#     if len(resp[0]) == 1:
#         return int(resp[0])
#     if len(resp[0]) == 5:
#         return int(resp[0][4])
#     else:
#         print("Response is not a number, cancelling test.")
#         core.quit()


# Get subject metadata
def get_meta(lst):
    dlg = gui.Dlg(title='REMEDY-WakeTask3')
    dlg.addField("Participant ID:")
    dlg.addField("Session:", choices=['1', '2'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    snr, sess = params

    try:
        part_id = int(snr)
    except ValueError:
        print("Participant ID is not a number, cancelling test.")
        core.quit()

    lst[0] = part_id  
    lst[1] = sess  

    return "REMEDY-WT3_P" + snr + "_" + "S" + sess + "_" + time.strftime("%Y-%m-%d_%Hh%M") + ".csv"


def mylogfile(lst, imgs, timings, cat, odor):
    for n in range(len(imgs)):
        lst[2 + n * 5 + 0] = imgs[n]
        lst[2 + n * 5 + 1] = timings[n]
        lst[2 + n * 5 + 2] = cat[n]
        lst[2 + n * 5 + 3] = odor[n]



#----------------------------- Initialize variables

# Create output dataframe
outputlog = [0] * (2 + 11 * 9 * 4)        #  2 (metadata) + nb img * 4 (img name [str], presentation time [int], category [str], odor [str])

# Get metadata
outputname = get_meta(outputlog)
participant = outputlog[0]
session = int(outputlog[1])

# Assert sess for partiicpant has not been created..

categs_current_id = get_categs_id(part_id=participant)
pairs_current_id = get_categs2odors(part_id=participant)
categs_current_sess = get_categs_session(categs=categs_current_id, sess=session)


#----------------------------- Hardware parameters

# olfactometer = olfactometer_init() #TO BE TESTED WITH DEVICEù

# win = visual.Window(fullscr=True, color="grey", units="pix")    # May be edited for testing purposes -> restricts screen size (change to fullscr=True when exp)
win = visual.Window(fullscr=False, size=[1000,800], color="grey", units="pix")    # May be edited for testing purposes -> restricts screen size (change to fullscr=True when exp)

mymouse = event.Mouse()
mymouse.setVisible(0)


#----------------------------- Create random stimuli blocks, define fixed stimuli & initialise output lists

# Create a dictionary with the 3 categories to be used in the session as keys, each containing 3 lists/blocks of 11 images as values
blocks_current_sess = {}
for i in categs_current_sess:
    blocks_categ = create_blocks(i)
    blocks_current_sess[i] = blocks_categ

# Create a list containing all the blocks as sublists
all_blocks_img = []
for cat in blocks_current_sess:
    all_blocks_img += blocks_current_sess[cat]
# Shuffle the list
random.shuffle(all_blocks_img)

#Create a list with the corresponding category for each block
all_blocks_cat = []
for i in range(len(all_blocks_img)):
    for cat, img_list in blocks_current_sess.items():
        if all_blocks_img[i] in img_list:
            all_blocks_cat.append(cat)

#Create a list with the corresponding odor for each block
all_blocks_odor = []
for i in range(len(all_blocks_cat)):
    all_blocks_odor = [pairs_current_id[i] for i in all_blocks_cat]

# Instructions
slide_instr = visual.ImageStim(win, image="instr1.png", units="pix", pos=(0,0))
slide_brk = visual.ImageStim(win, image="break.png", units="pix", pos=(0,0))
slide_end = visual.ImageStim(win, image="end.png", units="pix", pos=(0,0))

# Fixation cross
fixcross = visual.TextStim(win, text="+", units="norm", pos=(0,0.2), color="black") 

#Create lists to store data log
log_imgnames = [[0] * len(all_blocks_img[0])] * len(all_blocks_img)
log_imgtimings = [[0] * len(all_blocks_img[0])] * len(all_blocks_img)
log_imgcats = [[0] * len(all_blocks_img[0])] * len(all_blocks_img)
log_imgodors = [[0] * len(all_blocks_img[0])] * len(all_blocks_img)



# --------------------------  EXPERIMENT START  -------------------------- 

#--------------- Show instructions

show(slide_instr)
wait_kbd()

timer_task = core.Clock()                    # TESTING PURPOSES ONLY - Whole task timing

#--------------- Present stimuli blocks

mydir = os.getcwd()

for nblock in range(len(all_blocks_img)):

    # Navigate to category subfolder
    filepath = os.path.join(mydir, all_blocks_cat[nblock])
    os.chdir(filepath)

    slide_block = visual.TextStim(win, text=f"BLOCK {nblock+1}", units="norm", pos=(0,0.2), color="black") 
    show(slide_block)
    start_block = wait_kbd()
    if start_block is None:
        present_odor(1)                     # TESTING PURPOSES ONLY - Specify device=olfactometer
    sleep(0.1)

    counter = 0

    for nimg in range(len(all_blocks_img[nblock])):

        timer_img = core.Clock()

        imgname = all_blocks_img[nblock][nimg]
        show(fixcross)
        sleep(1)
        img = visual.ImageStim(win, image=imgname, units="norm", pos=(0,0.2))
        show(img)
        wait_kbd()

        log_imgnames[nblock][nimg] = imgname
        log_imgtimings[nblock][nimg] = round(timer_img.getTime() * 1000, 2)
        log_imgcats[nblock][nimg] = all_blocks_img[nblock]
        log_imgodors[nblock][nimg] = all_blocks_odor[nblock]
    
        counter += 1

        if counter > 1:                                                         # TESTING PURPOSES ONLY - Limits block to X images
            break

    present_odor(0)                                                             # TESTING PURPOSES ONLY - Specify device=olfactometer
     

show(slide_end)
mylogfile(outputlog, log_imgnames, log_imgtimings, log_imgcats, log_imgodors)

print('Time of completion of full task:', round(timer_task.getTime(),2), ' secs')                 # TESTING PURPOSES ONLY - Task timing
for i in range(len(log_imgtimings)):
    print('Average image rt for block ', i+1, ':', mean(log_imgtimings[i]),' msecs')                # TESTING PURPOSES ONLY - Avg image timing

# --------------------------  EXPERIMENT END  -------------------------- 


# Export output data
os.chdir(mydir)
save2csv(outputname, outputlog)

# Thanks, close window and quit
show(slide_end)
sleep(2)
win.close()