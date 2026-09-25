from pxr import Usd, Sdf, UsdGeom

layer = Sdf.Layer.Find('D:/CurrentProjects/Maya/DPA8600/RLucas_TestUSD/USD/main_stage.usda')

stage = Usd.Stage.Open(layer)

for prim in stage.TraverseAll():
    print(prim)
    
cube = stage.GetPrimAtPath('/cube')
cubeSchema = UsdGeom.Gprim(cube)

cubeSchemaOps = cubeSchema.GetOrderedXformOps() # This allows us to know the existing opinions on the xform

print(cubeSchemaOps[0].Get()) # Bro these all do the same thing and return the same thing

print(cube.GetAttribute(cubeSchemaOps[0].GetOpName()).Get()) # Here we can grab the attribute to run a get command on

print(cubeSchema.GetTranslateOp().Get()) # This works just as fine, but what if we don't know it exists

layer = Sdf.Layer.Find('D:/CurrentProjects/Maya/DPA8600/RLucas_TestUSD/USD/layout.usda')

stage2 = Usd.Stage.Open(layer)

for prim in stage2.TraverseAll():
    print(prim)
    
cube2 = stage2.GetPrimAtPath('/cube')
print(cube2 == cube) # Not the same thing

cube2Schema = UsdGeom.Gprim(cube2)
cube2SchemaOps = cube2Schema.GetOrderedXformOps()
print(cube2Schema.GetTranslateOp().Get()) # Pointers are the same when printed, but can't run Get() here
#cube2Schema.AddTranslateOp() # Need to add the translate opinion if it does not exist; will through error
cube2Schema.GetTranslateOp().Set(cubeSchema.GetTranslateOp().Get())
stage.RemovePrim('/cube')

