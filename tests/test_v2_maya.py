"""Maya integration coverage for the PyMEL-free package."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import maya.standalone


def setUpModule():
    try:
        maya.standalone.initialize(name="python")
    except RuntimeError:
        pass


def tearDownModule():
    try:
        maya.standalone.uninitialize()
    except RuntimeError:
        pass


class MayaV2Tests(unittest.TestCase):
    def setUp(self):
        from maya import cmds

        cmds.file(new=True, force=True)

        import cg3dmaya_v2.preferences.core as preferences_core

        self.preferences_core = preferences_core
        preferences_core._PREFS_INSTANCE = preferences_core.new()

    def tearDown(self):
        self.preferences_core._PREFS_INSTANCE = None

    def test_environment_paths_round_trip(self):
        from cg3dmaya_v2.core import paths

        prefs = self.preferences_core.get()
        prefs.environment_variables = {"CG3D_MAYA_TEST_ROOT"}

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).as_posix()
            file_path = root + "/exports/character.fbx"
            with mock.patch.dict(
                os.environ, {"CG3D_MAYA_TEST_ROOT": root}, clear=False
            ):
                env_path = paths.path_to_env_path(file_path)
                resolved, resolved_root = paths.env_path_to_path(env_path)

        self.assertEqual(
            env_path, "%CG3D_MAYA_TEST_ROOT%/exports/character.fbx"
        )
        self.assertEqual(resolved, file_path)
        self.assertEqual(resolved_root, root)

    def test_game_exporter_node_and_path_sync(self):
        from maya import cmds

        from cg3dmaya_v2.core.game_exporter import ExportType, GameExporter

        try:
            cmds.loadPlugin(GameExporter.PLUGIN_NAME, quiet=True)
        except RuntimeError as error:
            self.skipTest("Game Exporter plug-in is unavailable: {}".format(error))

        exporter = cmds.createNode("gameFbxExporter")
        cmds.setAttr(exporter + ".exportTypeIndex", 2)
        cmds.setAttr(exporter + ".exportFilename", "Rig_", type="string")
        cmds.setAttr(exporter + ".animClips[0].exportAnimClip", True)
        cmds.setAttr(
            exporter + ".animClips[0].animClipName", "Walk", type="string"
        )

        prefs = self.preferences_core.get()
        prefs.search_for_new_location = self.preferences_core.OptionEnum.ALWAYS

        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir, "nested", "exports")
            export_dir.mkdir(parents=True)
            Path(export_dir, "Rig_Walk.fbx").touch()
            cmds.setAttr(exporter + ".exportPath", temp_dir, type="string")
            GameExporter.sync_paths(temp_dir, exporter)

            self.assertEqual(
                cmds.getAttr(exporter + ".exportPath"), export_dir.as_posix()
            )

        self.assertEqual(
            GameExporter.get_export_node(ExportType.ANIMATION), exporter
        )

    def test_preferences_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs_path = Path(temp_dir, "prefs.pickle")
            with mock.patch.object(
                self.preferences_core, "_get_save_path", return_value=prefs_path
            ):
                prefs = self.preferences_core.new()
                prefs.environment_variables = {"PROJECT_ROOT"}
                self.preferences_core.set_prefs(prefs)
                self.preferences_core._PREFS_INSTANCE = None
                loaded = self.preferences_core.get()

        self.assertEqual(loaded.environment_variables, {"PROJECT_ROOT"})

    def test_shape_cloner_moves_curve_shape_to_joint(self):
        from maya import cmds

        from cg3dmaya_v2.core.shape_cloner import ShapeCloner

        source = cmds.circle(name="source_ctrl", normal=(1, 0, 0))[0]
        cmds.select(clear=True)
        target = cmds.joint(name="target_joint", position=(3, 2, 1))

        ShapeCloner._shapes_to_ctrl(
            [source], [target], move_shapes=True, bake=False
        )

        shapes = cmds.listRelatives(target, shapes=True, fullPath=True) or []
        self.assertTrue(shapes)
        self.assertTrue(all(cmds.nodeType(shape) == "nurbsCurve" for shape in shapes))
        self.assertTrue(cmds.objExists(source))


if __name__ == "__main__":
    unittest.main()
