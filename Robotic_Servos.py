#%%


from dynamixel_sdk import *
import time
import numpy as np
import math

'''
Original information:
Firmware version = 41
ID = ~
Baud Rate = 34 = 57600 bps
Return delay time = 250 = 500msec
CW angle limit = 0 = 0°
CWW angle limit = 4095 = 360°
'''



#%%

ADDR_MX_TORQUE_ENABLE      = 24             # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36
ADDR_MX_POS_LIMIT = 8
ADDR_MX_MOVING = 46
ADDR_MX_VOLTAGE = 42
ADDR_MX_LOAD = 40
ADDR_MX_SPEED = 38
ADDR_MX_MOVING_SPEED = 32
ADDR_MX_CW_LIMIT = 6
ADDR_MX_CCW_LIMIT = 8

BAUDRATE                   = 57600

PROTOCOL_VERSION = 1.0

# Port operating

def openport(PORT_NUM):
    # open the port for communication
    '''port : port number for connecting the usb on your PC, you can check it
        in the device manager.
    example: "COM5"'''
    
    port = PortHandler(PORT_NUM)
    if port.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
    if port.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate to %d" % BAUDRATE)
        return port
    else:
        print("Failed to change the baudrate")

def openpacket():
    # open the port for sending data
    packet = PacketHandler(PROTOCOL_VERSION)
    if packet:
        print("Succeeded to open the Packet")
        return packet
    else:
        print("Fail to open the Packet")

class Robotis_Servo():
    def __init__(self, port, packet, servo_id):
        '''
        Parameters
        ----------
        port: the instantiated object of port from the above openport
        packet : the instantiated object of packet from the above openpacket
        servo_id : servo's ID, you can check it from dynamixel wizard.
        '''
        
        self.return_delay = 250 * 2e-6
        self.servo_id = servo_id
        self.settings = {
            'home_encoder': 0x7FF,
            'max_encoder': 0xFFF,
            'rad_per_enc': math.radians(360.0) / 0xFFF,
            'max_ang': math.radians(180),
            'min_ang': math.radians(-180),
            'flipped': False,
            'max_speed': math.radians(100)
        }
        self.port = port
        self.packet = packet

    # The following function can be applied to check the status of the servo(s)
    def read_current_pos(self):
        dxl_present_position, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id, ADDR_MX_PRESENT_POSITION)
        if self.check_com(dxl_result, dxl_error):
            return dxl_present_position

    def read_goal_position(self):
        dxl_goal_position, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id,ADDR_MX_GOAL_POSITION)
        if self.check_com(dxl_result, dxl_error):
            return dxl_goal_position

    def is_moving(self):
        # check if the servo is moving
        dxl_is_moving, dxl_result, dxl_error = self.packet.read1ByteTxRx(self.port, self.servo_id,ADDR_MX_MOVING)
        if self.check_com(dxl_result, dxl_error):
            return dxl_is_moving

    def read_voltage(self):
        dxl_voltage, dxl_result, dxl_error = self.packet.read1ByteTxRx(self.port, self.servo_id, ADDR_MX_VOLTAGE)
        if self.check_com(dxl_result, dxl_error):
            return dxl_voltage/10.

    def read_load(self):
        dxl_load, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id, ADDR_MX_LOAD)
        if self.check_com(dxl_result, dxl_error):
            if dxl_load <=1023 and dxl_load != 0 :
                print("Load works to the CCW direction")
                return dxl_load
            elif dxl_load > 1024:
                print("Load works to the CW direction")
                return 1024 - dxl_load
            elif dxl_load == 0:
                print("No load works")
                return dxl_load

    def read_speed(self):
        dxl_speed, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id, ADDR_MX_SPEED)
        if self.check_com(dxl_result, dxl_error):
            if dxl_speed <=1023 and dxl_speed != 0 :
                print("Servo is running in the CCW direction")
                speed_rpm = dxl_speed * 0.11
                return speed_rpm
            elif dxl_speed > 1024:
                print("Servo is running in the CW direction")
                speed_rpm = (1024 - dxl_speed) * 0.11
                return speed_rpm
            elif dxl_speed == 0:
                print("Servo is not running")
                return dxl_speed

    # The following function can be applied for movement or change the parameters of movement
    def goto(self, position):
        # go to the position
        mode = self.check_move_mode()
        if mode=='wheel':
            print("goto function cannot be applied on wheel mode, please change to another mode")
        elif mode=='joint':
            cw_limit = self.check_cw_limit()
            ccw_limit = self.check_ccw_limit()
            if position>max(cw_limit,ccw_limit) or position<min(cw_limit,ccw_limit):
                print("The input position value is invalid, which is out of the range of cw and ccw angle limit")
            else:
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_GOAL_POSITION,position)
                self.check_com(dxl_result, dxl_error)
        elif mode=='multiturn':
            if position>28672 or position<-28672:
                print("The input position is invalid, which is out of range, valid range is -28672~28672")
            else:
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_GOAL_POSITION, position)
                self.check_com(dxl_result, dxl_error)

    def enable_torque(self):
        dxl_result, dxl_error = self.packet.write1ByteTxRx(self.port, self.servo_id, ADDR_MX_TORQUE_ENABLE,1)
        if self.check_com(dxl_result, dxl_error) == 0:
            print("Unable to enable torque")

    def disable_torque(self):
        dxl_result, dxl_error = self.packet.write1ByteTxRx(self.port, self.servo_id, ADDR_MX_TORQUE_ENABLE,0)
        if self.check_com(dxl_result, dxl_error) ==0:
            print("Unable to disable torque")

    def wheel_set_speed(self, direction, speed):
        mode = self.check_move_mode()
        if mode=="wheel":
            if speed<0 or speed>2047:
                print("Input speed is not valid, which is out of range. The valid range is [0,1023]")
            elif direction == "CW":
                speed += 1024
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_MOVING_SPEED, speed)
                self.check_com(dxl_result, dxl_error)
            elif direction == "CCW":
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_MOVING_SPEED, speed)
                self.check_com(dxl_result, dxl_error)
        else:
            print("Current moving mode is not wheel mode, please change the mode to wheel mode and then use this function")

    def joint_set_speed(self, speed):
        mode = self.check_move_mode()
        if mode=="joint":
            if speed<0 or speed>1023:
                print("Input speed is not valid, which is out of range. The valid range is [0,1023]")
            else:
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_MOVING_SPEED, speed)
                self.check_com(dxl_result, dxl_error)
        else:
            print("Current moving mode is not joint mode, please change the mode to wheel mode and then use this function")

    def multiturn_set_speed(self, speed):
        mode = self.check_move_mode()
        if mode=="multiturn":
            if speed<0 or speed>1023:
                print("Input speed is not valid, which is out of range. The valid range is [0,1023]")
            else:
                dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_MOVING_SPEED, speed)
                self.check_com(dxl_result, dxl_error)
        else:
            print("Current moving mode is not joint mode, please change the mode to wheel mode and then use this function")

    def set_torque(self,torque):
        if torque>1023 or torque<0:
            print("Invalid input torque value")
        else:
            dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_MOVING_SPEED, speed)
            self.check_com(dxl_result, dxl_error)


    # The following functions can be applied to Change the movement mode and working range
    def set_cw_limit(self,num):
        dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_CW_LIMIT, int(num))
        if self.check_com(dxl_result, dxl_error)==0:
            print("Fail to set CW limit to position %d" % int(num))

    def set_ccw_limit(self, num):
        dxl_result, dxl_error = self.packet.write2ByteTxRx(self.port, self.servo_id, ADDR_MX_CCW_LIMIT, int(num))
        if self.check_com(dxl_result, dxl_error)==0:
            print("Fail to set CW limit to position %d" % int(num))

    def init_joint_mode(self, cw_limit, cww_limit):
        self.set_cw_limit(cw_limit)
        self.set_ccw_limit(cww_limit)

    def init_wheel_mode(self):
        self.set_cw_limit(0)
        self.set_ccw_limit(0)

    def init_multiturn_mode(self):
        self.set_cw_limit(4095)
        self.set_ccw_limit(4095)

    def reset_move_mode(self):
        self.set_cw_limit(0)
        self.set_ccw_limit(4095)

    # The following functions can be applied to check the movement mode and working range
    def check_cw_limit(self):
        cw_limit, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id, ADDR_MX_CW_LIMIT)
        if self.check_com(dxl_result, dxl_error):
            return cw_limit

    def check_ccw_limit(self):
        ccw_limit, dxl_result, dxl_error = self.packet.read2ByteTxRx(self.port, self.servo_id, ADDR_MX_CCW_LIMIT)
        if self.check_com(dxl_result, dxl_error):
            return ccw_limit

    def check_move_mode(self):
        cw_limit = self.check_cw_limit()
        ccw_limit = self.check_ccw_limit()

        if cw_limit==0 and ccw_limit==0:
            return "wheel"

        if cw_limit>0 and cw_limit<4095 and ccw_limit>0 and ccw_limit<4095:
            return "joint"

        if cw_limit==4095 and ccw_limit==4095:
            return "multiturn"

    def check_com(self,result,error):
        if result != COMM_SUCCESS:
            print("%s" % self.packet.getTxRxResult(result))
            return 0
        elif error != 0:
            print("%s" % self.packet.getRxPacketError(error))
            return 0
        else:
            return 1

class TwoServo(Robotis_Servo):
    # 2 SERVOS work together, it will not be used recently
    def __init__(self,port,packet,id1,id2):
        self.port = port
        self.packet = packet
        self.id1 = id1
        self.id2 = id2

    def multigoto(self, ID1Pos, ID2Pos):
        groupSyncWrite = GroupSyncWrite(self.port, self.packet,ADDR_MX_GOAL_POSITION,4)

        param_id1pos = [DXL_LOBYTE(DXL_LOWORD(ID1Pos)),DXL_HIBYTE(DXL_LOWORD(ID1Pos)),DXL_LOBYTE(DXL_HIWORD(ID1Pos)),
                        DXL_HIBYTE(DXL_HIWORD(ID1Pos))]
        param_id2pos = [DXL_LOBYTE(DXL_LOWORD(ID2Pos)),DXL_HIBYTE(DXL_LOWORD(ID2Pos)),DXL_LOBYTE(DXL_HIWORD(ID2Pos)),
                        DXL_HIBYTE(DXL_HIWORD(ID2Pos))]

        dxl_addparam_result = groupSyncWrite.addParam(self.id1, param_id1pos)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % self.id1)
            quit()
        else:
            print("[ID:%03d] groupSyncWrite addparam successed" % self.id1)

        dxl_addparam_result = groupSyncWrite.addParam(self.id2, param_id2pos)
        if dxl_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % self.id1)
            quit()
        else:
            print("[ID:%03d] groupSyncWrite addparam successed" % self.id1)

        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packet.getTxRxResult(dxl_comm_result))

        groupSyncWrite.clearParam()


'''
The following code is not useful, please ignore
'''
# class Yale_Hand_T42():
#     # Some direct command for gripper.
#     def __init__(self):
#
#         self.port = openport()
#         self.packet = openpacket()
#         self.servo1 = Robotis_Servo(self.port, self.packet, 1)
#         self.servo2 = Robotis_Servo(self.port, self.packet, 2)
#         self.servo1.init_multiturn_mode()
#         self.servo2.init_multiturn_mode()
#         self.servo1.multiturn_set_speed(80)
#         self.servo2.multiturn_set_speed(80)
#
#     def hand_grasp(self):
#         self.servo1.goto(4400)
#         self.servo2.goto(2180)
#
#     def hand_release(self):
#         self.servo1.goto(3350)
#         self.servo2.goto(3230)


# class UCD_PT_O():
#     def __init__(self):

#         self.port = openport()
#         self.packet = openpacket()
#         self.servo1 = Robotis_Servo(self.port, self.packet, 1)
#         self.servo2 = Robotis_Servo(self.port, self.packet, 2)
#         self.servo1.init_multiturn_mode()
#         self.servo2.init_multiturn_mode()
#         self.servo1.multiturn_set_speed(80)
#         self.servo2.multiturn_set_speed(80)



# if __name__ == '__main__':
    # hand = Hand()
    # # hand.hand_grasp()
    # hand.hand_release()




#     port = openport()
#     packet = openpacket()
#     #
#     # servo1 = Robotis_Servo(port, packet, 1)
#     servo2 = Robotis_Servo(port, packet, 2)
#     #
#     # servo1.init_multiturn_mode()
#     servo2.init_multiturn_mode()
#     #
#     print(servo2.read_current_pos())
#     # servo1.multiturn_set_speed(80)
#     servo2.multiturn_set_speed(80)
#     # print(servo1.read_speed(),servo2.read_speed())
#
#     # servo2.disable_torque()
#
#     # servo1.goto(4400)
#     servo2.goto(166)
# # 166-2000
    # servo1.goto(3350)
    # servo2.goto(3230)

    # servo = TwoServo(port,packet,1,2)
    # # servo.multigoto(4400,2180)
    # servo.multigoto(3350, 3230)
    #
    # # servo1.init_multiturn_mode()
    # servo2.init_multiturn_mode()
    # servo1.goto(10000)
    # servo2.goto(10000)

    # port = servo.openPort("COM5")
    # packet = servo.openPacket()
    # pos = servo.set_cw_limit(200)
    # print(servo.check_cw_limit())
    # servo.init_multiturn_mode()
    # servo.goto(-2000)
    # servo.init_wheel_mode()
    # servo.wheel_set_speed('CCW', 200)
    # servo.joint_set_speed(200)
    # a = servo.check_move_mode()
    # print(a)
    # print(pos)
    # servo.kill_cont_turn()
    # bbb = MX28Status().GetCurrentPosition(aaa,1)
    # print(bbb)
    # aaa.closePort()





















    # def openPort(self, Port_num):
    #     portHandler = PortHandler(Port_num)
    #
    #     if portHandler.openPort():
    #         print("Succeeded to open the port")
    #     else:
    #         print("Failed to open the port")
    #
    #     if portHandler.setBaudRate(self.baudrate):
    #         print("Succeeded to change the baudrate to %d" % self.baudrate)
    #     else:
    #         print("Failed to change the baudrate")
    #
    #     return portHandler

    # def openPacket(self):
    #     self.protocal_version = PROTOCOL_VERSION
    #     packetHandler = PacketHandler(self.protocal_version)
    #     if packetHandler:
    #         print("Succeeded to open the Packet")
    #     else:
    #         print("Fail to open the Packet")
    #
    #     return packetHandler


        # speed_val = int(amnt*1023)
        # if speed_val < 0:
        #     speed_val = speed_val+1024
        # hi,lo = speed_val / 256, speed_val % 256
        # self.write_address(0x20,[lo,hi])
    #
    # def read_goal_position(self):
    #     data = self.read_address(0x1e, 2)
    #     enc_val = data[0] + data[1] * 256
    #     return enc_val





