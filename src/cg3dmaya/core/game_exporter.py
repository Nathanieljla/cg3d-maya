import pathlib
import os

import pymel.core as pm

import cg3dmaya.core.convert_fbx_file
import cg3dguru.utils as gutils

import cg3dmaya.preferences
import cg3dmaya.core.paths

from .export_type import ExportType


from enum import Enum

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
        
        converter_script = cg3dmaya.core.convert_fbx_file.__file__.replace("\\", "/")
        fbx_filename = fbx_filename.replace("\\", "/")
        save_filename = fbx_filename
        try:
            di.Commandline.run_shell_command(f"{mayapy} {converter_script} {fbx_filename} {save_filename}", converter_script)
        except Exception as e:
            print(e)        

    

    @staticmethod
    def _export(tab: ExportType):
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
            #Maybe our path is valid from the export process?
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
                    if pm.waitCursor(state=False, query=True):
                        pm.waitCursor(state=False)
                    
                    
        pm.displayInfo(f"Namespaces removed: {namespaces}. Converted to Binary: {binary}.")
        
        
    @staticmethod
    def sync_paths(file_root, exporter):
        prefs = cg3dmaya.preferences.get()
        if prefs.search_for_new_location == cg3dmaya.preferences.OptionEnum.NEVER:
            return
        
        filenames = set()
        #1 = mesh export, #2 = Animation Export, #3 = Time Editor export
        if exporter.exportTypeIndex.get() != 2:
            filenames.add(f"{exporter.exportFilename.get()}.fbx")
            
        else:
            prefix = exporter.exportFilename.get()
            for anim in exporter.animClips:
                if not anim.exportAnimClip.get():
                    continue

                name = anim.animClipName.get()
                filenames.add(
                    f"{prefix}{name}.fbx"
                )
                

        file_paths = dict()
        duplicates_found = set()
        def list_all_files(directory):
            nonlocal file_paths
            
            """Lists all files in the given directory and its subdirectories."""
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file = file.lower()
                    
                    if not file.endswith('fbx'):
                        continue
                    
                    if file in file_paths:
                        duplicates_found.add(file)
                    else:
                        file_paths[file] = os.path.join(root)
                    

        list_all_files(file_root)
        new_paths = set()
        for filename in filenames:
            filename = filename.lower()
            
            if filename in file_paths:
                new_paths.add(
                    file_paths[filename].replace("\\", "/")
                )
                
        new_paths = list(new_paths)
        if not len(new_paths):
            return
        
        if len(new_paths) > 1 or duplicates_found:
            pm.warning(f"Too many paths exist to update location. See console for more details.")
            if len(new_paths) > 1:
                print(f"\nExport data now exists at:\n{new_paths}\n")
            if duplicates_found:
                print(f"\nThere are multipe files of the same name. The duplicate names are:\n{duplicates_found}\n")
                
            return
        else:
            new_path =new_paths[0].replace("\\", "/")
            if prefs.use_option(prefs.search_for_new_location, f"Update file location to:\n{new_path}"):
                exporter.exportPath.set(new_path)



    @staticmethod
    def get_export_node(export_type: ExportType):
        game_exporters = pm.ls(type='gameFbxExporter')
        for exporter in game_exporters:
            if export_type == ExportType.MODEL and exporter.exportTypeIndex.get() == 1:
                return exporter
            elif export_type == ExportType.ANIMATION and exporter.exportTypeIndex.get() == 2:
                return exporter
            elif export_type == ExportType.TIME_EDITOR and exporter.exportTypeIndex.get() == 3:
                return exporter
            
        #this shouldn't be possible
        return None

 

    @staticmethod
    def replace_env_paths(exporter):
        env_path = exporter.exportPath.get()
        if not env_path:
            return
        
        path, root = cg3dmaya.core.paths.env_path_to_path(env_path)
        if root:
            exporter.exportPath.set(path)

        return root

    

    @staticmethod
    def add_env_paths(exporter):
        path = exporter.exportPath.get()
        if not path:
            return
        
        env_path = cg3dmaya.core.paths.path_to_env_path(path)
        exporter.exportPath.set(env_path)

        
    @staticmethod
    def export(export_type: ExportType):
        exporter = GameExporter.get_export_node(export_type)
        if not exporter:
            pm.warning("No game export data found!  Please setup the game exporter.")
            return
        
        try:
            root = GameExporter.replace_env_paths(exporter)
            if root:
                GameExporter.sync_paths(root, exporter)
                #only do this if we're dealing with paths that are relative
                #to a project environment variable, otherwise you might start
                #creating folder from other people's harddrive paths
                pathlib.Path(exporter.exportPath.get()).mkdir(parents=True, exist_ok=True)

            GameExporter._export(export_type)
        except Exception as e:
            pm.warning(e)
        finally:
            GameExporter.add_env_paths(exporter)


    @staticmethod
    def export_animations():
        GameExporter.export(ExportType.ANIMATION)

    @staticmethod
    def export_model():
        GameExporter.export(ExportType.MODEL)
        
    @staticmethod
    def export_time_editor():
        GameExporter.export(ExportType.TIME_EDITOR)
