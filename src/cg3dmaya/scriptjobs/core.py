
import pathlib
import re

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
    #so convert to a string.  Also on windows network drives use
    #backslashes
    current_path_str = str(current_path).replace("\\", "/")
    if current_path_str.startswith(project_path):
        return

    workspace_path = None
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
        if prefs.callback_switch_project != cg3dmaya.preferences.OptionEnum.NEVER:
            _check_project(prefs.callback_switch_project == cg3dmaya.preferences.OptionEnum.ASK, target_path=file_object.rawFullName())
    except Exception as e:
        pm.error('Project swith errored:{}'.format(e))

    om.MScriptUtil.setBool(args[0], True)


def after_save(*args, **kwargs):
    prefs = cg3dmaya.preferences.get()
    if prefs.callback_switch_project != cg3dmaya.preferences.OptionEnum.NEVER:
        _check_project(prefs.callback_switch_project == cg3dmaya.preferences.OptionEnum.ASK)


CHECK_FILE_ID = om.MSceneMessage.addCheckFileCallback(om.MSceneMessage.kBeforeOpenCheck, before_file_check)
AFTER_SAVE_ID = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, after_save)


###----------------------------------------
#Update reference check
###----------------------------------------
def check_ref_version(ret_code, file_obj, client_data=None):
    try:
        prefs = prefs = cg3dmaya.preferences.get()
        updates = prefs.major_update + prefs.minor_update + prefs.patch_update
        if updates and prefs.ref_expression:
            regex = re.compile(prefs.ref_expression)
            source_fullpath = file_obj.rawFullName().replace("\\", "/").replace("//", "/")
            ref_path = pathlib.Path(source_fullpath)
            ref_dir = ref_path.parent

            source_info = regex.search(ref_path.name).groupdict()
            source_name = source_info.get("base_name", "")
            major = 0 if not source_info.get("major") else source_info.get("major")
            minor = 0 if not source_info.get("minor") else source_info.get("minor")
            patch = 0 if not source_info.get("patch") else source_info.get("patch")
            source_version = (int(major), int(minor), int(patch))

            all_files = [str(f) for f in ref_dir.iterdir() if f.is_file()]
            ref_versions = []
            ref_files = {}

            for file_path in all_files:
                file = pathlib.Path(file_path)
                file_pattern = regex.search(file.name)
                if not file_pattern:
                    continue

                file_info = file_pattern.groupdict()
                if file_info.get("base_name") != source_name:
                    continue

                major = 0 if not file_info.get("major") else file_info.get("major")
                minor = 0 if not file_info.get("minor") else file_info.get("minor")
                patch = 0 if not file_info.get("patch") else file_info.get("patch")

                major, minor, patch = (int(major), int(minor), int(patch))
                ref_versions.append((major, minor, patch))

                major_files: dict = ref_files.setdefault(major, {})
                minor_files: dict = major_files.setdefault(minor, {})
                minor_files[patch] = file_path

            if not ref_versions:
                return

            ref_versions.sort()
            highest_version = ref_versions[-1]
            if highest_version <= source_version:
                return

            new_file = None
            if prefs.major_update == 1 and prefs.minor_update == 1 and prefs.patch_update == 1:
                new_file = ref_files[highest_version[0]][highest_version[1]][highest_version[2]]
                
            else:
                #Get the highest major value if allowed, else use the source's major value
                target_major = source_version[0] if not prefs.major_update else highest_version[0]
                major_dict = ref_files.get(target_major, {})
                if not major_dict:
                    return

                #If we're using the sources major value and we're not allowed
                #to upgrade minors, then we'll use the source minor, else
                #we'll use the highest minor.
                highest_minor = sorted(major_dict.keys())[-1]
                matches_source = target_major == source_version[0]
                target_minor = source_version[1] if matches_source and not prefs.minor_update else highest_minor
                minor_dict = major_dict.get(target_minor, {})
                if not minor_dict:
                    return

                #If we're using the sources major.minor and we're not allowed allowed to upgrade patches
                #then we'll use then source patch, else we'll use the highest patch.
                highest_patch = sorted(minor_dict.keys())[-1]
                matches_source = matches_source and target_minor == source_version[1]
                target_patch = source_version[2] if matches_source and not prefs.patch_update else highest_patch
                target_file = minor_dict.get(target_patch, "")
                if not target_file:
                    return
                
                target_version = (target_major, target_minor, target_patch)
                if target_version <= source_version:
                    return

                delta = tuple([target_version[idx] - value for idx, value in enumerate(source_version)])

                #If the new version is a major update
                check = delta[0] > 0 and prefs.major_update == 2
                
                #If the new version is a minor update
                if delta[0] == 0 and delta[1] > 0 and prefs.minor_update == 2:
                    check = True

                #If thew new version is a patch update
                if delta[0] == 0 and delta[1] == 0 and prefs.patch_update == 2:
                    check = True

                if check:
                    old_name = ref_path.name
                    new_name = pathlib.Path(target_file).name
                    
                    result = pm.confirmDialog(title='3D CG Guru', message=f"Update {old_name} with {new_name}", messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                    if result == 'Yes':
                        new_file = target_file
                else:
                    new_file = target_file

            if new_file:
                file_obj.setRawFullName(new_file)

    except Exception as e:
        pm.error('Guru Reference update errored:{}'.format(e))

    finally:
        om.MScriptUtil.setBool(ret_code, True)


CHECK_REF_ID = om.MSceneMessage.addCheckFileCallback(om.MSceneMessage.kBeforeLoadReferenceCheck, check_ref_version)



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
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.OptionEnum.NEVER:
            return
        
        result = None
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.OptionEnum.ASK:
            if pm.mel.eval('FBXExportInAscii -q') == 1:
                result = pm.confirmDialog(title='3D CG Guru', message='Stripe Namespaces?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            else:
                pm.confirmDialog(title='3D CG Guru', message="Can't remove namespace. FBX file type is Binary. Expected ASCII")
                result = 'No'
                
        if prefs.callback_fbx_namespaces == cg3dmaya.preferences.OptionEnum.ALWAYS:
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





