'''
very simple code of instantiation
'''

from UCD_Hand import *

#%%
# Check the com port in your device manager
model = PT_O('COM5',2)
#%%
# Open the gripper with the speed of 50/1023
model.open(50)
#%%
# Close the gripper with the speed of 50/1023
model.close(50)
#%%
# Stop the gripper when it is moveing
model.stop()
#%%
# Open the gripper with default speed
model.open()
#%%

