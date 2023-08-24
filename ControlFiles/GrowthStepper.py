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
        
#Event handlers: These will be called every time the associated event occurs.

def onDigitalInput1_StateChange(self, state):
    #print("State [1]: " + str(state))
    pass

def onDigitalInput2_StateChange(self, state):
    #print("State [2]: " + str(state))
    if not(state):
        stepper0.setVelocityLimit(0)
    elif not(digitalInput3.getState()):
        speed,_ = get_parameters(parameter_file)
        stepper0.setVelocityLimit(int(speed))  

def onDigitalInput3_StateChange(self, state):
    #print("State [3]: " + str(state))
    if not(state):
        stepper0.setVelocityLimit(0)
    elif not(digitalInput2.getState()):
        speed,_ = get_parameters(parameter_file)
        stepper0.setVelocityLimit(-int(speed))

#stepper control parameters (do not change)
StepsPerRev = 360/1.8*(204687/2057)*16 #200steps/rev*gear ratio*16microsteps
#318,424.113
cmperRev = 5.735
onecm = StepsPerRev/cmperRev #this is the steps per 1 cm of motion (value is 55,522.949)
timeout = 5000 #for connecting to motor controller (ms)

#define speed and length for scan (change)
#assuming bottom of tube is at the bottom of the furnace
h0 = 18 #intial height above the bottom
h1 = 15.5 #final height above bottom (negative means out of furnace
v = onecm*(h1-h0)/(3600*90) #steps per sec
v =-2
#v = -10000
wait_time = 11#hr
wait_time = 5/3600#hr

parameter_path = 'C:\\Users\\Contactless\\Desktop\\Stepper\\StepperParameters.txt'
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
#Assign any event handlers you need before calling open so that no events are missed.
digitalInput1.setOnStateChangeHandler(onDigitalInput1_StateChange)
digitalInput2.setOnStateChangeHandler(onDigitalInput2_StateChange)
digitalInput3.setOnStateChangeHandler(onDigitalInput3_StateChange)

#Open your Phidgets and wait for attachment
stepper0.openWaitForAttachment(timeout)
digitalInput1.openWaitForAttachment(timeout)
digitalInput2.openWaitForAttachment(timeout)
digitalInput3.openWaitForAttachment(timeout)


#start scan
stepper0.setControlMode(StepperControlMode.CONTROL_MODE_RUN)
stepper0.setCurrentLimit(2)#Amp
stepper0.setDataRate(100)#Hz
speed,_ = get_parameters(parameter_file)
print('Starting Intial posisiton',stepper0.getPosition())
reset = True
offset = 0
stepper0.setVelocityLimit(int(speed))
stepper0.setEngaged(True)
stepper0.addPositionOffset(-stepper0.getPosition())#sets current position to zero
while False and (stepper0.getPosition()-offset)< abs(int(h0*onecm))or reset:
    if reset:
        offset = stepper0.getPosition()
        reset =False
        if offset != 0:
            print('Something Weird is still happening')
    print(str(round((stepper0.getPosition()-offset)/int(h0*onecm)*100,1))+'%')
    time.sleep(1)
stepper0.setEngaged(False)
print('Top posisiton',stepper0.getPosition()/onecm)
print('Waiting for heating')
#wait for heating up
time.sleep(wait_time*3600)
stepper0.setAcceleration(4000)
print('Beginning moving')
now = datetime.now()
print('Time is',now.strftime("%d/%m/%Y_%H:%M:%S"))
reset = True
offset = 0
#this gives a measured rate of 8/16 steps per sec
stepper0.setEngaged(True)
stepper0.setVelocityLimit(0)
stepper0.addPositionOffset(-stepper0.getPosition()-80) #
v_slow = -5
while (stepper0.getPosition() > int((h1-h0)*onecm) or reset) and not(digitalInput2.getState() and digitalInput3.getState()):
    print(stepper0.getPosition())
    
    if reset:
        #offset = stepper0.getPosition()
        #offset = 0 
        reset =False
        #if offset != 0:
            #print('Something Weird is still happening')
        t0 = time.perf_counter()
        #pold = 0

    desired_p = int((time.perf_counter()-t0)*v)
    stepper0.setVelocityLimit(v_slow)
    while abs(stepper0.getPosition())<abs(desired_p):
        
        time.sleep(.1)
    if stepper0.getPosition()!= desired_p:
        print('Not Moving')
        #v_slow -=1
    stepper0.setVelocityLimit(0)
    time.sleep(1)
    #p= stepper0.getPosition()
    #print(str(round(p/int((h1-h0)*onecm)*100,4))+'%')
    #print(stepper0.getPosition()/(time.perf_counter()-t0))
    
    #t2 = time.perf_counter()
    #print(p,(p-pold)/(t2-t),t2-t)
    #t = t2
    #pold = p
print('Done')
print('Traveled: ',str(stepper0.getPosition()/onecm)+'cm in',str((time.perf_counter-t0)/3600)+'hours')
now = datetime.now()
print('Time is',now.strftime("%d/%m/%Y_%H:%M:%S"))
stepper0.setEngaged(False)
#while not(digitalInput2.getState() and digitalInput3.getState()): #failsafe 
    #time.sleep(1)

#Close your Phidgets and files once the program is done.
stepper0.close()
digitalInput1.close()
digitalInput2.close()
digitalInput3.close()
print('Stepper Closed')
parameter_file.close()
