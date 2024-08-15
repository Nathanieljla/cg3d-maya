"""
This command allows mayapy to convert an ascii to binary
"""


def fbx_ascii_to_binary(filename, save_name=''):
    initialized = False
    try:
        import maya.standalone 			
        maya.standalone.initialize()
        initialized = True
    except:
        pass

    success = False
    try:
        from maya import cmds
        cmds.loadPlugin("fbxmaya")
        cmds.file(filename, prompt=False, i=True, importFrameRate=True, importTimeRange='override')

        if save_name:
            filename = save_name
            
        import maya.mel as mm
        mm.eval("FBXResetExport")
        mm.eval(f'FBXExportBakeComplexAnimation -v false') ##pymel.core.mel.FBXExportBakeComplexAnimation(v=False)
        mm.eval(f'FBXExportBakeResampleAnimation -v false') #pymel.core.mel.FBXExportBakeResampleAnimation(v=True)
        mm.eval(f'FBXExportSkins -v true') #pymel.core.mel.FBXExportSkins(v=True)
        mm.eval(f'FBXExportShapes -v true') #pymel.core.mel.FBXExportShapes(v=True)
        mm.eval(f'FBXExportConstraints -v false') #pymel.core.mel.FBXExportConstraints(v=False)
        mm.eval(f'FBXExportInputConnections -v false') #pymel.core.mel.FBXExportInputConnections(v=False)
        mm.eval(f'FBXExportCameras -v false') #pymel.core.mel.FBXExportCameras(v=False)
        mm.eval(f'FBXExportLights -v false') #pymel.core.mel.FBXExportLights(v=False)
        mm.eval(f'FBXExportInAscii -v false') #pymel.core.mel.FBXExportInAscii(v=False)
        mm.eval(f'FBXExportAnimationOnly -v false') #pymel.core.mel.FBXExportAnimationOnly(v=False)
        mm.eval(f'FBXExport -f "{filename}"') #pymel.core.mel.FBXExport(f=filename)

        success = True
    except Exception as e:
        print("crash")
        print(e)
        success = False
    finally:
        if initialized:
            try:
                maya.standalone.uninitialize()
            except:
                pass

    return success


#import cg3dguru.utils.drop_installer as di
#mayapy, pip = di.Commandline.get_python_paths()

#converter_script = r"C:/Users/natha/OneDrive/MATC/maya/modules/cg3dmaya/scripts/cg3dmaya/convert_fbx_file.py"
#fbx_test = r"E:/UnityProjects/doomer@doomer_stand_slam_ascii.fbx"
#save_test = r"E:/UnityProjects/doomer@doomer_stand_slam.fbx"
#try:
    #di.Commandline.run_shell_command(f"{mayapy} {converter_script} {fbx_test} {save_test}", converter_script)
#except Exception as e:
    #print(e)

if __name__ == '__main__':
    import sys
    this_file = ""
    fbx = ""
    save_path = ""
    issue = False
    
    with open(r"E:\UnityProjects\args.txt", 'a') as f:
        print(sys.argv, file=f)    
    
    if len(sys.argv) == 2:
        this_file, fbx = sys.argv

    elif len(sys.argv) == 3:
        print("3 args")
        this_file, fbx, save_path = sys.argv

    else:
        issue = True

    fbx = fbx.strip()
    save_path = save_path.strip()
    print(f"fbx source: {fbx} save: {save_path}")

    if not issue:
        fbx_ascii_to_binary(fbx, save_path)
    
    

    