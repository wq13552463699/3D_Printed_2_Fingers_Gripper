from Robotic_Servos import *
import time
import sys
import pandas as pd

print("--------------------------------------------------------------------")
print("README")
print("The is the calibration function, help you to calibarate the gripper")
print("for different device. Stongly reconmmend you calibarate the gripper")
print("every time you set up a new finger tip or device.\n")

print("Please read the calibrating file carefully in advance, otherwise the")
print("gripper may break your device.\n")

print("The calibration may take you around 3 mins")
print("Please check the Dynamixel ID and the output port number in advance")
print("If you are ready, please take your gripper on your hand, and plug in")
print("the cable(power and USB).\n")
print("--------------------------------------------------------------------")

input("Press 'Enter' for confirmation")

id = input("Please enter the ID of your Dynamixel and press 'Enter' for confirmation\
           , e.g. 3\nYour input:") 
id = int(id)

com = input("Please enter the com port number from your PC and press 'Enter' for confirmation,e.g. 5\nYour input:")
port_num = "COM%s" % com

print("\nInitilizing and activating your servo......")

port = openport(port_num)
packet = openpacket()
servo = Robotis_Servo(port, packet, id)
limits = {}
time.sleep(1)
print("Initilizing and activating finished, please follow the instruction to finish the rest\
      of the calibration\n")
print("--------------------------------------------------------------------")

print("\nPlease gentelly push the finger to your expected close position")
ref = input("Please enter 'yes'(lower case) and press 'Enter' for confirming the position\
            \nYour input:")
if ref == "yes":
    print("Don't move the finger, writing......")
    close_limit = servo.read_current_pos()
    time.sleep(1)
    limits['close_limit'] = int(close_limit)
else:
    print("Invalid input, existing")
    sys.exit(0)
    
print("The close limit is successfully stored\n")
print("Please gentelly pull the finger to your expected open position")
ref = input("please enter 'yes'(lower case) and press 'Enter' for confirming the position\
            \nYour input:")
ref = str(ref)
if ref == "yes":
    print("Don't move the finger, writing......")
    open_limit= servo.read_current_pos()
    time.sleep(1)
    limits['open_limit'] = int(open_limit)
else:
    print("Invalid input, existing")
    sys.exit(0)
print("The open limit is successfully stored\n")

df = pd.DataFrame([limits], columns=['close_limit', "open_limit"])
df.to_csv("./calibaration.csv", index=False)

print("\nThe calibration is successful, thanks for your cooration:)")
input("Press enter to exit")



