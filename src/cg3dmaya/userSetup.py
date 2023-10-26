import maya.cmds as cmds
import maya.utils


def guru_setup():
    try:    
        print("Guru: building Menu!")
        from cg3dguru.utils import menu_maker
        menu_maker.run(menu_namespace='cg3dmaya.menu')

        print("Guru: registering script jobs!")
        import cg3dmaya.scriptjobs
        cg3dmaya.scriptjobs.register_project_switch()
    except Exception as e:
        import traceback
        from pathlib import Path        
        import maya.cmds as cmds
        
        module_path = cmds.moduleInfo(path=True, moduleName='cg3dmaya')
        print("\n\n")
        print("--------------------------------------------------------")
        print(e)
        log = Path(module_path).parent.joinpath('cg3dmaya', 'scripts', 'error.log')
        callstack = traceback.format_exc()
        print(callstack)
        print("--------------------------------------------------------")
        print("\n\n")
        
        with open(log, 'w') as f:
            f.write(callstack)

maya.utils.executeDeferred(guru_setup)



