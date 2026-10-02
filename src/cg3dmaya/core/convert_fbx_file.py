"""Convert an ASCII FBX file to binary from a Maya Python process.

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

import json


def _convert_fbx(filename, save_name):
    from maya import cmds

    cmds.loadPlugin("fbxmaya")
    cmds.file(
        filename,
        prompt=False,
        i=True,
        importFrameRate=True,
        importTimeRange="override",
    )

    if save_name:
        filename = save_name

    import maya.mel as mm

    mm.eval("FBXResetExport")
    mm.eval("FBXExportBakeComplexAnimation -v false")
    mm.eval("FBXExportBakeResampleAnimation -v false")
    mm.eval("FBXExportSkins -v true")
    mm.eval("FBXExportShapes -v true")
    mm.eval("FBXExportConstraints -v false")
    mm.eval("FBXExportInputConnections -v false")
    mm.eval("FBXExportCameras -v false")
    mm.eval("FBXExportLights -v false")
    mm.eval("FBXExportInAscii -v false")
    mm.eval("FBXExportAnimationOnly -v false")
    mm.eval("FBXExport -f {}".format(json.dumps(filename.replace("\\", "/"))))

def fbx_ascii_to_binary(filename, save_name=""):
    initialized = False
    try:
        import maya.standalone

        maya.standalone.initialize()
        initialized = True
    except RuntimeError:
        return False

    success = False
    try:
        _convert_fbx(filename, save_name)
        success = True
        
    except Exception as error:
        print("FBX conversion failed: {}".format(error))
        success = False

    finally:
        if initialized:
            try:
                maya.standalone.uninitialize()
            except RuntimeError:
                pass

    return success


if __name__ == "__main__":
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
        print("Wrong number of arguments. Expected 2 or 3; got {}".format(len(sys.argv)))
