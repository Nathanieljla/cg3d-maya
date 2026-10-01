"""Clone NURBS control shapes using Maya's native command layer."""

from maya import cmds, mel

import cg3dguru.utils as gutils


class ShapeCloner:
    @staticmethod
    def _move_shapes():
        result = cmds.confirmDialog(
            title="Shape Cloner",
            message="Move Shape(s) to joint(s)?",
            messageAlign="center",
            button=["Yes", "No"],
            defaultButton="Yes",
            dismissString="No",
        )
        return result == "Yes"

    @staticmethod
    def _get_temp_transforms(transform_list):
        temp_transforms = cmds.duplicate(
            list(transform_list), returnRootsOnly=True
        ) or []
        if temp_transforms:
            parented = [
                transform
                for transform in temp_transforms
                if cmds.listRelatives(transform, parent=True)
            ]
            if parented:
                cmds.parent(parented, world=True, absolute=True)
            cmds.makeIdentity(
                temp_transforms,
                apply=True,
                translate=False,
                rotate=True,
                scale=True,
            )
        return temp_transforms

    @staticmethod
    def _shapes_to_ctrl(
        transform_set, ctrl_set, only_match=False, move_shapes=None, bake=True
    ):
        transform_list = list(transform_set)
        if bake:
            cmds.select(transform_list)
            mel.eval("BakeCustomPivot")

        ctrl = next(iter(ctrl_set))
        temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
        shapes = cmds.listRelatives(
            temp_transforms, shapes=True, fullPath=True
        ) or []

        if move_shapes is None:
            move_shapes = ShapeCloner._move_shapes()

        if not move_shapes:
            ctrl_matrix = gutils.MatrixUtils.get_world_matrix(ctrl)
            for transform in temp_transforms:
                temp_matrix = gutils.MatrixUtils.get_world_matrix(transform)
                adjusted_matrix = temp_matrix * ctrl_matrix.inverse()
                gutils.MatrixUtils.set_world_matrix(
                    transform, adjusted_matrix, no_scale=True
                )
            cmds.makeIdentity(
                temp_transforms,
                apply=True,
                translate=True,
                rotate=True,
                scale=True,
            )

        if only_match:
            ctrl_matrix = gutils.MatrixUtils.get_world_matrix(ctrl)
            for transform in temp_transforms:
                gutils.MatrixUtils.set_world_matrix(
                    transform, ctrl_matrix, no_scale=True
                )
        else:
            for shape in shapes:
                if cmds.nodeType(shape) == "nurbsCurve":
                    cmds.parent(shape, ctrl, relative=True, shape=True)
            cmds.delete(temp_transforms)

    @staticmethod
    def _shape_to_ctrls(transform_set, ctrl_set, only_match=False, bake=True):
        ctrls = list(ctrl_set)
        transform_list = list(transform_set)
        if bake:
            cmds.select(transform_list)
            mel.eval("BakeCustomPivot")

        for ctrl in ctrls:
            temp_transforms = ShapeCloner._get_temp_transforms(transform_list)
            shapes = cmds.listRelatives(
                temp_transforms, shapes=True, fullPath=True
            ) or []

            if only_match:
                gutils.MatrixUtils.set_world_matrix(
                    temp_transforms[0],
                    gutils.MatrixUtils.get_world_matrix(ctrl),
                    no_scale=True,
                )
            else:
                for shape in shapes:
                    if cmds.nodeType(shape) == "nurbsCurve":
                        cmds.parent(shape, ctrl, relative=True, shape=True)
                cmds.delete(temp_transforms)

    @staticmethod
    def _shapes_to_ctrls(transform_set, ctrl_set):
        ctrls = list(ctrl_set)
        transforms = list(transform_set)
        pairing = []

        cmds.select(transforms)
        mel.eval("BakeCustomPivot")

        for transform in transforms:
            transform_position = gutils.MatrixUtils.get_world_pos(transform)
            closest_ctrl = ctrls[0]
            distance = (
                transform_position - gutils.MatrixUtils.get_world_pos(closest_ctrl)
            ).length()

            for ctrl in ctrls:
                current_distance = (
                    transform_position - gutils.MatrixUtils.get_world_pos(ctrl)
                ).length()
                if current_distance < distance:
                    distance = current_distance
                    closest_ctrl = ctrl
            pairing.append((transform, closest_ctrl))

        for transform, ctrl in pairing:
            ShapeCloner._shapes_to_ctrl(
                [transform], [ctrl], only_match=False, move_shapes=False, bake=False
            )

    @staticmethod
    def run(only_match=False):
        selected_ctrls = cmds.ls(
            selection=True, type=["joint", "ikHandle"], long=True
        ) or []
        selected_transforms = cmds.ls(
            selection=True, exactType="transform", long=True
        ) or []

        ctrl_transforms = set()
        for transform in selected_transforms:
            shapes = cmds.listRelatives(
                transform, shapes=True, fullPath=True
            ) or []
            if not shapes:
                ctrl_transforms.add(transform)
            elif len(shapes) == 1 and cmds.nodeType(shapes[0]) == "locator":
                ctrl_transforms.add(transform)

        ctrl_set = set(selected_ctrls)
        ctrl_set.update(ctrl_transforms)
        transform_set = set(selected_transforms)
        transform_set.difference_update(ctrl_set)

        if not ctrl_set:
            cmds.error("No joints or other controls found in the selection!")
        if not transform_set:
            cmds.error("No shape transforms found in the selection!")

        if len(ctrl_set) == 1:
            ShapeCloner._shapes_to_ctrl(
                transform_set, ctrl_set, only_match=only_match
            )
        elif len(transform_set) == 1:
            ShapeCloner._shape_to_ctrls(
                transform_set, ctrl_set, only_match=only_match
            )
        else:
            ShapeCloner._shapes_to_ctrls(transform_set, ctrl_set)


def run():
    ShapeCloner.run()
