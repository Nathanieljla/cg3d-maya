import pymel.core as pm

#defaults = pm.ls(defaultNodes=True)
#print(defaults)
#roots = pm.ls(assemblies=True)
#for node in defaults:
    #print(node)
    
def link_joints():
    print('linking')
    selection = pm.ls(sl=True, type='joint')
    for j in selection:
        epic_joint = None
        try:
            epic_joint = pm.PyNode(f'epic:{j.name()}')
        except:
            continue
        
        print(epic_joint)
        delta = epic_joint.translate.get() - j.translate.get()
        add_node = pm.createNode('plusMinusAverage')
        j.translate >> add_node.input3D[0]
        add_node.input3D[1].set(delta)
        add_node.output3D >> epic_joint.translate
        j.rotate >> epic_joint.rotate



def Run():
    selection = pm.ls(sl=True)
    if len(selection) != 2:
        pm.warning("PLease select a joint and constraint")
        return
    
    joint = pm.ls(sl=True, type='joint')
    if len(joint) != 1:
        pm.warning("can't find joint in selection")
        return

    joint = joint[0]
    selection.pop(selection.index(joint))
    constraint = selection[0]
    target = pm.pointConstraint(constraint, q=True, targetList=True)[0]
    rig_root = pm.PyNode('Rig:root')
    rig_root.TopSimWeight.set(0.0)
    rig_root.BottomSimWeight.set(0.0)
    #pm.system.dgeval(constraint)
    p1 = joint.getTranslation(space='world')
    
    rig_root.TopSimWeight.set(1.0)
    rig_root.BottomSimWeight.set(1.0)
    pm.pointConstraint(constraint, e=True, offset=[0, 0, 0])
    #pm.system.dgeval(joint)
    p2 = joint.getTranslation(space='world')
    delta = list(p1 - p2)
    pm.pointConstraint(constraint, e=True, offset=delta)
    #pm.system.dgeval(joint)

    
    ##See where the joint sits when everything is at zero
    #pm.pointConstraint(target, constraint, e=True, weight=0.0)
    #pm.system.dgeval(joint)
    #p1 = joint.getTranslation(space='world')
    #pm.pointConstraint(target, constraint, e=True, weight=1.0)
    #pm.system.dgeval(joint)
    #p2 = joint.getTranslation(space='world')

    #delta = list(p2 - p1)
    #print(delta)
    #pm.pointConstraint(constraint, e=True, offset=delta)
    #pm.system.dgeval(joint)

Run()