import maya.cmds as mc
import maya.api.OpenMaya as om
import numpy as np

###################################################################
# FUNCTION DEFINTIONS
###################################################################

###############################################
# GetAABB(obj)
# Get AABB of a given object and its respective
# properties like size, largest dim, and center
# Return: List of AABB and properties
###############################################
def GetAABB(obj):
    
    # Get axis aligned BB of group, then find size, largest dimension, and center
    bbObj       = np.array(mc.exactWorldBoundingBox(obj))
    bbObjSize   = bbObj[3:] - bbObj[:3]  
    bbObjLgDim  = np.max(bbObjSize)
    bbObjCenter = np.array([[(bbObj[3] + bbObj[0]) / 2],
                            [(bbObj[4] + bbObj[1]) / 2],
                            [(bbObj[5] + bbObj[2]) / 2]])
                            
    bbList = [bbObj, bbObjSize, bbObjLgDim, bbObjCenter.flatten()]
    
    return bbList

###############################################

###############################################
# Rescale(refObj, target, mag)
# Rescales the target obj transform to match the 
# proportions of the refernce obj. Scale is
# multiplied by a provided magnitude
# Return: None
###############################################
def Rescale(refObj, target, mag):
    
    # Find the proportions between the refObj and target to scale target
    refBB    = GetAABB(refObj)
    targetBB = GetAABB(target)
    
    ratios = np.round(refBB[1] / targetBB[1])
    s = np.max(ratios) * mag     # Store max proportion
    mc.scale(s, s, s, target, os = True, r = True)

###############################################

###############################################
# lookAt(target, pos, transform)
# Creates a lookAt matrix based on a target
# and position. It only does a rotation
# The input maya transform is then rotated
# Return: None
###############################################
def lookAt(target, pos, transform):
    
    # Find forwad, right, and up vectors of world pos
    forward = (pos - target)
    forward = forward / np.linalg.norm(forward)
    right   = np.cross(np.array([0,1,0]), forward)
    right   = right / np.linalg.norm(right)
    up      = np.cross(forward, right)
    up      = up / np.linalg.norm(up)
    
    # Create lookat matrix
    lookAt  = (((right[0],   right[1],   right[2],   0),
                (up[0],      up[1],      up[2],      0),
                (forward[0], forward[1], forward[2], 0),
                (0,          0,          0,          1)))
               
    # Get current matrix of the object we want to rotate
    currMat = om.MMatrix(mc.getAttr(transform + '.worldMatrix'))
    
    # Set the object's transform matrix to the new transformed matrix
    mc.xform(transform, matrix = om.MMatrix(lookAt) * currMat, ws = True)
     
###############################################
     
###############################################
# CreateTurntable()
# Procedurally creates turntable from a
# cylinder object
# Return: List object with maya properties
#         and vertex data
###############################################
def CreateTurntable():
    
    # Create cylinder
    turntable = mc.polyCylinder(sz = 1)
    
    # Store vertices 
    mc.select(turntable)
    vertices = np.array(mc.ls(turntable[0] + '.vtx[*]', fl = True))
   
    # Move pivot to bottom middle center
    rotateP = turntable[0] + '.rotatePivot'
    scaleP  = turntable[0] + '.scalePivot'

    # Set bottom to 0,0,0
    bb = GetAABB(turntable[0])
    center = bb[3]
    displacement = center[1] - bb[0][1]
    mc.move(0, displacement, 0, turntable[0], r = True)
    
    # Scale turn table down from bottom middle
    pos = mc.pointPosition(vertices[-2]) # Bottom middle vertex world position
    mc.move(pos[0], pos[1], pos[2], rotateP, scaleP, a = True)
    mc.scale(1, 0.05, 1, os = True, r = True)
    
    # Freeze transforms
    mc.makeIdentity(a = True, n = True, pn = True, t = True, r = True, s = True)
    
    turntable.append(vertices)
    
    return turntable
    
    
###############################################

###############################################
# CreateSeamless()
# Procedurally creates seamless from a plane 
# object
# Return: List object with maya 
#         properties, vertex data, and edge 
#         data
###############################################
def CreateSeamless():
    
    # Create plane for seamless
    seamless = mc.polyPlane()

    # Store vertices and edges into np arrays
    mc.select(seamless)
    
    vertices = np.array(mc.ls(seamless[0] + '.vtx[*]', fl = True))
    edges    = np.array(mc.ls(seamless[0] + '.e[*]', fl = True))
    
    vertices = np.reshape(vertices, (11, 11)) # Reshape vertices to square matrix
    
    # Reformat edges into horizontal and vertical edges for easy selection
    # If the row is even, we check if i is even and add edges to h, else 
    # we add to v. If the row is odd, we check if i is odd and add edges
    # to h, else we add to v. If col = num of verts, we switch the parity 
    # of the row. If we have reached the last row in the plane,
    # we add all edges to h.
    h   = []
    v   = []
    row = 0
    col = 0
    switch = False
    numVerts = vertices.shape[0]
    for i in range(len(edges)):
        if row + 1 == numVerts:
            h.append(edges[i])
        elif switch:
            if col + 1 == numVerts:
                v.append(edges[i])
                col = 0
                row = row + 1
                switch = False
            else:
                if i % 2 == 1:
                    h.append(edges[i])
                else:
                    v.append(edges[i])
                    col = col + 1
        else:
            if col + 1 == numVerts:
                v.append(edges[i])
                col = 0
                row = row + 1
                switch = True
            else:
                if i % 2 == 0:
                    h.append(edges[i])
                else:
                    v.append(edges[i])
                    col = col + 1
                    
    # Create numpy matrix to represent h edges
    h = np.array(h)
    h = np.reshape(h, (11, 10))
    
    # Create numpy matrix to represent v edges
    v = np.array(v)
    v = np.reshape(v, (10, 11))
    
    # Get all vertices above and including the middle of the plane
    index = int(vertices.shape[0] / 2)
    
    selection = vertices[index:]
    
    mc.select(selection.flatten())

    # Rotate the vertices up 90 degrees to make back of seamless    
    mc.rotate(90, 0, 0, r = True, os = True)
    
    # Select and bevel the middle row of edges
    selection = h[int(h.shape[0]/2)]
  
    mc.polyBevel3(selection, fraction = 0.4, oaf = True, af = True, d = True, m = 0, mia = 0, c = True, sg = 6, ws = True, sa = 30.0, mv = True, mvt = 0.0001, ma = 180.0, at = 180.0 )
    
    # Add vertices and edges to seamless list
    seamless.append(vertices)
    seamless.append(h)
    seamless.append(v)
    
    return seamless

###############################################

###############################################
# Driver code
###############################################

# Take viewport selection
selection = mc.ls(selection=True)

if 0 < len(selection) < 2:
    
    # Get axis aligned BB of group, then find size, largest dimension, and center
    obj         = selection
    bbObjList   = GetAABB(obj)
    bbObj       = bbObjList[0]
    bbObjSize   = bbObjList[1]
    bbObjLgDim  = bbObjList[2]
    bbObjCenter = bbObjList[3]

    # Create seamless and get properties
    seamless     = CreateSeamless()
    vtxSeamless  = seamless[2]
    heSeamless   = seamless[3]
    veSeamless   = seamless[4] 
    scaleP       = seamless[0] + '.scalePivot'
    rotateP      = seamless[0] + '.rotatePivot'
    
    # Create turntable and get vertices
    #turntable    = CreateTurntable()
    #vtxTurntable = turntable[2]
    
    # Move seamless and turntable to the bottom middle of object
    pos = mc.pointPosition(vtxSeamless[2,5])  # Get position of center vertex
    mc.move(pos[0], pos[1], pos[2], scaleP, rotateP, absolute = True)
    mc.move(bbObjCenter[0], bbObj[1] - 0.001, bbObjCenter[2], seamless[0], absolute = True)
    #mc.move(bbObjCenter[0], bbObj[1] + 0.001, bbObjCenter[2], turntable[0], absolute = True)
        
    # Rescale seamless and turntable to match proportions of object
    Rescale(obj[0], seamless[0], 3)
    #Rescale(obj[0], turntable[0], 0.25)
    
    # Move obj to top of turntable
    # pos = mc.pointPosition(vtxTurntable[-1])
    # mc.move(pos[0], pos[1], pos[2], obj[0], a = True)
    
    # Create and move camera proportional to the largest dimension of the BB
    dCamera = mc.camera()
    mc.move(bbObjCenter[0], bbObjCenter[1], bbObjCenter[2], dCamera[0], a = True) # Reset camera to center of object
    mc.move(0, 0, (bbObjLgDim + 1) * 2, dCamera[0], r = True)
    mc.viewLookAt(dCamera[0], pos = (bbObjCenter[0], bbObjCenter[1], bbObjCenter[2])) # Make camera look at center of object
    
    # Create key light
    keyShape = mc.directionalLight(n = "keyLight")
    key = mc.listRelatives(keyShape, p = True) # Need to get the parent transform
    key.append(keyShape)
    mc.setAttr(key[1] + '.aiExposure', 3.0)
    
    scaleP  = key[0] + '.scalePivot'  # Need pivot points
    rotateP = key[0] + '.rotatePivot'
    
    # Move key light into position (45 degrees from the front and slightly up)
    mc.move(bbObjCenter[0], bbObj[4], bbObjCenter[2], key[0], a = True) # Reset keylight to top center of object
    mc.move(0, 0, (bbObjLgDim + 1) * 2, key[0], r = True)
    mc.move(bbObjCenter[0], bbObjCenter[1], bbObjCenter[2], scaleP, rotateP, a = True) # Reset pivot to center of object
    mc.rotate(0, 45, 0, key[0], os = True, r = True)
    
    # Make key light look at target object
    keyPos = np.array(mc.getAttr(key[0] + '.translate'))
    lookAt(bbObjCenter.flatten(), keyPos.flatten(), key[0])
    
    # Create fill light
    fill      = mc.createNode('transform', name='fillLight')
    fillShape = mc.createNode('aiAreaLight', name='fillLightShape', parent=fill)
    fill      = [fill, fillShape]
    
    # Need to illuminate by default
    mc.connectAttr(fill[0] + '.instObjGroups', 'defaultLightSet.dagSetMembers', na = True)
    mc.setAttr(fill[1] + '.exposure', 7.0)
    
    scaleP  = fill[0] + '.scalePivot'  # Need pivot points
    rotateP = fill[0] + '.rotatePivot'
    
    # Move fill light into position (-45 degrees from the front and slightly up)
    mc.move(bbObjCenter[0], bbObj[4], bbObjCenter[2], fill[0], a = True) # Reset fill light to top center of object
    mc.scale(8, 8, 8, fill[0], os = True, r = True)
    mc.move(0, 0, (bbObjLgDim + 1) * 2, fill[0], r = True)
    mc.move(bbObjCenter[0], bbObjCenter[1], bbObjCenter[2], scaleP, rotateP, a = True) # Reset pivot to center of object
    mc.rotate(0, -45, 0, fill[0], os = True, r = True)
    
    # Make fill light look at target object
    fillPos = np.array(mc.getAttr(fill[0] + '.translate'))
    lookAt(bbObjCenter.flatten(), fillPos.flatten(), fill[0])
    
    # Create back light
    back      = mc.createNode('transform', name='backLight')
    backShape = mc.createNode('aiAreaLight', name='backLightShape', parent=back)
    back      = [back, backShape]
    
    # Need to illuminate by default
    mc.connectAttr(back[0] + '.instObjGroups', 'defaultLightSet.dagSetMembers', na = True)
    mc.setAttr(back[1] + '.exposure', 6.5)
    
    scaleP  = back[0] + '.scalePivot'  # Need pivot points
    rotateP = back[0] + '.rotatePivot'
    
    # Move back light into position (push back from center and slightly up)
    mc.move(bbObjCenter[0], bbObj[4], bbObjCenter[2], back[0], a = True) # Reset back light to top center of object
    mc.scale(5, 5, 5, back[0], os = True, r = True)
    mc.move(0, 0, -bbObjLgDim, back[0], r = True)
    mc.move(bbObjCenter[0], bbObjCenter[1], bbObjCenter[2], scaleP, rotateP, a = True) # Reset pivot to center of object
    mc.rotate(0, 20, 0, back[0], os = True, r = True)
    
    # Make back light look at target object
    backPos = np.array(mc.getAttr(back[0] + '.translate'))
    lookAt(bbObjCenter.flatten(), backPos.flatten(), back[0])
    
    # Rotate object over time
    mc.expression(s = obj[0] + '.rotateY = time * 30', o = obj[0], ae = True, uc = 'all')
        
###############################################