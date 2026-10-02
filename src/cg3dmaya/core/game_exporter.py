"""Helpers for driving Maya's Game Exporter without PyMEL."""

from enum import Enum
import os
import pathlib

from maya import cmds, mel
from maya.api import OpenMaya as om

import cg3dguru.utils as gutils
import cg3dmaya.core.convert_fbx_file
import cg3dmaya.core.paths
import cg3dmaya.preferences


class ExportType(Enum):
    MODEL = "Model"
    ANIMATION = "Animation"
    TIME_EDITOR = "Time_editor"


def _plug(node, attribute):
    return "{}.{}".format(node, attribute)


class GameExporter:
    PLUGIN_NAME = "gameFbxExporter"

    @staticmethod
    def _get_export_path(path_str):
        export_path = pathlib.Path(path_str)
        if not export_path.exists():
            project_path = pathlib.Path(cmds.workspace(query=True, rootDirectory=True))
            absolute_path = project_path.joinpath(path_str)
            export_path = absolute_path if absolute_path.exists() else None
        return export_path

    @staticmethod
    def _get_file_stats(folder_path):
        return {str(path): path.stat().st_mtime for path in folder_path.iterdir()}

    @staticmethod
    def convert_ascii_to_binary(fbx_filename):
        import cg3dguru.utils.drop_installer as installer

        mayapy, _ = installer.Commandline.get_python_paths()
        converter_script = cg3dmaya.core.convert_fbx_file.__file__.replace("\\", "/")
        fbx_filename = fbx_filename.replace("\\", "/")
        command = '"{}" "{}" "{}" "{}"'.format(
            mayapy, converter_script, fbx_filename, fbx_filename
        )
        try:
            installer.Commandline.run_shell_command(command, converter_script)
        except Exception as error:
            print(error)

    @staticmethod
    def _ensure_plugin():
        if not cmds.pluginInfo(GameExporter.PLUGIN_NAME, query=True, loaded=True):
            try:
                cmds.loadPlugin(GameExporter.PLUGIN_NAME)
            except RuntimeError:
                pass
        if not cmds.pluginInfo(GameExporter.PLUGIN_NAME, query=True, loaded=True):
            cmds.error("Can't load game exporter!")

    @staticmethod
    def _find_control(suffix, control_type="control"):
        for control in cmds.lsUI(long=True, type=control_type) or []:
            if control.endswith(suffix):
                return control
        return None

    @staticmethod
    def _export(tab: ExportType):
        GameExporter._ensure_plugin()

        for node in cmds.ls(type="gameFbxExporter") or []:
            cmds.setAttr(_plug(node, "fileType"), 1)

        mel.eval(GameExporter.PLUGIN_NAME)
        export_tab = GameExporter._find_control(
            "gameExporterTabLayout", control_type="tabLayout"
        )
        if not export_tab:
            cmds.error("No game exporter detected. Export failed!")

        target_tab = "gameExporterModelTab"
        target_filetype = "model_gameExporterFileType"
        path_name = "model_gameExporterExportPath"
        if tab == ExportType.ANIMATION:
            target_tab = "gameExporterAnimationTab"
            target_filetype = "anim_gameExporterFileType"
            path_name = "anim_gameExporterExportPath"
        elif tab == ExportType.TIME_EDITOR:
            target_tab = "gameExporterTimeEditorTab"
            target_filetype = "timeEditor_gameExporterFileType"
            path_name = "timeEditor_gameExporterExportPath"

        active_tab = cmds.tabLayout(export_tab, query=True, selectTab=True)
        if active_tab != target_tab:
            cmds.tabLayout(export_tab, edit=True, selectTab=target_tab)
            select_command = cmds.tabLayout(
                export_tab, query=True, selectCommand=True
            )
            if select_command:
                mel.eval(select_command)

        filetype_control = GameExporter._find_control(target_filetype)
        if not filetype_control:
            cmds.error("Failed to find the Game Exporter file-type control.")
        if cmds.optionMenu(filetype_control, query=True, value=True) != "ASCII":
            cmds.optionMenu(filetype_control, edit=True, value="ASCII")

        path_control = GameExporter._find_control(path_name)
        if not path_control:
            cmds.error("Failed to find export path. Can't export.")

        export_path_str = cmds.textField(path_control, query=True, text=True)
        export_path = GameExporter._get_export_path(export_path_str)
        pre_file_stats = GameExporter._get_file_stats(export_path) if export_path else {}

        mel.eval("gameExp_DoExport")

        export_path = export_path or GameExporter._get_export_path(export_path_str)
        if not export_path:
            cmds.warning("Couldn't find the export path. Namespaces weren't removed!")
            return

        post_file_stats = GameExporter._get_file_stats(export_path)
        namespaces_removed = False
        converted_to_binary = False
        prefs = cg3dmaya.preferences.get()
        remove_subdeformers = prefs.use_option(
            prefs.remove_subdeformer_namespaces,
            "Remove Subdeformer Namespaces too?",
        )
        convert_binary = prefs.use_option(
            prefs.convert_fbx_to_binary, "Convert to Binary FBX File?"
        )

        for filename, modified_time in post_file_stats.items():
            if filename in pre_file_stats and modified_time <= pre_file_stats[filename]:
                continue

            try:
                cmds.waitCursor(state=True)
                print("Removing namespace: {}".format(filename))
                gutils.remove_namespaces(filename, remove_subdeformers)
                namespaces_removed = True
            except Exception as error:
                cmds.warning(
                    "Namespace failed. Make sure it is an ASCII file: {} {}".format(
                        filename, error
                    )
                )
            finally:
                cmds.waitCursor(state=False)

            try:
                if convert_binary:
                    cmds.waitCursor(state=True)
                    print("Converting ASCII to binary")
                    GameExporter.convert_ascii_to_binary(filename)
                    converted_to_binary = True
            except Exception as error:
                cmds.warning(
                    "FBX-to-binary conversion failed for {}: {}".format(
                        filename, error
                    )
                )
            finally:
                if cmds.waitCursor(query=True, state=True):
                    cmds.waitCursor(state=False)

        om.MGlobal.displayInfo(
            "Namespaces removed: {}. Converted to Binary: {}.".format(
                namespaces_removed, converted_to_binary
            )
        )

    @staticmethod
    def sync_paths(file_root, exporter):
        prefs = cg3dmaya.preferences.get()
        if prefs.search_for_new_location == cg3dmaya.preferences.OptionEnum.NEVER:
            return

        filenames = set()
        export_type_index = cmds.getAttr(_plug(exporter, "exportTypeIndex"))
        prefix = cmds.getAttr(_plug(exporter, "exportFilename"))
        if export_type_index != 2:
            filenames.add("{}.fbx".format(prefix))
        else:
            indices = cmds.getAttr(
                _plug(exporter, "animClips"), multiIndices=True
            ) or []
            for index in indices:
                clip = "{}.animClips[{}]".format(exporter, index)
                if not cmds.getAttr(clip + ".exportAnimClip"):
                    continue
                name = cmds.getAttr(clip + ".animClipName")
                filenames.add("{}{}.fbx".format(prefix, name))

        file_paths = {}
        duplicates_found = set()
        for root, _, files in os.walk(file_root):
            for filename in files:
                filename = filename.lower()
                if not filename.endswith(".fbx"):
                    continue
                if filename in file_paths:
                    duplicates_found.add(filename)
                else:
                    file_paths[filename] = root

        new_paths = {
            file_paths[filename.lower()].replace("\\", "/")
            for filename in filenames
            if filename.lower() in file_paths
        }
        if not new_paths:
            return

        if len(new_paths) > 1 or duplicates_found:
            cmds.warning("Too many paths exist to update the export location.")
            if len(new_paths) > 1:
                print("\nExport data now exists at:\n{}\n".format(sorted(new_paths)))
            if duplicates_found:
                print(
                    "\nDuplicate FBX names were found:\n{}\n".format(
                        sorted(duplicates_found)
                    )
                )
            return

        new_path = next(iter(new_paths))
        if prefs.use_option(
            prefs.search_for_new_location,
            "Update file location to:\n{}".format(new_path),
        ):
            cmds.setAttr(_plug(exporter, "exportPath"), new_path, type="string")

    @staticmethod
    def get_export_node(export_type: ExportType):
        for exporter in cmds.ls(type="gameFbxExporter") or []:
            index = cmds.getAttr(_plug(exporter, "exportTypeIndex"))
            if export_type == ExportType.MODEL and index == 1:
                return exporter
            if export_type == ExportType.ANIMATION and index == 2:
                return exporter
            if export_type == ExportType.TIME_EDITOR and index == 3:
                return exporter
        return None

    @staticmethod
    def replace_env_paths(exporter):
        env_path = cmds.getAttr(_plug(exporter, "exportPath"))
        if not env_path:
            return None
        path, root = cg3dmaya.core.paths.env_path_to_path(env_path)
        if root:
            cmds.setAttr(_plug(exporter, "exportPath"), path, type="string")
        return root

    @staticmethod
    def add_env_paths(exporter):
        path = cmds.getAttr(_plug(exporter, "exportPath"))
        if not path:
            return
        env_path = cg3dmaya.core.paths.path_to_env_path(path)
        cmds.setAttr(_plug(exporter, "exportPath"), env_path, type="string")

    @staticmethod
    def export(export_type: ExportType):
        exporter = GameExporter.get_export_node(export_type)
        if not exporter:
            cmds.warning("No game export data found! Please set up the Game Exporter.")
            return

        try:
            root = GameExporter.replace_env_paths(exporter)
            if root:
                GameExporter.sync_paths(root, exporter)
                pathlib.Path(cmds.getAttr(_plug(exporter, "exportPath"))).mkdir(
                    parents=True, exist_ok=True
                )
            GameExporter._export(export_type)
        except Exception as error:
            cmds.warning(str(error))
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
