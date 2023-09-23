import maya.cmds as cmds
import maya.utils

import cg3dmaya.scriptjobs

def guru_setup():
    print("Guru: building Menu!")
    from cg3dguru.utils import menu_maker
    menu_maker.run(menu_namespace='cg3dmaya.menu')

    print("Guru: registering script jobs!")
    import cg3dmaya.scriptjobs
    cg3dmaya.scriptjobs.register_project_switch()

maya.utils.executeDeferred(guru_setup)



