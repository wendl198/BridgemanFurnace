# BridgemanFurnace
This is a repository that is made to be a manual for the home-built Bridgeman furnace. This was built by Sudarshan Sharma and Blake Wendland. Most of the materials and the orginal idea for the furnace were done by Zach Anderson.
For any questions, please email Blake at wendl198@umn.edu or blakewendland@gmail.com

The motion of this furnace is controlled by a 42BYGHW811 stepper motor [https://www.openimpulse.com/blog/products-page/product-category/42byghw811-stepper-motor-2-5-4-8-kg%E2%8B%85cm/]. The stepper motor is controlled via a PhidgetStepper 1063_1 controller[https://www.phidgets.com/?tier=3&prodid=60]. This controller can be easily controlled in many ways, but my prefered choice is to use the python API. Other choices can be veiwed here [https://www.phidgets.com/?view=code_samples&lang=Python]

Important values:
The gear ratio of the gear box attached to the motor is 204687/2057~99.51
The controller microsteps in 1/16 steps. The motor has 200 steps per rev (1.8 degree steps), so there are 3200 1/16 steps per revolution (This is the unit that the API uses by default).
Velocity units are in 1/16 steps per second by default with any integer value (1-32768) inclusive.
There are 318424.113 1/16 steps per rev.
The cm per rev was measured to be roughly 5.735 (not extremely precise. uncertainty is likely +-.07).

On Windows, this can be done easily by running a batch file that sets up a virtual enviroment to run the python script. Then this script can perform any required task. A few examples of this can be found in the ControlFiles folder. In my programs, any parameters can be changed during runtime via the StepperParameters.txt file, but this is often not required.

There are two buttons attached to the stepper controller board. The button closer to the wire is down the other is up. If you must kill a program that is running, you can either press both buttons at the same time. Alternatively, you can close all open programs and run the QuickStop program.

The temperature profile of the furance for the set point 1020C was measured 8/16/23 and can be found in the TempProfile folder. 

When running the stepper motor, there are two modes: step and run (toggled with stepper0.setControlMode(StepperControlMode.CONTROL_MODE_RUN) and stepper0.setControlMode(StepperControlMode.CONTROL_MODE_STEP). Run mode allows you to give a velocity that tell the motor the speed in which it should run (positive is up negative is down). Step mode is the default and allows you to set a terget position and the motor will automatically move there. I have had significant trouble with step mode not actually moving upon startup, so I highly recommend you use run mode. 
