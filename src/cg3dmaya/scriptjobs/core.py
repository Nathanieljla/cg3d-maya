import pymel.core as pm

PROJECT_SWITCH_OPEN_ID = -1
PROJECT_SWITCH_SAVE_ID = -1

def _check_projects(*args, **kwargs):
    project_path = pm.mel.eval('workspace -q -rd')
    current_path = pm.system.sceneName()
    if current_path.startswith(project_path):
        return

    workspace_path = None
    while not current_path.samepath(current_path.parent):
        current_path = current_path.parent
        if (current_path + '/workspace.mel').exists():
            workspace_path = current_path
            break
        
    if workspace_path is not None:
        result = pm.confirmDialog(title='3D CG Guru', message='Switch Projects and reload?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if result == 'Yes':
            pm.mel.eval('workspace -o "{}"'.format(workspace_path))
            pm.system.openFile(pm.system.sceneName())


def register_project_switch(register: bool | None = None):
    global PROJECT_SWITCH_OPEN_ID, PROJECT_SWITCH_SAVE_ID

    if register is None:
        #make this read the prefs
        register = True
        
    if register:
        PROJECT_SWITCH_OPEN_ID = pm.scriptJob(event=["SceneOpened", _check_projects], protected=True)
        PROJECT_SWITCH_SAVE_ID = pm.scriptJob(event=["SceneSaved", _check_projects], protected=True)
    else:
        if PROJECT_SWITCH_OPEN_ID > -1:
            pm.scriptJob(kill=PROJECT_SWITCH_OPEN_ID, force=True)
        if PROJECT_SWITCH_SAVE_ID > -1:
            pm.scriptJob(kill=PROJECT_SWITCH_SAVE_ID, force=True)






