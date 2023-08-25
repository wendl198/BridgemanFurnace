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


#stepper control parameters (do not change)
StepsPerRev = 360/1.8*(204687/2057)*16 #200steps/rev*gear ratio*16microsteps #318,424.113
cmperRev = 5.735
onecm = StepsPerRev/cmperRev #this is the steps per 1 cm of motion (value is 55,522.949)
timeout = 5000 #for connecting to motor controller (ms)

#define speed and length for scan (change)
#assuming bottom of tube is at the bottom of the furnace
h0 = 0 #intial height above the bottom
h1 = h0-12 #final height above bottom (negative means out of furnace
v = onecm*(h1-h0)/(3600*60) #steps per sec
#up is negative values
#down is positive values
wait_time = 11#hr
# wait_time = 5/3600#hr

parameter_path = 'StepperParameters.txt'
parameter_file = open(parameter_path, 'r')

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
speed,_ = get_parameters(parameter_file)
stepper0.setTargetPosition(0)
stepper0.setVelocityLimit(int(speed))
stepper0.setEngaged(True)
stepper0.addPositionOffset(-(pos :=stepper0.getPosition()))#sets current position to zero
print('Starting Intial posisiton',pos)
target = -abs(int(h0*onecm))#want to move up so negative height
stepper0.setTargetPosition(target)
#start lifting to intial height
while (pos := stepper0.getPosition())> target:
    print(str(round((pos)/int(h0*onecm)*100,1))+'%')
    time.sleep(1)
    
stepper0.setEngaged(False)
print('Top posisiton',stepper0.getPosition()/onecm)
print('Waiting for heating')#wait for heating up
time.sleep(wait_time*3600)
stepper0.setAcceleration(4000)#slowest acceleration
print('Beginning moving')
now = datetime.now()
print('Time is',now.strftime("%d/%m/%Y_%H:%M:%S"))
reset = True
final_target = abs(int((h1-h0)*onecm)) #should be positive for lowering
stepper0.setTargetPosition(stepper0.getPosition())
stepper0.setEngaged(True)
stepper0.setVelocityLimit(max(5,int(abs(v)+1)))#this gives a measured rate of 8/16 steps per sec
stepper0.addPositionOffset(-stepper0.getPosition()) 
#start lowering from intial height                       
while ((pos := stepper0.getPosition()) < final_target or reset) and not(digitalInput2.getState() and digitalInput3.getState()):
    # print(pos)
    if reset:
        reset =False
        t0 = time.perf_counter()
    stepper0.setTargetPosition(target:=abs(int((time.perf_counter()-t0)*v)))#use absolute value to ensure positive thus down
    time.sleep(1)
    
stepper0.setEngaged(False)    
print('Done')
print('Traveled: ',str(stepper0.getPosition()/onecm)+'cm in',str((time.perf_counter()-t0)/3600)+'hours')
now = datetime.now()
print('Time is',now.strftime("%d/%m/%Y_%H:%M:%S"))

#Close your Phidgets and files once the program is done.
stepper0.close()
digitalInput1.close()
digitalInput2.close()
digitalInput3.close()
print('Stepper Closed')
parameter_file.close()
