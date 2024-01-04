from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
from Phidget22.Devices.DigitalInput import *
import time
from datetime import datetime

def get_parameters(f):
    try:
        f.seek(0) #resets pointer to top of the file
        lines = f.readlines()
        return (lines[0].split()[1],#MaxSpeed
                lines[1].split()[1])#SomethingElse
    except:
        print('Error Reading Parameters: Edit parameters.txt or redownload it from https://github.com/wendl198/ContactlessProbe.')
        time.sleep(1)
        return get_parameters(f) #this will recursively tunnel deeper until the problem is fixed. It will not record data
    #May be smart to install a better fail safe, but this is probably good enough for most users.
def still_moving(pos,target,v):
    if v > 0: #moving down
        if target > pos:
            return True
        else:
            return False
    elif v < 0: #moving up
        if target < pos:
            return True
        else:
            return False

# stepper control parameters (DO NOT CHANGE)
StepsPerRev = 360/1.8*(204687/2057)*16 #200steps/rev*gear ratio*16microsteps #318,424.113
cmperRev = 5.735
onecm = StepsPerRev/cmperRev #this is the steps per 1 cm of motion (value is 55,522.949)
timeout = 5000 #for connecting to motor controller (ms)
# stepper control parameters (DO NOT CHANGE)

'''
README:

This is a template that is designed to be easily modified to set up a simple bridgman growth.
The procedure that this template has two moving steps and three unique posistions.

Posistions:
The first posistion is the same for every growth. One must define a origin on their sample
 and align it with the origin of the bridgman furnance, which is defined to the bottom of the alumia tube.
e.g. the Hg1201 growth uses the bottom of the quartz tube as an origin that is aligned with the bottom to begin. 
The next point is the waiting posistion. As the name implies, this is where the sample awaits the furnace to heat.
The final posistion is after the sample is fully lowered.

Moving Steps:
The first moving step moves from the origin to the waiting height quickly (at the speed set by StepperParameters.txt).
The second moving step moves from the waiting posistion to the final posistion at a speed determined by how far and how long you want to move


'''

# define speed and length for scan (CHANGE)
# Above the bottom of the furnace is positive
waiting_height = 2.39 # waiting height of the growth tube above the bottom of the aluminia tube
lower_distance = -30 # positive number lowers, neg raises
lower_time = 2 # time to lower growth in hrs
wait_time = 45 # hrs (waiting for furnace before lowering begins)
# define speed and length for scan (CHANGE)



# main travel info
height_final = waiting_height-lower_distance  #final height above bottom at the end (negative means below furnace)
v = -onecm*(height_final-waiting_height)/(3600*lower_time) #units of steps per sec 
# the sign of v matters!!
# up is negative values
# down is positive values
# this is opposite as of what is intuitive: steps is proportional to negative height



#file handling
parameter_path = 'StepperParameters.txt'
parameter_file = open(parameter_path, 'r')#this is where the first move's speed comes from

#example for saving posisiton & time data
# now = datetime.now()
# dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")#get unique name
# save_path = ''
# save_file = open('/home/blake/BridgemanFurnace/RawData/Stepper'+dt_string+'.dat', "a")#leave file open
# save_file.write("Time (min)" + "\t" + 'Position(1/16 steps)'+ '\t' + 'x (cm)' + "\n")#set header



#Create your Phidget channels
stepper0 = Stepper()
digitalInput1 = DigitalInput()
digitalInput2 = DigitalInput()
digitalInput3 = DigitalInput()
#Set addressing parameters to specify which channel to open (if any)
digitalInput1.setChannel(1)
digitalInput2.setChannel(2)
digitalInput3.setChannel(3)
#Open your Phidgets and wait for attachment
stepper0.openWaitForAttachment(timeout)
digitalInput1.openWaitForAttachment(timeout)
digitalInput2.openWaitForAttachment(timeout)
digitalInput3.openWaitForAttachment(timeout)



#start scan
stepper0.setControlMode(StepperControlMode.CONTROL_MODE_STEP)
stepper0.setCurrentLimit(2)#Amp
stepper0.setDataRate(100)#Hz
speed,_ = get_parameters(parameter_file) #this is the fast speed that the motor will move your sample to its waiting posistion
stepper0.setTargetPosition(0)
stepper0.setVelocityLimit(int(speed))
stepper0.setEngaged(True)
stepper0.addPositionOffset(-(pos :=stepper0.getPosition()))#sets current position to zero

print('Starting Initial posistion',pos)
target = -int((height_final-waiting_height)*onecm)
stepper0.setTargetPosition(target)
reset = True # I was having trouble with it skipping the whole movement loops on the very first iteration, so I added this reset. It is not that sexy, but it works great. With more effort, one could likely fix this easily

#start lifting to waiting height
#this will lift quickly and continuiously
while (still_moving((pos := stepper0.getPosition()),target,v) or reset) and not(digitalInput2.getState() and digitalInput3.getState()):
    if reset:
        reset = False
    print(str(round((pos)/int(waiting_height*onecm)*100,1))+'%')
    # Do other stuff here if wanted
    time.sleep(1)

stepper0.setEngaged(False)
print('Top posisiton',stepper0.getPosition()/onecm)
print('Waiting for heating')# wait for heating up
time.sleep(wait_time*3600)

# set up slow move
print('Beginning moving')
now = datetime.now()
print('Time is',now.strftime("%d/%m/%Y_%H:%M:%S"))
reset = True
target = -int((height_final-waiting_height)*onecm)
stepper0.setTargetPosition(stepper0.getPosition())
stepper0.setAcceleration(4000)# slowest acceleration
stepper0.setEngaged(True)
stepper0.setVelocityLimit(max(5,int(abs(v)+1))) # 5 gives a measured rate of 8/16 steps per sec
stepper0.addPositionOffset(-stepper0.getPosition()) 

# start moving                      
while (still_moving((pos := stepper0.getPosition()),target,v) or reset) and not(digitalInput2.getState() and digitalInput3.getState()):
    if reset:
        reset = False
        t0 = time.perf_counter()
    stepper0.setTargetPosition(int((time.perf_counter()-t0)*v))

    # do stuff here (provided is an example of saving the posistion and time data)
    # save_file.write(str((time.perf_counter()-t0)/60) + "\t" +  str(pos)+'\t' + str(waiting_height-pos/onecm)+"\n")
    # save_file.flush()#this will save the data without closing the file
    time.sleep(1)
    
stepper0.setEngaged(False)    
print('Done')
print('Traveled: ',str(stepper0.getPosition()/onecm)+'cm in',str((time.perf_counter()-t0)/3600)+'hours')
now = datetime.now()
print('Time is',now.strftime("%m/%d/%Y_%H:%M:%S"))

#Close your Phidgets and files once the program is done.
stepper0.close()
digitalInput1.close()
digitalInput2.close()
digitalInput3.close()
print('Stepper Closed')
parameter_file.close()
# save_file.close()
