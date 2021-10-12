UCD_hand python API version:2

This project can be applied to control the Dynamixel servo MX28 by python.
The communication protocal is Dynamixel SDK, link: https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/
Information and data about the Dynamixel MX28 are checked from Dynamixel e-mannual, link: https://emanual.robotis.com/docs/en/dxl/mx/mx-28/


Installation:
The installation of this project is simple, you can copy whole of this project folder to local. All required files are included in this folders,
so users don't have to configurate dynamixel sdk themselves. 
To install the dependency python libraries: pip install -r requirements.txt

Hardware Setup:
Coming soon...

Application:
For this version, we don't have the command to use the servo in the command line, you can use the API purely by python IDE.
1. Calibration:
	The purpose of calibaration is to find the position of the open limit and the close limit(two positions that tips can get)
		User can set their own working range by setting the above 2 limits. For calibration: open the project and run 
		"Calibaration.py" and follow the instruction to finish the process. After calibaration finishing, a "calibaration.csv"
		will be created in the working directory, please leave it there and don't remove it, because it will be used everytime
		in initilization.
	Notice: please strictly follow the instruction to do the calibration to avoid the damage of the gripper and your own device.
	
2. Application:
	For the current version of application, you can use the functions in the 'UCD_Hand.py' for the movement of the gripper.
	But if you want to check the status(current, voltage, torque) or change the configuration of the gripper, please go to
	"Robotic_Servos.py". Actually, 'UCD_Hand.py' and "Calibaration.py" are all built based on the "Robotic_Servos.py". So, if
	you want to don some advanced operations or do some customization, please go to "Robotic_Servos.py".
	
README version:1
