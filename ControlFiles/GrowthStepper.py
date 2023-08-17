from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
from Phidget22.Devices.DigitalInput import *
import time

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

def onDigitalInput2_StateChange(self, state):#move up
    #print("State [2]: " + str(state))
    if not(state):
        stepper0.setEngaged(False)
        stepper0.addPositionOffset(-stepper0.getPosition())
    elif not(digitalInput3.getState()):
        stepper0.setTargetPosition(3000000)
        stepper0.setEngaged(True)
            
        

def onDigitalInput3_StateChange(self, state):#move down
    #print("State [3]: " + str(state))
    if not(state):
        stepper0.setEngaged(False)
        stepper0.addPositionOffset(-stepper0.getPosition())
    elif not(digitalInput2.getState()):
        stepper0.setTargetPosition(-3000000)
        stepper0.setEngaged(True)

#define speed and length for scan
StepsPerRev = 360/1.8*(204687/2057)*16 #200steps/rev*gear ratio*16microsteps
#318,424.113
cmperRev = 5.735
onecm = StepsPerRev/cmperRev #this is the steps per 1 cm of motion (value is 55,522.949)
l = 28 #desired movement length in cm
v = onecm*l/(3600*12) #steps per sec
timeout = 10000
wait_time = 50#hr

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

#wait for heating up
stepper0.setEngaged(False)
time.sleep(wait_time*60)

#start scan
stepper0.addPositionOffset(-stepper0.getPosition())#sets current position to zero
stepper0.setControlMode(StepperControlMode.CONTROL_MODE_RUN)
stepper0.setEngaged(True)
stepper0.setCurrentLimit(1)#Amp
stepper0.setDataRate(100)#Hz
print('Target Steps =',int(l*onecm))
stepper0.setVelocityLimit(v)

while stepper0.getPosition()< int(l*onecm) and not(digitalInput2.getState() and digitalInput3.getState()):
    time.sleep(1)
print('Done')
print('Traveled: ',stepper0.getPosition())

#end condition
while not(digitalInput2.getState() and digitalInput3.getState()):
    speed,_ = get_parameters(parameter_file)
    stepper0.setVelocityLimit(int(speed))
    
#Close your Phidgets and files once the program is done.
stepper0.close()
digitalInput1.close()
digitalInput2.close()
digitalInput3.close()
print('Stepper Closed')
parameter_file.close()
