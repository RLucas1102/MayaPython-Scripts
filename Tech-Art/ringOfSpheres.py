import maya.cmds as mc
import math as m

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

for i in range(1, 73):
    mc.polySphere(radius = .5)
    mc.move(0, 0, -10, relative = True) # Move sphere relative to its current position
    
    scaleP  = 'pSphere' + str(i) + '.scalePivot'
    rotateP = 'pSphere' + str(i) + '.rotatePivot'
    
    mc.move(0, 0, 0, scaleP, rotateP, absolute = True) # Moving pivot to 0,0,0; absolute flag ensures it moves to exact position
    
    mc.rotate(0, 5 * i, 0, relative = True, os = True) # Rotate sphere around new origin at (0,0,0) in object space
    
    # Set color of each sphere to its respective color on the color wheel when moving around the circle
    deg = i * 5
    
    redVal   = m.sin(m.radians(deg))
    greenVal = m.sin(m.radians(deg + 120))
    blueVal  = m.sin(m.radians(deg + 240))
    
    # Need to make each value in the 1, 0 range
    redVal   = reRange(redVal, 1, -1, 1, 0)    
    greenVal = reRange(greenVal, 1, -1, 1, 0)
    blueVal  = reRange(blueVal, 1, -1, 1, 0)
    
    mc.polyColorPerVertex(rgb=(redVal, greenVal, blueVal), cdo = True)
    
    # Expression to animate the spheres moving up and down in a wave pattern
    timeExp   = 'time + ' + str(i)
    objExp    = 'pSphere' + str(i)
    yTransExp = 'pSphere' + str(i) + '.translateY = sin(' + timeExp + ');'
    
    mc.expression(string = yTransExp, object = objExp, ae = True, uc = 'all')