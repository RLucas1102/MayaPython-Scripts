# Libraries for all USD stuff
from pxr import Usd, UsdGeom, UsdUtils, Sdf

# Libraries for working with paths and files
from pathlib import Path

# Libraries to used Maya commands
import maya.cmds as mc

project_folder = Path(mc.workspace(q=True, rd=True)) # Find project directory and convert to path

usd_file_name = "HelloWorld.usda"
usd_file_path = project_folder / "usd" / usd_file_name # Create usd file path

# TO-DO: Add option to not overwrite file and check if it exists; for testing, ignore this 

# Check if layer with identifier already exists
layer = Sdf.Layer.Find(usd_file_path.as_posix())
if layer:
    print("Opening old stage")
    stage = Usd.Stage.Open(layer) # Open stage if rootlayer already exists
    stage.GetRootLayer().Clear() # Restore layer to CreateNew state
else:
    print("Creating new stage")
    stage = Usd.Stage.CreateNew(usd_file_path.as_posix()) # Create new stage

# Defining an xform, sphere, and cube as separate generic prims
xform = stage.DefinePrim('/hello', 'Xform')
sphere = stage.DefinePrim('/hello/world', 'Sphere')
cube = stage.DefinePrim('/hello/world2', 'Cube')

# Resetting prim variables
xform = None
sphere = None
cube = None

# Finding prims again from stage
xform = stage.GetPrimAtPath('/hello')
sphere = stage.GetPrimAtPath('/hello/world')
cube = stage.GetPrimAtPath('/hello/world2')

# Listing property names for each prim
print(xform.GetPropertyNames())
print(sphere.GetPropertyNames())
print(cube.GetPropertyNames())

# Read extent attribute on sphere prim
# Extent is the axis-aligned object space boundaries of the object
extentAttr = sphere.GetAttribute('extent')
xformOpAttr = sphere.GetAttribute('xformOpOrder')
print(extentAttr.Get())
print(xformOpAttr.Get())
print(sphere.GetProperties()[1].Get())
print(sphere.GetAttributes())
print(sphere.GetRelationships())

# Increasing the sphere's radius by 2
radius = sphere.GetAttribute('radius')
radius.Set(2)
print(radius.Get())
print(extentAttr.Get())

# Set sphere's color
sphereSchema = UsdGeom.Gprim(sphere)
print(type(sphereSchema))
color = sphereSchema.GetDisplayColorAttr()
color.Set([(0,0,1)])

stage.GetRootLayer().Save() # Save out file

# Garbage Collection
del stage