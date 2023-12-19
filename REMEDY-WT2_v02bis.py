# -*- coding: utf-8 -*-


########################################################### REMEDY - WAKING TASK 3 ##############################################################################

#----------------------- General info:

#   REMEDY Pre-sleep task 2 [session 1 & session 2]
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
import threading


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
    if int(sess) == 1:
        return categs[:3]
    if int(sess) == 2:
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


def get_categs2odors(part_id, categories=['Buildings', 'Children', 'Food', 'Mammals', 'Vehicles', 'Water'], odors=['A', 'B', 'C', 'D', 'E', 'F']):
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
    # This function takes a list of image names (block) and the dictionary that links all lists (values) to its category (key) as input.
    # Output: corresponding category.
    categ_map = {tuple(block): categ for categ in dic_blocks for block in dic_blocks[categ]}
    categ = categ_map[tuple(block)]
    return categ


def olf_reader():
    try:
        while True:
            try:
                data = ser.readline()
                msg = str(data, "utf-8").strip()

                # questo è un esempio della tipologia dei messaggi che puou ricevere
                if msg == "Lost connection":
                    break
                else:
                    if msg.find("ERROR") != -1:
                        print(msg)
                    elif msg.find("WARM") != -1:
                        print(msg)
                    else:
                        print(msg)

            except Exception as en:
                print(en)
                pass

    except Exception as e:
        print(e)
        print("Lost connection!")


def olf_write(msg):
    # if ser:
    #     return 0
    global ser  

    if not ser or not ser.isOpen():
        print("Serial port is not open.")
        return 0
    try:
        if isinstance(data, str):
            data = bytes(data, "utf-8")
        ser.write(data)
        return 1
    except Exception as e:
        print(e)
        return 0


def olf_init(myport='/dev/cu.usbmodem20220051', mybaudrate=9600): 
    # WINDOWS: verify port after connecting devide [Device Manager] / MacOS: change name
    # Output: object allowing olfactometer control     
    try:
        ser = serial.Serial(port=myport, baudrate=mybaudrate)

        if ser.isOpen():
            print("Opened Serial Port")
            thw = threading.Thread(None, target=olf_reader)
            thw.start()

        else:
            pass

    except serial.SerialException as se:
        print("Monitor: Disconnected (Serial exception)")
    except IOError:
        print("Monitor: Disconnected (I/O Error)")
    except ValueError as ve:
        print(ve)


##def present_odor(on=1, duration=0, olfactometer=0):
##    # Controller for odor presentation. May be used as a timer for presentation by specifying duration as input, else will work as a ON(1)/OFF(0) switch.
##    if olfactometer==0:
##        if duration != 0:
##            print('Odor presentation started.')  # square wave high (open - on)
##            time.sleep(duration)
##            print('Odor presentation stopped.')
##        else:
##            if on==1:
##                print('Odor presentation started.')                    
##            if on==0:
##                print('Odor presentation stopped.')
##    else:
##        if duration == 0:
##            olfactometer.setDTR(False)  # square wave high (open - on)
##            time.sleep(duration)
##            olfactometer.setDTR(True)
##        else:
##            if on==1:
##                olfactometer.setDTR(False)  # square wave high (open - on)
##            if on==0:
##                olfactometer.setDTR(True)  # square wave high (open - on)


def olf_enable(on=1):
        
    if on == 1:
        olf_write('C M;;;;;;;')
        olf_write('E 1')
        
    elif on == 0:
        olf_write('E 0')
        

def odor_switch(odor=0, duration=0):
# Controller for odor presentation. May be used as a timer for presentation by specifying duration as input, else will work as a ON switch.

    jar='S ' + str(odor)
    
    if duration != 0:
        olf_write(jar) # square wave high (open - on)
        time.sleep(duration)
        olf_write(jar)
    else:
        olf_write(jar)


def wait_kbd(okkeys=["space","escape"]):
    mykey = event.waitKeys(keyList=okkeys)
    if mykey == ["space"]:
        return
    elif mykey == ["escape"]:
        core.quit()
    else:
      return mykey


# Pause until a specified key is hit and save the hit key
def get_kbd(okkeys=None):
    while True:
        mykey = event.waitKeys(keyList=okkeys)
        print(mykey)
        if mykey == ["space"]:
           return
        elif mykey == ["escape"]:
            core.quit()
        else:
            return mykey

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


# Save subject kb input directly as integers
def str2num(resp):
    if len(resp[0]) == 1:
        return int(resp[0])
    if len(resp[0]) == 5:
        return int(resp[0][4])
    else:
        print("Response is not a number, cancelling test.")
        core.quit()


# Get subject metadata
def get_meta(lst):
    dlg = gui.Dlg(title='REMEDY-WakeTask2')
    dlg.addField("Participant ID:")
    dlg.addField("Session:", choices=['1', '2'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    part_id, sess = params

    try:
        snr = int(part_id)
    except ValueError:
        print("Participant ID is not a number, cancelling test.")
        core.quit()

    lst[0] = part_id  
    lst[1] = sess  

    return "REMEDY-WT2_P" + part_id + "_" + "S" + sess + "_" + time.strftime("%Y-%m-%d_%Hh%M") + ".csv"


def logfile_wt2(lst, odors, vals, aros, mems):
    for n in range(len(odors)):
        lst[2+n][0] = odors[n]
        lst[2+n][1] = vals[n]
        lst[2+n][2] = aros[n]
        lst[2+n][3] = mems[n]


#----------------------------- Initialize variables

# Initialize output dataframe
outputlog = [0, 0, [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

# Get metadata
outputname = get_meta(outputlog)
participant = outputlog[0]
session = outputlog[1]

# Get items for current participant/session
categs_current_id = get_categs_id(part_id=participant)
pairs_current_id = get_categs2odors(part_id=participant)
odors_current_id = [odor for cat, odor in pairs_current_id.items()]
odors_current_sess = get_categs_session(categs=odors_current_id, sess=session)

#----------------------------- Hardware parameters

olf_init()

# win = visual.Window(fullscr=True, color="grey", units="pix")    # May be edited for testing purposes -> restricts screen size (change to fullscr=True when exp)
win = visual.Window(fullscr=False, size=[1000,800], color="grey", units="pix")    # May be edited for testing purposes -> restricts screen size (change to fullscr=True when exp)

mymouse = event.Mouse()
mymouse.setVisible(0)

emo_keys = ['1','num_1','2','num_2','3','num_3','4','num_4','5','num_5','escape']

#----------------------------- Define stimuli

# List initialization
vals = [0]*len(odors_current_sess)
aros = [0]*len(odors_current_sess)
mems = [0]*len(odors_current_sess)

# Instructions
slide_instr = visual.ImageStim(win, image="instr1.png", units="pix", pos=(0,0))
slide_brk = visual.ImageStim(win, image="break.png", units="pix", pos=(0,0))
slide_end = visual.ImageStim(win, image="end.png", units="pix", pos=(0,0))

# Fixation cross
fixcross = visual.TextStim(win, text="+", units="norm", pos=(0,0.2), color="black") 

# Self-Assessment Manikin & ratings             
valtxt = visual.TextStim(win, text="Please rate the odor valence:", color="black", units="norm", pos=(0,0))    # Text to display for prompting input
valSAM = visual.ImageStim(win, image="valSAM.png", units="norm", pos=(0,-0.5))

arotxt = visual.TextStim(win, text="Please rate the odor arousal:", color="black", units="norm", pos=(0,-0.0))    # Text to display for prompting input
aroSAM = visual.ImageStim(win, image="aroSAM.png", units="norm", pos=(0,-0.5))

memtxt = visual.TextStim(win, text="If any, please explicit any personal memories that the odor reminded you of:", color="black", units="norm", pos=(0,0.5))    # Text to display for prompting input


# --------------------------  EXPERIMENT START  -------------------------- 

olf_enable(1) #TO BE TESTED WITH DEVICE

#--------------- Show instructions

show(slide_instr)
wait_kbd()

timer_task = core.Clock()                    # TESTING PURPOSES ONLY - Whole task timing

#--------------- Present stimuli 

# mydir = os.getcwd()

for n in range(len(odors_current_sess)):

    timer_odor = core.Clock()

    show(fixcross)
    sleep(1)

    slide_block = visual.TextStim(win, text=f"PRESS SPACE TO PRESENT ODOR {n+1}", units="norm", pos=(0,0.2), color="black")
    slide_odor = visual.TextStim(win, text=f"PRESENTING ODOR {n+1}", units="norm", pos=(0,0.2), color="red")

    show(slide_block)
    start_block = wait_kbd()
    if start_block is None:
        show(slide_odor)
        present_odor(duration=5)       # TESTING PURPOSES ONLY - Specify device=olfactometer
    sleep(0.1)

    # Valence rating
    valtxt.draw()
    valSAM.draw()
    win.flip()
    vals[n] = str2num(get_kbd(okkeys=emo_keys))

    # Arousal rating
    arotxt.draw()
    aroSAM.draw()
    win.flip()
    aros[n] = str2num(get_kbd(okkeys=emo_keys))

    # Open question
    show(memtxt)
    core.wait(2)
    #textboxxxxxx

    while round(timer_task.getTime(),2) < 3:
        core.wait()

logfile_wt2(outputlog, odors_current_sess, vals, aros, mems)
print('Time of completion of full task:', round(timer_task.getTime(),2), ' secs')                 # TESTING PURPOSES ONLY - Task timing

# --------------------------  EXPERIMENT END  -------------------------- 


# Export output data
save2csv(outputname, outputlog)

# Thanks, close window and quit
show(slide_end)
sleep(2)
win.close()
