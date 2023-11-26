
import pathlib

import pymel.core as pm
import maya.OpenMaya as om


import cg3dguru.utils
import cg3dmaya.preferences


###----------------------------------------
#project switching logic
###----------------------------------------

def _check_project(ask, target_path=None):
    project_path = pm.mel.eval('workspace -q -rd')
    
    if target_path:
        current_path = pathlib.Path(target_path)
    else:
        current_path = pm.system.sceneName()

    #startswith doesn't work for WindowsPath, but works for Path
    #so convert to a string
    if str(current_path).startswith(project_path):
        return

    workspace_path = None
    #samepath is what I want to use, but WindowsPath doesn't know it
    #so I'm trying samefile
    while not current_path.samefile(current_path.parent):
        current_path = current_path.parent
        if current_path.joinpath('workspace.mel').exists():
            workspace_path = current_path.joinpath('workspace.mel')
            break
        
    if workspace_path is not None:
        result = 'Yes'
        if ask:
            result = pm.confirmDialog(title='3D CG Guru', message='Switch Projects?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')

        if result == 'Yes':
            path_string = str(workspace_path.parent).replace("\\", "/")
            pm.mel.eval('workspace -o "{}"'.format(path_string))
            pm.warning('Project Changed')


def before_file_check(*args, **kwargs):
    file_object = args[1]

    try:
        prefs = cg3dmaya.preferences.get()
        if prefs.callback_switch_project != cg3dmaya.preferences.CallbackEnum.NEVER:
            _check_project(prefs.callback_switch_project == cg3dmaya.preferences.CallbackEnum.ASK, target_path=file_object.rawFullName())
    except Exception as e:
        pm.error('Project swith errored:{}'.format(e))

    om.MScriptUtil.setBool(args[0], True)


def after_save(*args, **kwargs):
    prefs = cg3dmaya.preferences.get()
    if prefs.callback_switch_project != cg3dmaya.preferences.CallbackEnum.NEVER:
        _check_project(prefs.callback_switch_project == cg3dmaya.preferences.CallbackEnum.ASK)


CHECK_FILE_ID = om.MSceneMessage.addCheckFileCallback(om.MSceneMessage.kBeforeOpenCheck, before_file_check)
AFTER_SAVE_ID = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, after_save)


###----------------------------------------
#fbx namespace logic
###----------------------------------------

FBX_PATH = None
def before_export(*args, **kwargs):
    global FBX_PATH
    FBX_PATH = None
    
    om.MScriptUtil.setBool(args[0], True)
    file_object = args[1]

    if file_object.rawFullName().lower().endswith('fbx'):
        FBX_PATH = file_object.rawFullName()


def after_export(*args, **kwargs):
    global FBX_PATH
    if FBX_PATH is None:
        return
    
    try:
        prefs = cg3dmaya.preferences.get()
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.CallbackEnum.NEVER:
            return
        
        result = None
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.CallbackEnum.ASK:
            if pm.mel.eval('FBXExportInAscii -q') == 1:
                result = pm.confirmDialog(title='3D CG Guru', message='Stripe Namespaces?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            else:
                pm.confirmDialog(title='3D CG Guru', message="Can't remove namespace. FBX file type is Binary. Expected ASCII")
                result = 'No'
                
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.CallbackEnum.ALWAYS:
            result = 'Yes'
            if pm.mel.eval('FBXExportInAscii -q') != 1:
                result = None

        if result == 'Yes':
            cg3dguru.utils.remove_namespaces(FBX_PATH)
            pm.displayInfo("##---FBX Namespace removal complete---##")
    except UnicodeDecodeError as e:
        pm.error('Removing namespace failed. Filetype must be ascii: {}'.format(e))

    except Exception as e:
        pm.error('Removing FBX namespace failed: {}'.format(e))
        

CHECK_EXPORT_ID = om.MSceneMessage.addCheckFileCallback(om.MSceneMessage.kBeforeExportCheck, before_export)
AFTER_EXPORT_ID = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterExport, after_export)





