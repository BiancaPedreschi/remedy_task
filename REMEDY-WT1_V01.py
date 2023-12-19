# -*- coding: utf-8 -*-


########################################################### IMAGE RATING TASK ##############################################################################

#----------------------- General info:

#   Pilot study for TMR sleep study
#   Task: sample emotional ratings for pre-screened image set 
#   Goal: validate final selection of images for each category to be used in TMR / localizer task


#----------------------- Original design versions:

#   Lenovo ideapad330 x64
#   Processor Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz / 1800 Mhz / 4 Core(s) / 8 Logical Processor(s)
#   Microsoft Windows 10 Home - Version 10.0.19042 Build 19042
#   Python 3.6.5 (v3.6.5:f59c0932b4, Mar 28 2018, 16:07:46) [MSC v.1900 32 bit (Intel)] on win32
#       PsychoPy 3.0.4
#       Numpy 1.15.4

#----------------------- Edit log

# 04/06/21: script created [LS]
# 05/06/21: memPE task edited [LS]
# 07/06/21: img list reading integrated (obsolete) [LS]
# 09/06/21: v0.1 - getKbd() working [LS]
# 10/06/21: instructions slides created [LS]
# 11/06/21: v0.25 - categ selection with capital [LS]
#           v0.3 - all categs prototypicality rating [LS]
# 14/06/21: v0.35 - new instructions for categ/prototypicality [LS]
#           all imgs resized to 800*600 online with black padding [LS]
#           added 0 to categ ratings [LS]
# 15/06/21: v0.5 - added image quality ratings [LS]
#           added break every 100 images [LS]
#           added fixation cross before each new image [LS]
#           all imgs resized to 1000*750 with grey padding online (https://bulkresizephotos.com/en) [LS]
#           category 'HOUSES' renamed to 'BUILDINGS' - clearer [LS]
#           v0.55 - ready to share [LS]
#           added site selection in metadata [LS]
# 16/06/21: v0.6 - updated instructions [LS]
#           filepath internally created [LS]
#           added category 'ANIMALS (non-mammal)' [LS]
# 17/06/21: v0.65 - updated according to SS comments
#           'laterality' changed to 'handedness' in metadata
#           text added for arousal/valence rating
#           v0.7 - changed order of ratings (img qual before cats) [LS]
# 19/06/21: v0.75b - added rt timing "# TESTING PURPOSES ONLY - Image rating timing" [LS]
# 21/06/21: switching to Builder (needed for Pavlovia online run)
#           implementing new categorisation method - prompt n categs, if n>1, state ordered categs



################################################################################################################################################################


#----------------------- Import libraries

from psychopy import visual, core, event, gui, monitors
from statistics import mean             # TESTING PURPOSES ONLY - Image rating timing
import random, time, glob
import numpy as np
import csv
import os




#----------------------- Functions

# Write experience data to correct positions in list

def myLogfile(lst, myImgs, myVals, myAros):
     for n in range(len(myImgs)):
         lst[5 + n * 3 + 0] = myImgs[n]
         lst[5 + n * 3 + 1] = myVals[n]
         lst[5 + n * 3 + 2] = myAros[n]

# Pause until a specified key is hit
def waitKbd(okKeys=["space","escape"]):
    myKey = event.waitKeys(keyList=okKeys)
    if myKey == ["space"]:
        return
    elif myKey == ["escape"]:
        core.quit()
    else:
      return myKey


# Pause until a specified key is hit
def getKbd(okKeys=None):
    pressedKeys=[]
    while True:
        myKey = event.waitKeys(keyList=okKeys)
        print(myKey)
        if myKey == ["space"]:
           return pressedKeys
        elif myKey == ["escape"]:
            core.quit()
        else:
            pressedKeys.append(myKey)
            print(pressedKeys)


# Write outputLog to disk after test (csv format)
def saveToCsv(fileName, listVar):
    with open(fileName, 'w+') as csvDump:
        csvWriter = csv.writer(csvDump, quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(listVar)


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
def getMeta(lst):
    dlg = gui.Dlg(title='Image Rating Task')
    dlg.addField("Subject Number:")
    dlg.addField("Age:")
    dlg.addField("Gender:", choices=['Female', 'Male', 'Other'])
    dlg.addField("Handedness:", choices=['Right', 'Left'])
#    dlg.addField("Site:", choices=['IMT Lucca', 'Donders Institute'])
    dlg.addField("Ti piace sciare?:", choices=['si', 'no'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    snr, age, gen, hand, site = params

    try:
        subjectNb = int(snr)
    except ValueError:
        print("Subject Number is not a number, cancelling test.")
        core.quit()

    lst[0] = snr  
    lst[1] = age  
    lst[2] = gen  
    lst[3] = hand
    lst[4] = site
    
    folder_path = "/Users/foscagiannotti/Desktop/python_projects/space/REMEDY_TASK/ImageRating_Subs"
    
    file_name = "ImageRatingTask_Sb" + snr + "_" + time.strftime("%Y-%m-%d_%Hh%M") + ".csv"
    file_path = os.path.join(folder_path, file_name)

    return file_path

def main():
    # -------------------------- Experiment parameters -------------------------- 
 
    # Get image list
    imgList = []

    for file in glob.glob("/Users/foscagiannotti/Desktop/python_projects/space/REMEDY_TASK/DreamStudyImages_rs1000x750g/**/*.jpg"):
        imgList.append(file)

    random.shuffle(imgList)        

    imgList = imgList[:8]                           # May be edited for testing purposes -> restricts the image list to X random elements (change to [:] when exp)

    # Create output dataframe
    outputLog = [0] * (5 + len(imgList) * 3)        #  5 (metadata) + nb img * 3 (img name [str], valence [int], arousal [int])
    
    
    # Get metadata
    outputName = getMeta(outputLog)

    Mymonitor = monitors.Monitor('DELL SE2416H')
    Mymonitor.setSizePix((1440, 900)) 
    Mymonitor.setDistance(60)
    Mymonitor.setWidth(344)
    Mymonitor.setGamma(1.22)
    
    print("Prima di creare la finestra")
    win = visual.Window(
    monitor=Mymonitor,
    color="grey",
    units="pix",
    fullscr=True  
    )
    print("Dopo aver creato la finestra")
    #win = visual.Window(fullscr=True, color="grey", units="pix", monitor='Color LCD')    # May be edited for testing purposes -> restricts screen size (change to fullscr=True when exp)
    #win = visual.Window(fullscr=True, color="grey", units="pix", size=(1440, 900))
    #win = visual.Window(
    #fullscr=True,        # Schermo intero
    #monitor='DELL SE2416H',  # Sostituisci con il nome del tuo monitor esterno
    #color="grey",
    #units="pix"
    #size=(1440, 900))

    myMouse = event.Mouse(visible=True)
    #myMouse.setVisible(0)

    emoKeys = ['1','num_1','2','num_2','3','num_3','4','num_4','5','num_5','escape']
   

    # -------------------------- Create stimuli & initialise output lists -------------------------- 

    # Instructions
    instr = visual.ImageStim(win, image="instr1.png", units="pix", pos=(0,0))
    instrValSAM = visual.ImageStim(win, image="instr2.png", units="pix", pos=(0,0))
    instrAroSAM = visual.ImageStim(win, image="instr3.png", units="pix", pos=(0,0))
    

    slideBrk = visual.ImageStim(win, image="break.png", units="pix", pos=(0,0))
    slideEnd = visual.ImageStim(win, image="end.png", units="pix", pos=(0,0))


    # Fixation cross
    fixCross = visual.TextStim(win, text="+", units="norm", pos=(0,0.2), color="black") 


    # Self-Assessment Manikin & ratings             
    
    valSAM = visual.ImageStim(win, image="valSAM.png", units="norm", pos=(0,-0.8))

    aroSAM = visual.ImageStim(win, image="aroSAM.png", units="norm", pos=(0,-0.8))

    

    #Create lists to store subject's responses
    names = [0] * len(imgList)
    vals = [0] * len(imgList)
    aros = [0] * len(imgList)
  

    rt = [0] * len(imgList)          # TESTING PURPOSES ONLY - Image rating timing

    # --------------------------  INSTRUCTIONS  -------------------------- 

    show(instr)
    waitKbd()

    show(instrValSAM)
    waitKbd()

    show(instrAroSAM)
    waitKbd()


    # --------------------------  EXPERIMENT START  -------------------------- 

    counter = 0

    for n in range(len(imgList)):

        timer = core.Clock()                    # TESTING PURPOSES ONLY - Image rating timing

        show(fixCross)
        sleep(1)
        img = visual.ImageStim(win, image=imgList[n], units="norm", pos=(0,0.2))

        idx = imgList[n].find('x750g')          #  Strip path & keep only image name to save in output log (OK if folder name = 'DreamStudyImages_rs1000x750g')
        names[n] = imgList[n][idx+6:-4]

        # Valence rating
        print("Mostra immagine e stimolo di valenza")
        img.draw()
        valSAM.draw()
        win.flip()
        vals[n] = str2num(waitKbd(okKeys=emoKeys))

        # Arousal rating
        img.draw()
        aroSAM.draw()
        win.flip()
        aros[n] = str2num(waitKbd(okKeys=emoKeys))


      #  timing of imag rating
        rt[n] = round(timer.getTime() * 1000,2)         # TESTING PURPOSES ONLY - Image rating timing


        counter += 1

        if counter%5 == 0:                         # May be edited for testing purposes -> break every X images (change to %100 when exp)
            show(slideBrk)
            waitKbd()

    print('Rts:',rt)                                    # TESTING PURPOSES ONLY - Image rating timing
    print('Average image rt:', mean(rt),' ms')           # TESTING PURPOSES ONLY - Image rating timing
    print('Total image rt for', len(imgList),' images: ', round(sum(rt)/1000,2),' s')           # TESTING PURPOSES ONLY - Image rating timing

    myLogfile(outputLog, names, vals, aros)


    # --------------------------  EXPERIMENT END  -------------------------- 

    saveToCsv(outputName, outputLog)

    # Thanks, close window and quit
    show(slideEnd)
    sleep(5)

    win.close()

if __name__ == "__main__":
    main()
    core.quit()