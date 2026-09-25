import maya.cmds as mc
import numpy as np

#####################################################
# reRange:
# Takes an existing value and range, and finds where
# the value falls within a new range while still
# maintaining the original ratio
#####################################################

def reRange(oldValue, oldMax, oldMin, newMax, newMin):
    oldRange = (oldMax - oldMin)
    newRange = (newMax - newMin)
    newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
    return newValue

# Create positions for spheres
size = 2
vPos = np.array([[0, 0, 1],
                 [ .866, 0, -.5],
                 [-.866, 0, -.5]])
                
vPos = vPos * size

for i in range(72):
    
    # Set color of each sphere using i
    
    r1 = np.sin(np.radians(i * 5))
    g1 = np.sin(np.radians(i * 5 + 120))
    b1 = np.sin(np.radians(i * 5 + 240))
    
    r2 = np.sin(np.radians((i+10) * 5))
    g2 = np.sin(np.radians((i+10) * 5 + 120))
    b2 = np.sin(np.radians((i+10) * 5 + 240))
    
    r3 = np.sin(np.radians((i+20) * 5))
    g3 = np.sin(np.radians((i+20) * 5 + 120))
    b3 = np.sin(np.radians((i+20) * 5 + 240))
    
    colors = np.array([[r1, g1, b1], 
                       [r2, g2, b2], 
                       [r3, g3, b3]])
    
    # Need to make each value in the 1, 0 range
    
    colors = reRange(colors, 1, -1, 1, 0)
    
    # Create random radius and offsets
    rad1 = np.random.uniform(-.75, .75)
    rad2 = np.random.uniform(-.50, .50)
    rad3 = np.random.uniform(-.25, .25)
    
    radius  = np.array([1.0, .75, .5])
    offsets = np.array([rad1, rad2, rad3])
    
    # Generate three spheres in a triangle pattern
    spheres = []
    for j in range(vPos.shape[0]):
        s = mc.polySphere(r = offsets[j] + radius[j])[0]
        
        mc.move(vPos[j,0], vPos[j,1], vPos[j,2], absolute = True)
        
        mc.polyColorPerVertex(rgb=(colors[j,0], colors[j,1], colors[j,2]), cdo = True)
        
        spheres.append(s)
    
    # Group spheres and get pivots
    mc.select(spheres)
    groupA = mc.group(name = 'group_a_' + str(i))
    scaleP  = groupA + '.scalePivot'
    rotateP = groupA + '.rotatePivot'
    
    # Move pivot to center, rotate, and freeze transforms
    mc.move(0, 0, 0, scaleP, rotateP, absolute = True) # Moving pivot to 0,0,0; absolute flag ensures it moves to exact position
    mc.rotate(0, 45 * i, 0, relative = True, os = True)
    mc.makeIdentity(a = True, n = True, pn = True, t = True, r = True, s = True)
    
    # Move group to (10, 0, 0)
    mc.select(groupA)
    if i % 3 == 0:
        mc.move(7, 0, 0, relative = True)
    else:
        mc.move(10, 0, 0, relative = True)
    
    # Create new group and center pivot at center
    groupB = mc.group(name = 'group_b_' + str(i))
    scaleP  = groupB + '.scalePivot'
    rotateP = groupB + '.rotatePivot'
    mc.move(0, 0, 0, scaleP, rotateP, absolute = True) # Moving pivot to 0,0,0; absolute flag ensures it moves to exact position
    
    # Create expression for group_a to rotate around local center Y axis
    if i % 5 == 0:
        mc.expression(s = groupA + '.rotateY = time * 30;', o = groupA, ae = True, uc = 'all')
    else:
        mc.expression(s = groupA + '.rotateY = time * 10;', o = groupA, ae = True, uc = 'all')
    
    # Rotate groups in a circle to create helix based on index
    mc.select(groupB)
    mc.rotate(0, 0, 5 * i, relative = True, os = True)
    
    
    