import sys  
from Robotic_Servos import *
import time
import pandas as pd

'''
This is the main class you can use for controling the gripper, for the up-to-date
version, there are just a few functions you can use, but you can self-customize
your own funcstions based on 'Robotic_Servo'.
'''

class PT_O():
    '''
    Important!!!!!!!!!!!!!!!!!!!!!
    Notice: Please calibarate the gripper before using this code
    '''

    def __init__(self, port_num, id):
        '''
        port_num: port on your PC that connect with the servo, you can check it from system's device manager
        id: servo's ID, you can check it from dymanixel wizard
        '''
        self.id = id
        self.port_num = port_num
        self.port = openport(port_num)
        self.packet = openpacket()
        self.servo = Robotis_Servo(self.port, self.packet, self.id)
        self.servo.init_multiturn_mode()

        file = pd.read_csv(r'.\calibaration.csv')
        df = pd.DataFrame(file)
        self.close_limit = int(df['close_limit'])
        self.open_limit = int(df['open_limit'])
        
        
    def close(self, speed = 100):
        # speed: moving speed, default: 100
        self.servo.multiturn_set_speed(speed)
        self.servo.goto(self.close_limit)
        print("Gripper is Successfully closed")

    def open(self, speed = 100):
        # speed: moving speed, default: 100
        self.servo.multiturn_set_speed(speed)
        self.servo.goto(self.open_limit)
        print("Gripper is Successfully opened")
      
    def moveto(self, pos, speed = 100):
        # speed: moving speed, default: 100
        self.servo.multiturn_set_speed(speed)
        if pos <= self.close_limit and pos>=self.open_limit:
            self.servo.goto(pos)
        else:
            print("Invalid input, The input pos must be within the working range")
            sys.exit(0)
            
    def stop(self):
        #stop the servo anytime
        self.servo.disable_torque()
        self.servo.enable_torque()
        
    
        

