"""
Convert ascii fbx files to binary. Requires cg3dguru package

This module is intended to be called from mayapy.exe

example:
import cg3dguru.utils.drop_installer as di
mayapy, pip = di.Commandline.get_python_paths()

converter_script = %PATH to this file%
fbx_filename = %name of fbx file to convert%
save_filename = %optional new name of converted file%
try:
    di.Commandline.run_shell_command(f"{mayapy} {converter_script} {fbx_filename} {save_filename}", converter_script)
except Exception as e:
    print(e)

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
        mm.eval(f'FBXExportBakeComplexAnimation -v false')
        mm.eval(f'FBXExportBakeResampleAnimation -v false')
        mm.eval(f'FBXExportSkins -v true')
        mm.eval(f'FBXExportShapes -v true')
        mm.eval(f'FBXExportConstraints -v false')
        mm.eval(f'FBXExportInputConnections -v false')
        mm.eval(f'FBXExportCameras -v false')
        mm.eval(f'FBXExportLights -v false')
        mm.eval(f'FBXExportInAscii -v false')
        mm.eval(f'FBXExportAnimationOnly -v false')
        mm.eval(f'FBXExport -f "{filename}"')
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

    if len(sys.argv) == 2:
        this_file, fbx = sys.argv

    elif len(sys.argv) == 3:
        this_file, fbx, save_path = sys.argv

    else:
        issue = True

    if not issue:
        fbx = fbx.strip()
        save_path = save_path.strip()        
        fbx_ascii_to_binary(fbx, save_path)
    else:
        print(f"Wrong number of arguments. Expecte 2 or 3 got :{len(sys.arv)}")
    
    

    