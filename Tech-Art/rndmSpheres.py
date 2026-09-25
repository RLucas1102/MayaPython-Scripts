import maya.cmds as mc
import numpy as np

numSpheres = 500

# For each potential sphere, generate a random position and test it with existing positions
# If an intersection exists, do not add the position to existingSpheres
existingSpheres = []
for i in range(numSpheres):
    intersected = False;
    pos = np.random.uniform(-12, 12, (1, 2))
    
    for j in range(len(existingSpheres)):
        if np.linalg.norm(pos - existingSpheres[j]) < 1:
            intersected = True;
                
    if not intersected:
        existingSpheres.append(pos)
        
# For every position in existingSpheres, create a sphere and move it to its absolute position
for pos in existingSpheres:
    mc.polySphere(radius = 0.5)
    
    mc.move(pos[0,0], 0.0, pos[0,1], absolute = True)


                
   