import pymel.core as pm

defaults = pm.ls(defaultNodes=True)
print(defaults)
roots = pm.ls(assemblies=True)
for node in defaults:
    print(node)
