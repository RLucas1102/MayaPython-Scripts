import maya.cmds as mc

size = 4

for i in range(size):
    for j in range(size):
        for k in range(size):
            
            mc.sphere()
            mc.move(i*2, j*2, k*2)
