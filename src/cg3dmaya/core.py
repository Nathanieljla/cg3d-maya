from enum import Enum
import pathlib
import os

import pymel.core as pm

import cg3dmaya.convert_fbx_file
import cg3dguru.utils as gutils

import cg3dmaya.preferences


class ExportType(Enum):
    MODEL = 'Model'
    ANIMATION = 'Animation'
    TIME_EDITOR = 'Time_editor'



class GameExporter():
    PLUGIN_NAME = 'gameFbxExporter'
    
    @staticmethod
    def _get_export_path(path_str):        
        export_path = pathlib.Path(path_str)
        if not export_path.exists():
            #this must be project relative or a yet to be created dir
            #lets decide which it is
            abs_path = pathlib.Path(pm.mel.eval('workspace -q -rd')).joinpath(path_str)
            if abs_path.exists():
                export_path = abs_path
            else:
                export_path = None

        return export_path


    @staticmethod
    def _get_file_stats(folder_path):
        file_stats = {}

        for i in folder_path.iterdir():
            file_stats[str(i)] = os.stat(i).st_mtime
            
        return file_stats
    
    
    @staticmethod
    def convert_ascii_to_binary(fbx_filename):
        import cg3dguru.utils.drop_installer as di

        mayapy, pip = di.Commandline.get_python_paths()
        
        converter_script = cg3dmaya.convert_fbx_file.__file__.replace("\\", "/")
        fbx_filename = fbx_filename.replace("\\", "/")
        save_filename = fbx_filename
        try:
            di.Commandline.run_shell_command(f"{mayapy} {converter_script} {fbx_filename} {save_filename}", converter_script)
        except Exception as e:
            print(e)        

    
    @staticmethod
    def export(tab: ExportType):
        if not pm.pluginInfo(GameExporter.PLUGIN_NAME, q=True, loaded=True):
            try:
                pm.loadPlugin(GameExporter.PLUGIN_NAME)
            except:
                pass
            finally:
                if not pm.pluginInfo(GameExporter.PLUGIN_NAME, q=True, loaded=True):
                    pm.error("Can't load game exporter!")
                    
        #First let's make sure the export type is set to ascii
        for node in pm.ls(type="gameFbxExporter"):
            node.fileType.set(1)


        pm.mel.eval(GameExporter.PLUGIN_NAME)

        #Find the export tab
        export_tab = None
        for i in pm.lsUI(l=True, type='tabLayout'):
            if i.endswith('gameExporterTabLayout'):
                export_tab = i

        if not export_tab:
            pm.error("No game exporter detected.  Export failed!")

        target_tab = 'gameExporterModelTab'
        target_filetype = 'model_gameExporterFileType'
        path_name = 'model_gameExporterExportPath'
        if tab == ExportType.ANIMATION:
            target_tab = 'gameExporterAnimationTab'
            target_filetype = 'anim_gameExporterFileType'
            path_name = 'anim_gameExporterExportPath'
        elif tab == ExportType.TIME_EDITOR:
            target_tab = 'gameExporterTimeEditorTab'
            target_filetype = 'timeEditor_gameExporterFileType'
            path_name = 'timeEditor_gameExporterExportPath'

        #Active the target expor tab
        active_tab = pm.tabLayout(export_tab, query=True, selectTab=True)
        if active_tab != target_tab:
            pm.tabLayout(export_tab, edit=True, selectTab=target_tab)
            pm.mel.eval(pm.tabLayout(export_tab, query=True, selectCommand=True))
            
        #Let's make sure we're set to ascii (so the namespaces can be stripped)
        filetype_control = None
        for i in pm.lsUI(l=True,type='control'):
            if i.endswith(target_filetype):
                filetype_control = i

        if pm.optionMenu(filetype_control, q=True, value=True) != 'ASCII':
            pm.optionMenu(filetype_control, edit=True, value='ASCII')
            
        #Let's find the export path value so we can identify the files to
        #remove the namespaces from
        path_control = None
        for i in pm.lsUI(l=True,type='control'):
            if i.endswith(path_name):
                path_control = i
                
        if not path_control:
            pm.error("Failed to find export path. Can't export.")
            
        export_path_str = pm.textField(path_control, q=True, text=True)
        export_path = GameExporter._get_export_path(export_path_str)
        pre_file_stats = {}
        post_file_stats = {}
        
        if export_path:
            pre_file_stats = GameExporter._get_file_stats(export_path)

        #run the export
        pm.mel.eval('gameExp_DoExport')
        
        if not export_path:
            #Mayeb our path is valid from the export projcess?
            export_path = GameExporter._get_export_path(export_path_str)

        if not export_path:
            pm.warning("Couldn't find the export path.  Namespaces weren't removed!")
            return

        post_file_stats = GameExporter._get_file_stats(export_path)
        namespaces = False
        binary = False
        
        prefs = cg3dmaya.preferences.get()
        remove_submorphers = prefs.use_option(prefs.remove_subdeformer_namespaces, "Remove Subdeformer Namespaces too?")
        convert_binary = prefs.use_option(prefs.convert_fbx_to_binary, "Convert to Binary FBX File?")
        
        for filename, value in post_file_stats.items():
            if filename not in pre_file_stats or value > pre_file_stats[filename]:
                try:
                    pm.waitCursor(state=True)
                    print("Removing namespace: {}".format(filename))
                    gutils.remove_namespaces(filename, remove_submorphers)
                    namespaces = True
                    
                except Exception as e:
                    pm.warning("Namespace Failed. Make sure it's an ascii file:{} {}".format(filename, e))
                finally:
                    pm.waitCursor(state=False)

                try:
                    if convert_binary:
                        pm.waitCursor(state=True)
                        print("Converting ascii to binary")
                        GameExporter.convert_ascii_to_binary(filename)
                        binary = True
                    
                except Exception as e:
                    pm.warning("FBX to binary Failed. Make sure it's an ascii file:{} {}".format(filename, e))
                finally:
                    pm.waitCursor(state=False)
                    
                    
        pm.displayInfo(f"Namespaces removed: {namespaces}. Converted to Binary: {binary}.")


    @staticmethod
    def export_animations():
        GameExporter.export(ExportType.ANIMATION)

    @staticmethod
    def export_model():
        GameExporter.export(ExportType.MODEL)
        
    @staticmethod
    def export_time_editor():
        GameExporter.export(ExportType.TIME_EDITOR)
        


        

        
class ShapeCloner():
    @staticmethod
    def _move_shapes():
        result = pm.confirmDialog(title='Shape Cloner', message='Move Shape(s) to joint(s)?', messageAlign='center', button=['Yes', 'No'], defaultButton='Yes', dismissString='No')
        return result == 'Yes'
    
    
    @staticmethod
    def _get_temp_transforms(transform_list):
        temp_transforms = pm.duplicate(transform_list)
        pm.parent(temp_transforms, world=True, absolute=True)
        pm.makeIdentity(temp_transforms, apply=True, translate=False, rotate=True, scale=True)
        
        return temp_transforms
        
    
    @staticmethod
    def _shapes_to_ctrl(transform_set, ctrl_set, only_match=False, move_shapes=None, bake=True):
        transform_list = list(transform_set)
        
        if bake:
            pm.select(transform_list)
            pm.mel.eval('BakeCustomPivot')

        ctrl = list(ctrl_set)[0]
        temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
        shapes = pm.listRelatives(temp_transforms, shapes=True)
        
        if move_shapes is None:
            move_shapes = ShapeCloner._move_shapes()
        
        if not move_shapes:
            ctrl_matrix = gutils.MatrixUtils.get_world_matrix(ctrl)
            for i in temp_transforms:
                temp_matrix = gutils.MatrixUtils.get_world_matrix(i)
                adjusted_matrix = temp_matrix * ctrl_matrix.inverse()
                gutils.MatrixUtils.set_world_matrix(i, adjusted_matrix, no_scale=True)
                
            pm.makeIdentity(temp_transforms, apply=True, translate=True, rotate=True, scale=True)
            
        else:
            #TODO:Eventually make the shapes align to the user defined foward and up vects.
            pass
        
        if only_match:
            for transform in temp_transforms:
                gutils.MatrixUtils.set_world_matrix(transform,
                                                   gutils.MatrixUtils.get_world_matrix(ctrl), no_scale=True)
        else:
            for shape in shapes:
                if not shape.type() == 'nurbsCurve':
                    continue
                
                pm.parent(shape, ctrl, relative=True, shape=True)
    
            pm.delete(temp_transforms)
                

    @staticmethod
    def _shape_to_ctrls(transform_set, ctrl_set, only_match=False, bake=True):
        ctrls = list(ctrl_set)
        transform_list = list(transform_set)
        if bake:
            pm.select(transform_list)
            pm.mel.eval('BakeCustomPivot')

        for ctrl in ctrls:
            #This should be a list with one element
            temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
            shapes = pm.listRelatives(temp_transforms, shapes=True)

            #TODO:Eventually make the shapes align to the user defined foward and up vects.
            #where we assume Z=forward and Y=Up

            if only_match:
                gutils.MatrixUtils.set_world_matrix(temp_transforms[0],
                                                   gutils.MatrixUtils.get_world_matrix(ctrl), no_scale=True)
            else:
                for shape in shapes:
                    if not shape.type() == 'nurbsCurve':
                        continue
                    
                    pm.parent(shape, ctrl, relative=True, shape=True)
        
                pm.delete(temp_transforms)
        
    
    @staticmethod
    def _shapes_to_ctrls(transform_set, ctrl_set):
        #The size of the two lists is assumed to match
        
        #the only_match command doesn't make sense in this context
        #since the shapes have to already be in place to do joint trasnform matching.

        #Let's match each joint to the closest transform
        ctrls = list(ctrl_set)
        transforms = list(transform_set)
        pairing = []
        
        pm.select(transforms)
        pm.mel.eval('BakeCustomPivot')
        
        for transform in transforms:
            t_pos = gutils.MatrixUtils.get_world_pos(transform)
            j_pos = gutils.MatrixUtils.get_world_pos(ctrls[0])

            distance = t_pos.distanceTo(j_pos)
            closest_ctrl = ctrls[0]

            for ctrl in ctrls:
                j_pos = gutils.MatrixUtils.get_world_pos(ctrl)
                current_distance = t_pos.distanceTo(j_pos)
                
                if current_distance < distance:
                    distance = current_distance
                    closest_ctrl = ctrl

            pairing.append((transform, closest_ctrl))
            #we might have mutlipel shapes attaching to one joint, so let's not
            #reduce our list.
            #ctrls.pop(ctrls.index(closest_ctrl))

        #now that things are paired up we can
        for transform, ctrl in pairing:
            ShapeCloner._shapes_to_ctrl([transform], [ctrl], only_match=False, move_shapes=False, bake=False)
            
        

    @staticmethod
    def run(only_match=False):
        selected_ctrls = pm.ls(sl=True, type=['joint', 'ikHandle'])
        selected_transforms = pm.ls(sl=True, et='transform')

        #empty groups and locators needs to be found and added
        #to the ctrls set
        ctrl_transforms = set()
        for i in selected_transforms:
            shapes = pm.listRelatives(i, shapes=True)
            if not shapes:
                ctrl_transforms.add(i)
            elif len(shapes) == 1 and shapes[0].type() == 'locator':
                ctrl_transforms.add(i)
                #pm.delete(shapes[0])

        ctrl_set = set(selected_ctrls)
        ctrl_set.update(ctrl_transforms)
        
        transform_set = set(selected_transforms)
        transform_set.difference_update(ctrl_set)

        if not ctrl_set:
            pm.error("Not joint(s) (or other controls) found in selection!")

        if not transform_set:
            pm.error("No transform(s) found in selection!")

        if len(ctrl_set) == 1:
            ShapeCloner._shapes_to_ctrl(transform_set, ctrl_set, only_match=only_match)

        elif len(transform_set) == 1:
            ShapeCloner._shape_to_ctrls(transform_set, ctrl_set, only_match=only_match)

        #we don't need this condition now that we don't pop the ctrls as they're
        #paired with a transform.
        #elif len(transform_set) <= len(ctrl_set):
        else:
            ShapeCloner._shapes_to_ctrls(transform_set, ctrl_set)

        #else:
            #pm.error("Can't resolve transform and ctrl counts.")
            

        
        
        
def run():
    ShapeCloner.run()


